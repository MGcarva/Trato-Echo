import json, os

workflow = {
    "name": "Trato Hecho - Chat Agent",
    "id": "8726be75-0ef1-4125-9c85-f97008eef9bb",
    "active": False,
    "settings": {
        "executionOrder": "v1",
        "saveManualExecutions": True,
        "saveExecutionProgress": False,
        "errorWorkflow": ""
    },
    "meta": {"instanceId": "trato-hecho-instance"},
    "tags": [{"name": "trato-hecho"}, {"name": "chat-agent"}],
    "nodes": [],
    "connections": {}
}

# ── Credentials ──
redis_cred = {"redis": {"id": "dlDAEbv3seiyxAvV", "name": "Redis - Trato Hecho"}}
cors_headers = {"responseHeaders": {"entries": [
    {"name": "Access-Control-Allow-Origin", "value": "*"},
    {"name": "Content-Type", "value": "application/json"}
]}}

# ═══════════════════════════════════════════════════════════════
# SYSTEM PROMPT  (built as a plain Python string for readability)
# ═══════════════════════════════════════════════════════════════
CONSTRUIR_PROMPT_JS = r"""
const extract      = $('Extraer Input').first().json;
const redisQuote   = $('Obtener Cotización Redis').first().json;
const redisHistory = $input.first().json;
const { uuid, message } = extract;

// ── Historial ──
let history = [];
if (redisHistory && redisHistory.value) {
  try { history = JSON.parse(redisHistory.value); } catch(e) { history = []; }
}
history = history.slice(-30);

// ── Cotización existente ──
let quoteContext = '';
let existingQuote = null;
if (redisQuote && redisQuote.value) {
  try {
    existingQuote = JSON.parse(redisQuote.value);
    quoteContext = '\n\n=== COTIZACIÓN ACTIVA DEL CLIENTE ===\n'
      + 'Número: ' + existingQuote.numero + '\n'
      + 'Teléfono: ' + (existingQuote.telefono || 'no registrado') + '\n'
      + 'Nombre: ' + (existingQuote.nombre || 'no registrado') + '\n'
      + 'Producto: ' + existingQuote.tipo + '\n'
      + 'M²: ' + existingQuote.m2 + ' m²\n'
      + 'Instalación: ' + (existingQuote.instalacion ? 'Sí' : 'No') + '\n'
      + 'Total: $' + Number(existingQuote.total).toLocaleString('es-CL') + ' CLP\n'
      + 'Fecha: ' + existingQuote.fecha + '\n'
      + '\nEl cliente YA tiene cotización. Si quiere pagar, genera el link.\n'
      + 'Usa: [PAGAR: numero=' + existingQuote.numero + ', monto=' + existingQuote.total + ']';
  } catch(e) { existingQuote = null; }
}

const isFirstMessage = history.length === 0 && !existingQuote;
const hasHistory = history.length > 0;

let memoryRule = '';
if (isFirstMessage) {
  memoryRule = '- Es el PRIMER contacto. Saluda breve y pregunta el nombre: "¡Hola! Soy Queno de Césped Sintético SpA 🌿 ¿Cómo te llamas?" Espera que responda su nombre antes de seguir.';
} else if (hasHistory) {
  memoryRule = '- La conversación ya está en curso. PROHIBIDO saludar de nuevo. PROHIBIDO repetir preguntas ya respondidas. Continúa desde donde quedó.';
}
if (existingQuote) {
  memoryRule += '\n- El cliente ya tiene cotización guardada. Menciónala y pregunta si quiere pagar.';
}

const systemPrompt = `Eres Queno, asesor virtual de Césped Sintético SpA de Melipilla, Chile.

IDENTIDAD:
- Experto en césped sintético, relajado pero profesional
- Español chileno natural ("bacán", "dale", "perfecto", "listo")
- CONCISO: respuestas cortas, máximo 3-4 líneas
- Haces UNA pregunta a la vez

NOMBRE DEL CLIENTE:
- En el PRIMER mensaje SIEMPRE pregunta el nombre
- Una vez que lo sepas, úsalo naturalmente ("Dale Juan...", "Perfecto María")
- Si ya dijo su nombre en el historial, NO lo vuelvas a preguntar

TELÉFONO DEL CLIENTE:
- Después de saber el nombre, pregunta su número de teléfono de forma natural: "¿Me das tu número de celular para guardarte la cotización?"
- El teléfono es OBLIGATORIO antes de cotizar. Sin teléfono NO generes cotización.
- Si ya dio su teléfono en el historial, NO lo vuelvas a preguntar
- Formato esperado: +56 9 XXXX XXXX o 9 XXXX XXXX

COTIZACIÓN EXISTENTE:
- De forma natural pregunta si ya tiene una cotización realizada: "¿Ya habías cotizado antes con nosotros o es primera vez?"
- Si dice que sí, pregúntale su número de teléfono para buscarla
- Si ya tiene cotización en el sistema (ver abajo), menciónala directamente

MEMORIA — REGLA CRÍTICA:
${memoryRule}
- Si el cliente ya dio tipo de espacio → NO lo vuelvas a preguntar
- Si el cliente ya dio medidas → NO las vuelvas a pedir
- Si el cliente ya eligió producto → NO ofrezcas opciones de nuevo
- Si el cliente ya dio teléfono → NO lo vuelvas a pedir

PRODUCTOS (CLP/m²):
- Pasto Deportivo Pro 25mm: $12.000/m² (canchas)
- Pasto Ornamental Básico 20mm: $8.500/m² (jardines)
- Pasto Ornamental Premium 35mm: $15.000/m² (lujo)
- Instalación profesional: +$4.500/m²

CÁLCULO: m² = largo × ancho + 10% margen (redondear arriba)

COMPORTAMIENTO — MUESTRA PRECIOS SIEMPRE:
1. Cuando tengas medidas Y tipo de espacio → calcula m² con margen, recomienda producto Y muestra precio total INMEDIATAMENTE
2. Pregunta si quiere instalación ($4.500/m² extra)
3. Cuando tengas todo (m², producto, instalación, nombre, teléfono) → muestra resumen con TOTAL y pregunta si confirma
4. Si confirma → genera cotización con [COTIZAR: ...]
5. Si quiere pagar cotización existente → genera pago con [PAGAR: ...]

FLUJO DE COMPRA — DESPUÉS DE PAGAR:
- Cuando el cliente confirme que pagó o quiera comprar, pídele:
  1. Nombre completo (si no lo tienes ya)
  2. Dirección de entrega completa (calle, número, comuna, ciudad)
  3. Que envíe una foto/captura del comprobante de pago
- Cuando tengas nombre completo + dirección + confirmación de comprobante → genera la venta con [VENTA: ...]
- Informa que el plazo de entrega es de **5 días hábiles** desde la confirmación del pago
- Ejemplo: "Bacán [nombre], tu pedido queda registrado. Te entregamos en máximo 5 días hábiles en [dirección]. ¡Gracias por tu compra! 🌿"

Ejemplo de cálculo:
"Cancha 50×40m = 2.000m² + 10% = 2.200m² de Deportivo Pro a $12.000/m² = $26.400.000 CLP. ¿Te sumo instalación por $9.900.000?"

MARCADORES (SOLO con TODOS los datos confirmados):
[COTIZAR: m2=XX.XX, tipo=NOMBRE, instalacion=SI/NO, total=MONTO, telefono=TELEFONO, nombre=NOMBRE_CLIENTE]
[PAGAR: numero=COT-XXXX-XXX, monto=MONTO]
[VENTA: numero=COT-XXXX-XXX, nombreCompleto=NOMBRE, direccion=DIRECCION, telefono=TELEFONO, monto=MONTO]
${quoteContext}`;

const messages = [...history, { role: 'user', content: message }];
return [{ json: { uuid, systemPrompt, messages, existingQuote, history, message } }];
""".strip()

