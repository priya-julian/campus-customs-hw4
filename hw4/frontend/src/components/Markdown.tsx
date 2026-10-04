import type { ReactNode } from 'react'

/**
 * Just enough Markdown for the agent's replies: **bold** and "- " bullet lists.
 *
 * Deliberately renders React nodes rather than setting innerHTML, so model output can
 * never introduce markup into the page.
 */
function inline(text: string, keyPrefix: string): ReactNode[] {
  return text.split(/(\*\*[^*]+\*\*)/g).filter(Boolean).map((chunk, i) =>
    chunk.startsWith('**') && chunk.endsWith('**') ? (
      <strong key={`${keyPrefix}-${i}`}>{chunk.slice(2, -2)}</strong>
    ) : (
      <span key={`${keyPrefix}-${i}`}>{chunk}</span>
    ),
  )
}

export default function Markdown({ text }: { text: string }) {
  const blocks: ReactNode[] = []
  let bullets: string[] = []

  const flushBullets = () => {
    if (!bullets.length) return
    blocks.push(
      <ul key={`ul-${blocks.length}`} className="chat-list">
        {bullets.map((item, i) => <li key={i}>{inline(item, `li-${blocks.length}-${i}`)}</li>)}
      </ul>,
    )
    bullets = []
  }

  for (const line of text.split('\n')) {
    const bullet = line.match(/^\s*[-*]\s+(.*)$/)
    if (bullet) {
      bullets.push(bullet[1])
      continue
    }
    flushBullets()
    if (line.trim()) {
      blocks.push(<p key={`p-${blocks.length}`}>{inline(line, `p-${blocks.length}`)}</p>)
    }
  }
  flushBullets()

  return <>{blocks}</>
}
