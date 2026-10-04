import { useEffect, useRef, useState, type FormEvent } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { fetchChatHistory, formatPrice, sendChatMessage } from '../api'
import { useAuth } from '../auth'
import { useChatResults } from '../chatResults'
import Markdown from './Markdown'
import HandsomeDan from './HandsomeDan'
import type { ChatMessage } from '../types'

const GREETING: ChatMessage = {
  role: 'assistant',
  content:
    "Woof. I'm Handsome Dan — I keep an eye on the stockroom here at Campus Customs. " +
    'Ask me what something costs, what it looks like, or whether your size is still on ' +
    'the shelf. I will tell you straight.',
}

export default function ChatPanel() {
  const { user } = useAuth()
  const { show } = useChatResults()
  const navigate = useNavigate()
  const location = useLocation()
  const [open, setOpen] = useState(false)
  const [messages, setMessages] = useState<ChatMessage[]>([GREETING])
  const [draft, setDraft] = useState('')
  const [waiting, setWaiting] = useState(false)
  const logRef = useRef<HTMLDivElement>(null)

  // A signed-in shopper picks their conversation back up; signing out clears it from view.
  useEffect(() => {
    if (!user) {
      setMessages([GREETING])
      return
    }
    let cancelled = false
    fetchChatHistory().then((saved) => {
      if (!cancelled) setMessages(saved.length ? [GREETING, ...saved] : [GREETING])
    })
    return () => { cancelled = true }
  }, [user])

  useEffect(() => {
    logRef.current?.scrollTo({ top: logRef.current.scrollHeight, behavior: 'smooth' })
  }, [messages, waiting, open])

  async function onSubmit(e: FormEvent) {
    e.preventDefault()
    const text = draft.trim()
    if (!text || waiting) return

    const history = messages.filter((m) => m !== GREETING)
    setMessages((m) => [...m, { role: 'user', content: text }])
    setDraft('')
    setWaiting(true)
    try {
      // Report where the shopper is standing. A /products/:id route means "this" has a
      // referent; the server checks the id against the catalogue before trusting it.
      const match = location.pathname.match(/^\/products\/(.+)$/)
      const reply = await sendChatMessage(text, history, {
        path: location.pathname,
        product_id: match ? decodeURIComponent(match[1]) : null,
      })
      setMessages((m) => [...m, reply])

      // The neat part: whatever the agent matched becomes the product grid behind the
      // panel. The chat stays open so the conversation can carry on.
      if (reply.products?.length) {
        show(text, reply.products)
        navigate('/products')
      }
    } catch (err) {
      setMessages((m) => [
        ...m,
        {
          role: 'assistant',
          content: err instanceof Error ? err.message : 'Something went wrong. Try again?',
        },
      ])
    } finally {
      setWaiting(false)
    }
  }

  if (!open) {
    return (
      <button className="chat-fab" onClick={() => setOpen(true)}>
        <HandsomeDan size={34} />
        <span className="chat-fab-text">
          <b>Ask Handsome Dan</b>
          <small>Prices &amp; sizes, straight up</small>
        </span>
      </button>
    )
  }

  return (
    <aside className="chat-panel" aria-label="Shop assistant">
      <div className="chat-head">
        <HandsomeDan size={44} talking={waiting} />
        <div>
          <strong>Handsome Dan</strong>
          <small>
            {user
              ? `Keeping this chat for ${user.first_name ?? user.name}`
              : 'Campus Customs, 57 Broadway'}
          </small>
        </div>
        <button className="chat-close" onClick={() => setOpen(false)} aria-label="Close chat">
          ×
        </button>
      </div>

      <div className="chat-log" ref={logRef}>
        {messages.map((m, i) => (
          <div key={i} className={`turn ${m.role}`}>
            {m.role === 'assistant' && <HandsomeDan size={30} />}
            <div className="turn-body">
            <div className={`bubble ${m.role}`}>
              {m.role === 'assistant' ? <Markdown text={m.content} /> : m.content}
            </div>
            {!!m.products?.length && (
              <div className="chat-cards">
                {m.products.map((p) => (
                  <Link
                    key={p.product_id}
                    to={`/products/${p.product_id}`}
                    className="chat-card"
                    onClick={() => setOpen(false)}
                  >
                    <img src={p.image_url} alt={p.name} loading="lazy" />
                    <div className="chat-card-body">
                      <span className="chat-card-name">{p.name}</span>
                      <span className="chat-card-price">{formatPrice(p.price)}</span>
                    </div>
                  </Link>
                ))}
              </div>
            )}
            </div>
          </div>
        ))}
        {waiting && (
          <div className="turn assistant">
            <HandsomeDan size={30} talking />
            <div className="turn-body">
              <div className="bubble assistant typing">
                <span className="paws"><i /><i /><i /></span>
              </div>
            </div>
          </div>
        )}
      </div>

      <form className="chat-form" onSubmit={onSubmit}>
        <input
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          placeholder="Ask Dan about any item…"
          aria-label="Message"
        />
        <button type="submit" disabled={!draft.trim() || waiting}>Send</button>
      </form>
    </aside>
  )
}