# ═══════════════════════════════════════════════════════════════
# PARSEAR RESPUESTA CLAUDE  (extracts markers + new VENTA marker)
# ═══════════════════════════════════════════════════════════════
PARSEAR_RESPUESTA_JS = r"""
const claudeResp = $input.first().json;
const prevData = $('Construir Prompt Claude').first().json;
const { uuid, existingQuote, history, message } = prevData;

let rawText = '';
if (claudeResp.content && claudeResp.content[0]) {
  rawText = claudeResp.content[0].text || '';
}

const cotizarRegex = /\[COTIZAR:\s*m2=([\d.]+),\s*tipo=([^,]+),\s*instalacion=(SI|NO),\s*total=(\d+),\s*telefono=([^,]+),\s*nombre=([^\]]+)\]/i;
const pagarRegex   = /\[PAGAR:\s*numero=([^,]+),\s*monto=(\d+)\]/i;
const ventaRegex   = /\[VENTA:\s*numero=([^,]+),\s*nombreCompleto=([^,]+),\s*direccion=(.+?),\s*telefono=([^,]+),\s*monto=(\d+)\]/i;

const cotizarMatch = rawText.match(cotizarRegex);
const pagarMatch   = rawText.match(pagarRegex);
const ventaMatch   = rawText.match(ventaRegex);

const cleanText = rawText
  .replace(cotizarRegex, '')
  .replace(pagarRegex, '')
  .replace(ventaRegex, '')
  .replace(/\n{3,}/g, '\n\n')
  .trim();

let action = 'NONE';
let actionData = null;

if (cotizarMatch) {
  action = 'COTIZAR';
  actionData = {
    m2: parseFloat(cotizarMatch[1]),
    tipo: cotizarMatch[2].trim(),
    instalacion: cotizarMatch[3].toUpperCase() === 'SI',
    total: parseInt(cotizarMatch[4], 10),
    telefono: cotizarMatch[5].trim(),
    nombre: cotizarMatch[6].trim()
  };
} else if (ventaMatch) {
  action = 'VENTA';
  actionData = {
    numero: ventaMatch[1].trim(),
    nombreCompleto: ventaMatch[2].trim(),
    direccion: ventaMatch[3].trim(),
    telefono: ventaMatch[4].trim(),
    monto: parseInt(ventaMatch[5], 10)
  };
} else if (pagarMatch) {
  action = 'PAGAR';
  actionData = {
    numero: pagarMatch[1].trim(),
    monto: parseInt(pagarMatch[2], 10)
  };
}

const updatedHistory = [
  ...history,
  { role: 'user', content: message },
  { role: 'assistant', content: cleanText }
].slice(-40);

return [{ json: { uuid, cleanText, action, actionData, existingQuote, updatedHistory } }];
""".strip()

