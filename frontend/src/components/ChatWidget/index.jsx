import { useState, useCallback } from 'react'
import { useChat } from './useChat'
import ChatWindow from './ChatWindow'
import './ChatWidget.css'

export default function ChatWidget() {
  const [isOpen, setIsOpen] = useState(false)
  const { messages, quote, isLoading, sendMessage, clearChat } = useChat()

  const handleOpen = useCallback(() => setIsOpen(true), [])
  const handleClose = useCallback(() => setIsOpen(false), [])

  const handleClear = useCallback(() => {
    clearChat()
  }, [clearChat])

  // Show red dot if we have an active quote and chat is closed
  const showDot = !isOpen && quote

  return (
    <>
      {/* Chat window */}
      {isOpen && (
        <ChatWindow
          messages={messages}
          quote={quote}
          isLoading={isLoading}
          onSend={sendMessage}
          onClear={handleClear}
          onClose={handleClose}
        />
      )}

      {/* Floating action button */}
      <button
        className="cw-fab"
        onClick={isOpen ? handleClose : handleOpen}
        aria-label={isOpen ? 'Cerrar chat' : 'Abrir chat de cotizaciones'}
        aria-expanded={isOpen}
      >
        {isOpen ? (
          /* X icon when open */
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
            <path d="M18 6L6 18M6 6l12 12" strokeLinecap="round" />
          </svg>
        ) : (
          /* Chat icon when closed */
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
        )}

        {/* Notification dot */}
        {showDot && <span className="cw-fab-dot" aria-hidden="true" />}
      </button>
    </>
  )
}
