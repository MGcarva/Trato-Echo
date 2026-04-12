const http = require('http');
const { MongoClient } = require('mongodb');

const MONGO_URL = process.env.MONGO_URL || 'mongodb://mongo:27017';
const DB_NAME = 'tratohecho';
const PORT = 3100;

let db;

async function connectMongo() {
  const client = new MongoClient(MONGO_URL);
  await client.connect();
  db = client.db(DB_NAME);
  console.log('✅ Conectado a MongoDB:', DB_NAME);
}

function parseBody(req) {
  return new Promise((resolve, reject) => {
    let data = '';
    req.on('data', chunk => { data += chunk; });
    req.on('end', () => {
      try { resolve(JSON.parse(data)); }
      catch (e) { reject(new Error('JSON inválido')); }
    });
    req.on('error', reject);
  });
}

const server = http.createServer(async (req, res) => {
  res.setHeader('Content-Type', 'application/json');

  try {
    // POST /cotizaciones — guardar cotización
    if (req.method === 'POST' && req.url === '/cotizaciones') {
      const doc = await parseBody(req);
      doc.createdAt = new Date();
      const result = await db.collection('cotizaciones').insertOne(doc);
      res.writeHead(201);
      res.end(JSON.stringify({ ok: true, id: result.insertedId }));
      return;
    }

    // POST /ventas — guardar venta
    if (req.method === 'POST' && req.url === '/ventas') {
      const doc = await parseBody(req);
      doc.createdAt = new Date();
      const result = await db.collection('ventas').insertOne(doc);
      // También actualizar estado de la cotización a "vendido"
      if (doc.numeroCotizacion) {
        await db.collection('cotizaciones').updateOne(
          { numero: doc.numeroCotizacion },
          { $set: { estado: 'vendido', fechaVenta: new Date() } }
        );
      }
      res.writeHead(201);
      res.end(JSON.stringify({ ok: true, id: result.insertedId }));
      return;
    }

    // GET /cotizaciones?telefono=XXX — buscar cotización por teléfono
    if (req.method === 'GET' && req.url.startsWith('/cotizaciones')) {
      const url = new URL(req.url, `http://localhost:${PORT}`);
      const telefono = url.searchParams.get('telefono');
      if (telefono) {
        const docs = await db.collection('cotizaciones')
          .find({ telefono: { $regex: telefono.replace(/\D/g, '').slice(-8) } })
          .sort({ timestamp: -1 })
          .limit(5)
          .toArray();
        res.writeHead(200);
        res.end(JSON.stringify(docs));
        return;
      }
      // List all recent
      const docs = await db.collection('cotizaciones')
        .find({}).sort({ timestamp: -1 }).limit(20).toArray();
      res.writeHead(200);
      res.end(JSON.stringify(docs));
      return;
    }

    // GET /ventas — listar ventas
    if (req.method === 'GET' && req.url.startsWith('/ventas')) {
      const docs = await db.collection('ventas')
        .find({}).sort({ timestamp: -1 }).limit(20).toArray();
      res.writeHead(200);
      res.end(JSON.stringify(docs));
      return;
    }

    // Health check
    if (req.url === '/health') {
      res.writeHead(200);
      res.end(JSON.stringify({ status: 'ok' }));
      return;
    }

    res.writeHead(404);
    res.end(JSON.stringify({ error: 'Not found' }));
  } catch (err) {
    console.error('Error:', err.message);
    res.writeHead(500);
    res.end(JSON.stringify({ error: err.message }));
  }
});

connectMongo().then(() => {
  server.listen(PORT, '0.0.0.0', () => {
    console.log(`🚀 Mongo API escuchando en puerto ${PORT}`);
  });
}).catch(err => {
  console.error('❌ Error conectando a MongoDB:', err.message);
  process.exit(1);
});