# ═══════════════════════════════════════════════════════════════
# CREAR COTIZACIÓN  (now includes phone + name + MongoDB save)
# ═══════════════════════════════════════════════════════════════
CREAR_COTIZACION_JS = r"""
const parseData  = $('Parsear Respuesta Claude').first().json;
const counterVal = $input.first().json.value;
const { uuid, cleanText, actionData } = parseData;

const year = new Date().getFullYear();
const seq  = String(counterVal || 1).padStart(3, '0');
const numero = 'COT-' + year + '-' + seq;

const quote = {
  numero, uuid,
  m2: actionData.m2, tipo: actionData.tipo,
  instalacion: actionData.instalacion, total: actionData.total,
  telefono: actionData.telefono || '',
  nombre: actionData.nombre || '',
  fecha: new Date().toLocaleDateString('es-CL', { day: '2-digit', month: '2-digit', year: 'numeric' }),
  timestamp: Date.now(),
  estado: 'cotizado'
};

const msgInstalacion = quote.instalacion ? '\n🔧 Instalación incluida' : '';
const msgFinal = cleanText
  + '\n\n✅ ¡Cotización generada! Te la guardo por 10 días.\n\n'
  + '📋 Número: **' + quote.numero + '**\n'
  + '👤 Cliente: ' + quote.nombre + '\n'
  + '📱 Teléfono: ' + quote.telefono + '\n'
  + '📐 Metros cuadrados: ' + quote.m2 + ' m²\n'
  + '🌿 Producto: ' + quote.tipo + msgInstalacion
  + '\n💰 Total: $' + quote.total.toLocaleString('es-CL') + ' CLP\n\n'
  + '¿Quieres que te genere el link de pago de MercadoPago?';

return [{ json: { uuid, quote, message: msgFinal } }];
""".strip()

