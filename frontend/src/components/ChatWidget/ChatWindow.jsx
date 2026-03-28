import { useEffect, useRef, useState, useCallback } from 'react'
import ChatMessage from './ChatMessage'

const QUICK_CHIPS = [
  '¿Cuánto cuesta el m²?',
  'Necesito medir mi jardín',
  'Quiero una cotización',
  'Ver mi cotización activa',
]

const WELCOME_MSG = '¡Hola! Soy el asistente de **Césped Sintético SpA** 🌿\n\nPuedo ayudarte a:\n• Calcular los m² que necesitas\n• Cotizar el producto ideal\n• Generar un link de pago\n\n¿Por dónde empezamos?'

function formatCLP(amount) {
  return new Intl.NumberFormat('es-CL', {
    style: 'currency',
    currency: 'CLP',
    minimumFractionDigits: 0,
  }).format(amount)
}

export default function ChatWindow({ messages, quote, isLoading, onSend, onClear, onClose }) {
  const [input, setInput] = useState('')
  const messagesEndRef = useRef(null)
  const inputRef = useRef(null)
  const hasMessages = messages.length > 0

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, isLoading])

  // Focus input on open
  useEffect(() => {
    setTimeout(() => inputRef.current?.focus(), 100)
  }, [])

  const handleSend = useCallback(() => {
    const text = input.trim()
    if (!text || isLoading) return
    onSend(text)
    setInput('')
    inputRef.current?.focus()
  }, [input, isLoading, onSend])

  const handleKeyDown = useCallback((e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }, [handleSend])

  const handleChip = useCallback((text) => {
    onSend(text)
  }, [onSend])

  return (
    <div className="cw-window" role="dialog" aria-label="Chat de cotizaciones">
      {/* Header */}
      <header className="cw-header">
        <div className="cw-header-avatar" aria-hidden="true">🌿</div>
        <div className="cw-header-info">
          <div className="cw-header-name">Asistente Trato Hecho</div>
          <div className="cw-header-status">
            <span className="cw-status-dot" />
            En línea · Césped Sintético SpA
          </div>
        </div>
        <div className="cw-header-actions">
          {hasMessages && (
            <button
              className="cw-header-btn"
              onClick={onClear}
              title="Limpiar conversación"
              aria-label="Limpiar conversación"
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M3 6h18M8 6V4h8v2M19 6l-1 14H6L5 6" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
            </button>
          )}
          <button
            className="cw-header-btn"
            onClick={onClose}
            title="Cerrar chat"
            aria-label="Cerrar chat"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
              <path d="M18 6L6 18M6 6l12 12" strokeLinecap="round" />
            </svg>
          </button>
        </div>
      </header>

      {/* Active quote banner */}
      {quote && (
        <div className="cw-quote-banner" role="status">
          <span className="cw-quote-banner-icon">📋</span>
          <div className="cw-quote-banner-text">
            <div className="cw-quote-banner-num">Cotización activa: {quote.numero}</div>
            <div className="cw-quote-banner-detail">
              {quote.m2} m² · {quote.tipo} · {formatCLP(quote.total)}
            </div>
          </div>
        </div>
      )}

      {/* Messages */}
      <div className="cw-messages" role="log" aria-live="polite" aria-label="Mensajes del chat">
        {!hasMessages ? (
          /* Welcome screen */
          <div className="cw-welcome">
            <div className="cw-welcome-emoji" aria-hidden="true">🌿</div>
            <div className="cw-welcome-title">¡Bienvenido/a!</div>
            <div className="cw-welcome-desc">
              Te ayudo a calcular el metraje, cotizar y pagar tu césped sintético en minutos.
            </div>
            <div className="cw-welcome-chips" role="group" aria-label="Sugerencias de consulta">
              {QUICK_CHIPS.map(chip => (
                <button
                  key={chip}
                  className="cw-chip"
                  onClick={() => handleChip(chip)}
                  disabled={isLoading}
                >
                  {chip}
                </button>
              ))}
            </div>
          </div>
        ) : (
          messages.map(msg => (
            <ChatMessage key={msg.id} message={msg} />
          ))
        )}

        {/* Typing indicator */}
        {isLoading && (
          <div className="cw-typing" role="status" aria-label="El asistente está escribiendo">
            <span /><span /><span />
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input area */}
      <div className="cw-input-area">
        <div className="cw-input-row">
          <textarea
            ref={inputRef}
            className="cw-input"
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Escribe tu consulta..."
            rows={1}
            disabled={isLoading}
            aria-label="Escribe un mensaje"
          />
          <button
            className="cw-send-btn"
            onClick={handleSend}
            disabled={!input.trim() || isLoading}
            aria-label="Enviar mensaje"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          </button>
        </div>
        <div className="cw-input-hint">
          Powered by Claude AI · Trato Hecho
        </div>
      </div>
    </div>
  )
}
