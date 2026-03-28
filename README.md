# 🌿 Trato Hecho — Chat Agent de Cotizaciones

Sistema de cotizaciones con agente IA para **Césped Sintético SpA** (Melipilla, Chile).
El cliente interactúa con un widget flotante en el sitio web, el agente calcula metraje,
genera cotizaciones con número único y crea links de pago vía MercadoPago. Todo el flujo
corre a través de **n8n**.

---

## Arquitectura

```
[React Widget]  ──POST──▶  [n8n Webhook]
                               │
                    ┌──────────┼──────────────┐
                    ▼          ▼              ▼
               [Redis]    [Claude API]  [MercadoPago]
             (memoria        (IA)        (link pago)
              10 días)
```

| Capa | Tecnología |
|------|-----------|
| Frontend | React 18 + Vite |
| Widget | CSS puro, sin dependencias extra |
| Orquestación | n8n (self-hosted via Docker) |
| IA | Claude Sonnet (Anthropic API) |
| Pagos | MercadoPago Checkout Pro |
| Memoria | Redis 7 (TTL 10 días) |

---

## Estructura del proyecto

```
trato-hecho/
├── frontend/                          # React app + widget
│   ├── src/
│   │   ├── components/
│   │   │   ├── ChatWidget/
│   │   │   │   ├── index.jsx          # Widget flotante (FAB)
│   │   │   │   ├── ChatWindow.jsx     # Ventana de chat
│   │   │   │   ├── ChatMessage.jsx    # Burbuja de mensaje + QuoteCard
│   │   │   │   ├── useChat.js         # Hook: lógica + localStorage
│   │   │   │   └── ChatWidget.css     # Estilos del widget
│   │   │   └── LandingPage/
│   │   │       └── index.jsx          # Página demo del negocio
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── index.css
│   ├── .env.example
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
│
├── n8n/
│   ├── docker-compose.yml             # n8n + Redis en Docker
│   └── workflows/
│       └── trato-hecho.json           # Workflow importable
│
├── .env.example                       # Variables de entorno raíz
└── README.md
```

---

## Instalación paso a paso

### 1. Clonar y configurar variables de entorno

```bash
cp .env.example .env
cp frontend/.env.example frontend/.env
# Editar ambos archivos con tus claves reales
```

### 2. Levantar n8n + Redis con Docker

```bash
cd n8n
docker compose --env-file ../.env up -d
```

Acceder a n8n en **http://localhost:5678** con las credenciales del `.env`.

### 3. Configurar credencial Redis en n8n

1. **Settings → Credentials → New Credential → Redis**
2. Host: `redis` · Port: `6379` · Sin password
3. Guardar como: `Redis - Trato Hecho`

### 4. Importar el workflow

1. **Workflows → Import from file** → seleccionar `n8n/workflows/trato-hecho.json`
2. En los 3 nodos Redis, cambiar credencial a `Redis - Trato Hecho`
3. Activar el workflow con el toggle **Active**

### 5. Correr el frontend

```bash
cd frontend
npm install
npm run dev
# → http://localhost:3000
```

---

## Variables de entorno

| Variable | Descripción |
|----------|-------------|
| `ANTHROPIC_API_KEY` | API key Claude — [console.anthropic.com](https://console.anthropic.com/) |
| `MERCADOPAGO_ACCESS_TOKEN` | Token MP — [mercadopago.cl/developers](https://www.mercadopago.cl/developers/panel) |
| `N8N_USER` / `N8N_PASSWORD` | Credenciales admin de n8n |
| `WEBHOOK_URL` | URL pública de n8n |
| `FRONTEND_URL` | URL del frontend (para redirección post-pago) |
| `VITE_N8N_WEBHOOK_URL` | URL del webhook de chat (usado por React) |

---

## Flujo del agente (n8n)

```
POST /webhook/chat  { uuid, message, history[] }
     │
     ▼
Redis GET th:quote:{uuid}   ← recupera cotización activa si el cliente volvió
     │
     ▼
Claude Sonnet API  ← prompt con catálogo, instrucciones y contexto de cotización
     │
     ▼
Parsear respuesta
     │
     ├── [COTIZAR: m2=X, tipo=Y, instalacion=Z, total=N]
     │        │
     │        ▼
     │   Redis INCR th:counter
     │   Crear COT-2026-XXX
     │   Redis SET th:quote:{uuid}  TTL=864000s (10 días)
     │   ← { message, quote }
     │
     ├── [PAGAR: numero=COT-X, monto=N]
     │        │
     │        ▼
     │   MercadoPago API → preference
     │   ← { message, paymentLink: init_point }
     │
     └── (respuesta normal)
              └── ← { message }
```

---

## Memoria de 10 días

- UUID del cliente → `localStorage` del navegador
- Cotización → Redis con TTL 864.000s
- Si el cliente vuelve: el widget envía el UUID guardado, n8n recupera la cotización y Claude retoma desde donde quedó

---

## MercadoPago: Pruebas vs Producción

| Modo | Token | Descripción |
|------|-------|-------------|
| Prueba | `TEST-xxxx` | Pagos simulados sin dinero real |
| Producción | `APP_USR-xxxx` | Cobros reales |

Para testing usa las [tarjetas de prueba de MercadoPago](https://www.mercadopago.cl/developers/es/docs/checkout-pro/test-integration/test-cards).

---

## Despliegue en producción

```bash
# n8n + Redis en VPS
cd n8n
# Editar .env con WEBHOOK_URL=https://n8n.tudominio.cl/
docker compose --env-file ../.env up -d

# Frontend → Vercel / Netlify
cd frontend && npm run build
# Variable de entorno en plataforma: VITE_N8N_WEBHOOK_URL=https://n8n.tudominio.cl/webhook/chat
```

---

*Trato Hecho · DuocUC 2026 · Césped Sintético SpA · Melipilla, Chile*