# ═══════════════════════════════════════════════════════════════
# CREAR VENTA  (new node for processing sales)
# ═══════════════════════════════════════════════════════════════
CREAR_VENTA_JS = r"""
const parseData = $('Parsear Respuesta Claude').first().json;
const { uuid, cleanText, actionData, existingQuote } = parseData;

const now = new Date();
const entrega = new Date(now.getTime() + 5 * 24 * 60 * 60 * 1000);
const fechaEntrega = entrega.toLocaleDateString('es-CL', { day: '2-digit', month: '2-digit', year: 'numeric' });

const venta = {
  numeroCotizacion: actionData.numero,
  uuid,
  nombreCompleto: actionData.nombreCompleto,
  direccion: actionData.direccion,
  telefono: actionData.telefono,
  monto: actionData.monto,
  producto: existingQuote ? existingQuote.tipo : '',
  m2: existingQuote ? existingQuote.m2 : 0,
  instalacion: existingQuote ? existingQuote.instalacion : false,
  fechaVenta: now.toLocaleDateString('es-CL', { day: '2-digit', month: '2-digit', year: 'numeric' }),
  fechaEntregaEstimada: fechaEntrega,
  estado: 'pagado',
  timestamp: Date.now()
};

const msgFinal = cleanText
  + '\n\n🎉 ¡Venta registrada!\n\n'
  + '📋 Cotización: **' + venta.numeroCotizacion + '**\n'
  + '👤 Cliente: ' + venta.nombreCompleto + '\n'
  + '📱 Teléfono: ' + venta.telefono + '\n'
  + '📍 Dirección: ' + venta.direccion + '\n'
  + '💰 Monto: $' + venta.monto.toLocaleString('es-CL') + ' CLP\n'
  + '📦 Entrega estimada: **' + fechaEntrega + '** (5 días hábiles)\n\n'
  + '¡Gracias por tu compra! 🌿';

return [{ json: { uuid, venta, message: msgFinal } }];
""".strip()

