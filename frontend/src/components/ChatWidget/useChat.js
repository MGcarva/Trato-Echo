import { useState, useEffect, useCallback, useRef } from 'react'

const STORAGE = {
  UUID:     'th_uuid',
  MESSAGES: 'th_messages',
  QUOTE:    'th_quote',
}

const N8N_URL = import.meta.env.VITE_N8N_WEBHOOK_URL || 'http://localhost:5678/webhook/chat'

function getOrCreateUUID() {
  let id = localStorage.getItem(STORAGE.UUID)
  if (!id) {
    id = crypto.randomUUID()
    localStorage.setItem(STORAGE.UUID, id)
  }
  return id
}

function loadFromStorage(key, fallback) {
  try {
    const raw = localStorage.getItem(key)
    return raw ? JSON.parse(raw) : fallback
  } catch {
    return fallback
  }
}

export function useChat() {
  const [uuid] = useState(getOrCreateUUID)
  const [messages, setMessages] = useState(() => loadFromStorage(STORAGE.MESSAGES, []))
  const [quote, setQuote] = useState(() => loadFromStorage(STORAGE.QUOTE, null))
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)
  const abortRef = useRef(null)

  // Persist messages to localStorage whenever they change
  useEffect(() => {
    // Keep only last 40 messages to avoid bloating localStorage
    const toSave = messages.slice(-40)
    localStorage.setItem(STORAGE.MESSAGES, JSON.stringify(toSave))
  }, [messages])

  // Persist quote
  useEffect(() => {
    if (quote) {
      localStorage.setItem(STORAGE.QUOTE, JSON.stringify(quote))
    }
  }, [quote])

  const sendMessage = useCallback(async (text) => {
    if (!text.trim() || isLoading) return

    setError(null)

    // Add user message immediately
    const userMsg = { id: crypto.randomUUID(), role: 'user', content: text }
    const withUser = [...messages, userMsg]
    setMessages(withUser)
    setIsLoading(true)

    // Build history for context (max last 20 exchanges)
    const history = withUser
      .slice(-20)
      .slice(0, -1) // exclude last user message since we pass it separately
      .map(m => ({ role: m.role, content: m.content }))

    abortRef.current = new AbortController()

    try {
      const res = await fetch(N8N_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ uuid, message: text, history }),
        signal: abortRef.current.signal,
      })

      if (!res.ok) throw new Error(`Error ${res.status}: ${res.statusText}`)

      const data = await res.json()

      const assistantMsg = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: data.message || 'Sin respuesta del servidor.',
        quote: data.quote || null,
        paymentLink: data.paymentLink || null,
      }

      setMessages(prev => [...prev, assistantMsg])

      if (data.quote) {
        setQuote(data.quote)
      }
    } catch (err) {
      if (err.name === 'AbortError') return

      setError('No pude conectarme al servidor. Verifica tu conexión e intenta nuevamente.')
      const errMsg = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: 'Lo siento, tuve un problema técnico. Por favor intenta nuevamente.',
        isError: true,
      }
      setMessages(prev => [...prev, errMsg])
    } finally {
      setIsLoading(false)
    }
  }, [messages, uuid, isLoading])

  const clearChat = useCallback(() => {
    abortRef.current?.abort()
    setMessages([])
    setQuote(null)
    setError(null)
    setIsLoading(false)
    localStorage.removeItem(STORAGE.MESSAGES)
    localStorage.removeItem(STORAGE.QUOTE)
    localStorage.removeItem(STORAGE.UUID)
    // New UUID for next session
    const newId = crypto.randomUUID()
    localStorage.setItem(STORAGE.UUID, newId)
  }, [])

  return { uuid, messages, quote, isLoading, error, sendMessage, clearChat }
}
