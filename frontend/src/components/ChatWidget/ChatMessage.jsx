function formatTime(id) {
  // id is crypto.randomUUID() — use current time as fallback
  return new Date().toLocaleTimeString('es-CL', { hour: '2-digit', minute: '2-digit' })
}

function formatCLP(amount) {
  return new Intl.NumberFormat('es-CL', {
    style: 'currency',
    currency: 'CLP',
    minimumFractionDigits: 0,
  }).format(amount)
}

function QuoteCard({ quote, paymentLink }) {
  return (
    <div className="cw-quote-card">
      <div className="cw-quote-card-header">
        <span className="cw-quote-card-icon">📋</span>
        <div>
          <div className="cw-quote-card-title">Cotización generada</div>
          <div className="cw-quote-card-num">{quote.numero}</div>
        </div>
      </div>

      <div className="cw-quote-card-row">
        <span className="cw-quote-card-row-label">Producto</span>
        <span>{quote.tipo}</span>
      </div>
      <div className="cw-quote-card-row">
        <span className="cw-quote-card-row-label">Metros²</span>
        <span>{quote.m2} m²</span>
      </div>
      {quote.instalacion && (
        <div className="cw-quote-card-row">
          <span className="cw-quote-card-row-label">Instalación</span>
          <span>Incluida</span>
        </div>
      )}

      <div className="cw-quote-card-total">
        <span>Total</span>
        <span className="cw-quote-card-total-amount">{formatCLP(quote.total)}</span>
      </div>

      <div className="cw-quote-card-expiry">
        Válido por 10 días · {quote.fecha}
      </div>

      {paymentLink && (
        <a
          className="cw-pay-btn"
          href={paymentLink}
          target="_blank"
          rel="noopener noreferrer"
        >
          💳 Pagar con MercadoPago
        </a>
      )}
    </div>
  )
}

export default function ChatMessage({ message }) {
  const isUser = message.role === 'user'
  const isError = message.isError

  return (
    <div className={`cw-msg cw-msg--${message.role}${isError ? ' cw-msg--error' : ''}`}>
      <div className="cw-msg-bubble">
        {message.content}
      </div>

      {/* Render quote card if this message includes one */}
      {message.quote && (
        <QuoteCard quote={message.quote} paymentLink={message.paymentLink} />
      )}

      {/* Payment link without quote (standalone) */}
      {!message.quote && message.paymentLink && (
        <a
          className="cw-pay-btn"
          href={message.paymentLink}
          target="_blank"
          rel="noopener noreferrer"
          style={{ marginTop: '8px', display: 'block', maxWidth: '260px' }}
        >
          💳 Pagar con MercadoPago
        </a>
      )}

      <span className="cw-msg-time">
        {isUser ? '✓' : '🌿'} {formatTime(message.id)}
      </span>
    </div>
  )
}