# ═══════════════════════════════════════════════════════════════
# NODES
# ═══════════════════════════════════════════════════════════════
workflow["nodes"] = [
    # ── Webhook ──
    {
        "parameters": {
            "httpMethod": "POST",
            "path": "chat",
            "responseMode": "responseNode",
            "options": {"allowedOrigins": "*"}
        },
        "id": "4bdf114a-0bca-437e-8eee-8a0f59af2e72",
        "name": "Webhook Chat",
        "type": "n8n-nodes-base.webhook",
        "typeVersion": 2,
        "position": [200, 400],
        "webhookId": "a1f2e3d4-b5c6-7890-abcd-ef1234567890"
    },

    # ── Extract Input ──
    {
        "parameters": {
            "jsCode": (
                "const raw = $input.first().json;\n"
                "const body = raw.body || raw;\n"
                "const uuid    = String(body.uuid    || '').trim();\n"
                "const message = String(body.message || '').trim();\n"
                "if (!uuid)    throw new Error('uuid es requerido');\n"
                "if (!message) throw new Error('message es requerido');\n"
                "return [{ json: { uuid, message } }];"
            )
        },
        "id": "0ca90f6a-f511-41a7-bf4c-ba7cd3306a0c",
        "name": "Extraer Input",
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": [420, 400]
    },

    # ── Redis GET quote ──
    {
        "parameters": {
            "operation": "get",
            "key": "=th:quote:{{ $json.uuid }}",
            "propertyName": "value"
        },
        "id": "0d137eda-65ee-429d-acf4-056b686ffa2e",
        "name": "Obtener Cotización Redis",
        "type": "n8n-nodes-base.redis",
        "typeVersion": 1,
        "position": [640, 400],
        "credentials": redis_cred
    },

    # ── Redis GET history ──
    {
        "parameters": {
            "operation": "get",
            "key": "=th:history:{{ $('Extraer Input').first().json.uuid }}",
            "propertyName": "value"
        },
        "id": "a1b2c3d4-e5f6-7890-abcd-111122223333",
        "name": "Obtener Historial Redis",
        "type": "n8n-nodes-base.redis",
        "typeVersion": 1,
        "position": [860, 400],
        "credentials": redis_cred
    },

    # ── Build Prompt ──
    {
        "parameters": {"jsCode": CONSTRUIR_PROMPT_JS},
        "id": "ec83745d-155b-410b-922c-487c976d4c48",
        "name": "Construir Prompt Claude",
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": [1080, 400]
    },

    # ── Call Claude API ──
    {
        "parameters": {
            "method": "POST",
            "url": "https://api.anthropic.com/v1/messages",
            "sendHeaders": True,
            "headerParameters": {
                "parameters": [
                    {"name": "x-api-key", "value": "={{ $env.ANTHROPIC_API_KEY }}"},
                    {"name": "anthropic-version", "value": "2023-06-01"},
                    {"name": "content-type", "value": "application/json"}
                ]
            },
            "sendBody": True,
            "specifyBody": "json",
            "jsonBody": "={{ JSON.stringify({ model: 'claude-sonnet-4-6', max_tokens: 1024, system: $json.systemPrompt, messages: $json.messages }) }}",
            "options": {"timeout": 30000}
        },
        "id": "67dd2c24-ed10-48ff-b330-d4b91ea2afad",
        "name": "Llamar Claude API",
        "type": "n8n-nodes-base.httpRequest",
        "typeVersion": 4,
        "position": [1300, 400]
    },

    # ── Parse Claude Response ──
    {
        "parameters": {"jsCode": PARSEAR_RESPUESTA_JS},
        "id": "dee445cd-a3fc-48a2-91a8-10e1c4c3b5c8",
        "name": "Parsear Respuesta Claude",
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": [1520, 400]
    },

    # ── Redis SET history ──
    {
        "parameters": {
            "operation": "set",
            "key": "=th:history:{{ $json.uuid }}",
            "value": "={{ JSON.stringify($json.updatedHistory) }}",
            "expire": True,
            "ttl": 864000
        },
        "id": "b1c2d3e4-f5a6-7890-bcde-222233334444",
        "name": "Guardar Historial Redis",
        "type": "n8n-nodes-base.redis",
        "typeVersion": 1,
        "position": [1740, 400],
        "credentials": redis_cred
    },

    # ── Switch Action ──
    {
        "parameters": {
            "rules": {
                "values": [
                    {
                        "conditions": {
                            "options": {"caseSensitive": False, "leftValue": "", "typeValidation": "strict"},
                            "conditions": [{"leftValue": "={{ $('Parsear Respuesta Claude').first().json.action }}", "rightValue": "COTIZAR", "operator": {"type": "string", "operation": "equals"}}],
                            "combinator": "and"
                        },
                        "outputKey": "COTIZAR"
                    },
                    {
                        "conditions": {
                            "options": {"caseSensitive": False, "leftValue": "", "typeValidation": "strict"},
                            "conditions": [{"leftValue": "={{ $('Parsear Respuesta Claude').first().json.action }}", "rightValue": "PAGAR", "operator": {"type": "string", "operation": "equals"}}],
                            "combinator": "and"
                        },
                        "outputKey": "PAGAR"
                    },
                    {
                        "conditions": {
                            "options": {"caseSensitive": False, "leftValue": "", "typeValidation": "strict"},
                            "conditions": [{"leftValue": "={{ $('Parsear Respuesta Claude').first().json.action }}", "rightValue": "VENTA", "operator": {"type": "string", "operation": "equals"}}],
                            "combinator": "and"
                        },
                        "outputKey": "VENTA"
                    }
                ]
            },
            "options": {"fallbackOutput": "extra"}
        },
        "id": "5175e91c-6d37-47e9-93b9-61b9cf3265fe",
        "name": "Switch Acción",
        "type": "n8n-nodes-base.switch",
        "typeVersion": 3,
        "position": [1960, 400]
    },

    # ── Redis INCR counter ──
    {
        "parameters": {"operation": "incr", "key": "th:counter"},
        "id": "f5dd1c36-1d67-4944-a4ec-c07cf8562ad4",
        "name": "Incrementar Contador",
        "type": "n8n-nodes-base.redis",
        "typeVersion": 1,
        "position": [2180, 100],
        "credentials": redis_cred
    },

    # ── Create Quote ──
    {
        "parameters": {"jsCode": CREAR_COTIZACION_JS},
        "id": "acb7b66d-ea24-44fd-a59c-218afef63d00",
        "name": "Crear Cotización",
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": [2400, 100]
    },

    # ── Redis SET quote ──
    {
        "parameters": {
            "operation": "set",
            "key": "=th:quote:{{ $json.uuid }}",
            "value": "={{ JSON.stringify($json.quote) }}",
            "expire": True,
            "ttl": 864000
        },
        "id": "2159c742-6997-4909-bb76-108536ce4e51",
        "name": "Guardar Cotización Redis",
        "type": "n8n-nodes-base.redis",
        "typeVersion": 1,
        "position": [2620, 100],
        "credentials": redis_cred
    },

    # ── MongoDB: Save Quote via HTTP to mongo-api ──
    {
        "parameters": {
            "method": "POST",
            "url": "http://mongo-api:3100/cotizaciones",
            "sendHeaders": True,
            "headerParameters": {"parameters": [{"name": "Content-Type", "value": "application/json"}]},
            "sendBody": True,
            "specifyBody": "json",
            "jsonBody": "={{ JSON.stringify($json.quote) }}",
            "options": {"timeout": 10000}
        },
        "id": "mongo-save-quote-001",
        "name": "Mongo Guardar Cotización",
        "type": "n8n-nodes-base.httpRequest",
        "typeVersion": 4,
        "position": [2840, 100]
    },

    # ── Respuesta Cotización ──
    {
        "parameters": {
            "jsCode": (
                "const quoteData = $('Crear Cotización').first().json;\n"
                "return [{ json: { message: quoteData.message, quote: quoteData.quote, paymentLink: null } }];"
            )
        },
        "id": "04f84a42-0447-4923-a331-6ed794cef9cf",
        "name": "Respuesta Cotización",
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": [3060, 100]
    },

    # ── MercadoPago ──
    {
        "parameters": {
            "method": "POST",
            "url": "https://api.mercadopago.com/checkout/preferences",
            "sendHeaders": True,
            "headerParameters": {
                "parameters": [
                    {"name": "Authorization", "value": "=Bearer {{ $env.MERCADOPAGO_ACCESS_TOKEN }}"},
                    {"name": "Content-Type", "value": "application/json"}
                ]
            },
            "sendBody": True,
            "specifyBody": "json",
            "jsonBody": "={{ JSON.stringify({ items: [{ id: $json.actionData.numero, title: 'Césped Sintético SpA - ' + $json.actionData.numero, description: $json.existingQuote ? ($json.existingQuote.m2 + ' m² de ' + $json.existingQuote.tipo) : 'Pasto Sintético', quantity: 1, currency_id: 'CLP', unit_price: $json.actionData.monto }], external_reference: $json.actionData.numero, back_urls: { success: $env.FRONTEND_URL + '?pago=ok', failure: $env.FRONTEND_URL + '?pago=error', pending: $env.FRONTEND_URL + '?pago=pendiente' }, auto_return: 'approved', statement_descriptor: 'CESPED SINTETICO SPA' }) }}",
            "options": {"timeout": 15000}
        },
        "id": "cb779899-409e-4dc9-9960-c7fef45d4f82",
        "name": "Llamar MercadoPago",
        "type": "n8n-nodes-base.httpRequest",
        "typeVersion": 4,
        "position": [2180, 350]
    },

    # ── Respuesta Pago ──
    {
        "parameters": {
            "jsCode": (
                "const mpResp = $input.first().json;\n"
                "const parseData = $('Parsear Respuesta Claude').first().json;\n"
                "const paymentLink = mpResp.init_point || mpResp.sandbox_init_point || null;\n"
                "const message = parseData.cleanText + (paymentLink\n"
                "  ? '\\n\\n💳 Aquí está tu link de pago para **' + parseData.actionData.numero + '**:\\n\\n' + paymentLink + '\\n\\nPaga seguro con MercadoPago.'\n"
                "  : '\\n\\nHubo un problema con el link de pago. Contáctanos directamente.');\n"
                "return [{ json: { message, quote: parseData.existingQuote || null, paymentLink } }];"
            )
        },
        "id": "15f1b067-297e-466f-b935-70b56a478db3",
        "name": "Respuesta Pago",
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": [2400, 350]
    },

    # ── Crear Venta (Code) ──
    {
        "parameters": {"jsCode": CREAR_VENTA_JS},
        "id": "venta-code-001",
        "name": "Crear Venta",
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": [2180, 600]
    },

    # ── Mongo Guardar Venta via HTTP ──
    {
        "parameters": {
            "method": "POST",
            "url": "http://mongo-api:3100/ventas",
            "sendHeaders": True,
            "headerParameters": {"parameters": [{"name": "Content-Type", "value": "application/json"}]},
            "sendBody": True,
            "specifyBody": "json",
            "jsonBody": "={{ JSON.stringify($json.venta) }}",
            "options": {"timeout": 10000}
        },
        "id": "mongo-save-venta-001",
        "name": "Mongo Guardar Venta",
        "type": "n8n-nodes-base.httpRequest",
        "typeVersion": 4,
        "position": [2400, 600]
    },

    # ── Respuesta Venta ──
    {
        "parameters": {
            "jsCode": (
                "const ventaData = $('Crear Venta').first().json;\n"
                "return [{ json: { message: ventaData.message, venta: ventaData.venta, paymentLink: null } }];"
            )
        },
        "id": "resp-venta-001",
        "name": "Respuesta Venta",
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": [2620, 600]
    },

    # ── Respuesta Simple ──
    {
        "parameters": {
            "jsCode": (
                "const parseData = $('Parsear Respuesta Claude').first().json;\n"
                "return [{ json: { message: parseData.cleanText, quote: parseData.existingQuote || null, paymentLink: null } }];"
            )
        },
        "id": "f1894916-3b80-410c-849f-ece1a5eb40c2",
        "name": "Respuesta Simple",
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": [2180, 850]
    },

    # ── Respond Webhook nodes ──
    {
        "parameters": {"respondWith": "json", "responseBody": "={{ JSON.stringify($json) }}", "options": cors_headers},
        "id": "64d1a889-080d-45cd-b7bf-af6094bc6c9a",
        "name": "Responder Webhook (Cotizar)",
        "type": "n8n-nodes-base.respondToWebhook",
        "typeVersion": 1,
        "position": [3280, 100]
    },
    {
        "parameters": {"respondWith": "json", "responseBody": "={{ JSON.stringify($json) }}", "options": cors_headers},
        "id": "5d22ed31-a01b-4829-8e53-f85606b82966",
        "name": "Responder Webhook (Pagar)",
        "type": "n8n-nodes-base.respondToWebhook",
        "typeVersion": 1,
        "position": [2620, 350]
    },
    {
        "parameters": {"respondWith": "json", "responseBody": "={{ JSON.stringify($json) }}", "options": cors_headers},
        "id": "resp-webhook-venta-001",
        "name": "Responder Webhook (Venta)",
        "type": "n8n-nodes-base.respondToWebhook",
        "typeVersion": 1,
        "position": [2840, 600]
    },
    {
        "parameters": {"respondWith": "json", "responseBody": "={{ JSON.stringify($json) }}", "options": cors_headers},
        "id": "8f00e480-ead8-4b63-a3c9-5c11ec44b82f",
        "name": "Responder Webhook (Simple)",
        "type": "n8n-nodes-base.respondToWebhook",
        "typeVersion": 1,
        "position": [2400, 850]
    }
]

# ═══════════════════════════════════════════════════════════════
# CONNECTIONS
# ═══════════════════════════════════════════════════════════════
workflow["connections"] = {
    "Webhook Chat":              {"main": [[{"node": "Extraer Input", "type": "main", "index": 0}]]},
    "Extraer Input":             {"main": [[{"node": "Obtener Cotización Redis", "type": "main", "index": 0}]]},
    "Obtener Cotización Redis":  {"main": [[{"node": "Obtener Historial Redis", "type": "main", "index": 0}]]},
    "Obtener Historial Redis":   {"main": [[{"node": "Construir Prompt Claude", "type": "main", "index": 0}]]},
    "Construir Prompt Claude":   {"main": [[{"node": "Llamar Claude API", "type": "main", "index": 0}]]},
    "Llamar Claude API":         {"main": [[{"node": "Parsear Respuesta Claude", "type": "main", "index": 0}]]},
    "Parsear Respuesta Claude":  {"main": [[{"node": "Guardar Historial Redis", "type": "main", "index": 0}]]},
    "Guardar Historial Redis":   {"main": [[{"node": "Switch Acción", "type": "main", "index": 0}]]},
    # Switch: output 0 = COTIZAR, 1 = PAGAR, 2 = VENTA, 3 = fallback (Simple)
    "Switch Acción": {"main": [
        [{"node": "Incrementar Contador", "type": "main", "index": 0}],
        [{"node": "Llamar MercadoPago", "type": "main", "index": 0}],
        [{"node": "Crear Venta", "type": "main", "index": 0}],
        [{"node": "Respuesta Simple", "type": "main", "index": 0}]
    ]},
    # COTIZAR path
    "Incrementar Contador":      {"main": [[{"node": "Crear Cotización", "type": "main", "index": 0}]]},
    "Crear Cotización":          {"main": [[{"node": "Guardar Cotización Redis", "type": "main", "index": 0}]]},
    "Guardar Cotización Redis":  {"main": [[{"node": "Mongo Guardar Cotización", "type": "main", "index": 0}]]},
    "Mongo Guardar Cotización":  {"main": [[{"node": "Respuesta Cotización", "type": "main", "index": 0}]]},
    "Respuesta Cotización":      {"main": [[{"node": "Responder Webhook (Cotizar)", "type": "main", "index": 0}]]},
    # PAGAR path
    "Llamar MercadoPago":        {"main": [[{"node": "Respuesta Pago", "type": "main", "index": 0}]]},
    "Respuesta Pago":            {"main": [[{"node": "Responder Webhook (Pagar)", "type": "main", "index": 0}]]},
    # VENTA path
    "Crear Venta":               {"main": [[{"node": "Mongo Guardar Venta", "type": "main", "index": 0}]]},
    "Mongo Guardar Venta":       {"main": [[{"node": "Respuesta Venta", "type": "main", "index": 0}]]},
    "Respuesta Venta":           {"main": [[{"node": "Responder Webhook (Venta)", "type": "main", "index": 0}]]},
    # Simple path
    "Respuesta Simple":          {"main": [[{"node": "Responder Webhook (Simple)", "type": "main", "index": 0}]]}
}

# ═══════════════════════════════════════════════════════════════
# OUTPUT
# ═══════════════════════════════════════════════════════════════
out = os.path.join(os.path.dirname(__file__), "trato-hecho-workflow.json")
with open(out, "w", encoding="utf-8") as f:
    json.dump(workflow, f, indent=2, ensure_ascii=False)

print("✅ Workflow JSON generado:", out)
