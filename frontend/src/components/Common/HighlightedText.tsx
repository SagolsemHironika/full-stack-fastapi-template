import { useMemo } from "react"

function escapeHtml(value: string) {
  return value
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;")
}

export function HighlightedText({
  text,
  query,
  className,
}: {
  text: string
  query: string
  className?: string
}) {
  const html = useMemo(() => {
    if (!query) return ""
    const escapedQuery = escapeHtml(query)
    const regex = new RegExp(`(${escapedQuery})`, "gi")
    return text.replace(
      regex,
      '<mark class="bg-yellow-200 dark:bg-yellow-800 rounded-sm">$1</mark>',
    )
  }, [text, query])

  if (!query) {
    return <span className={className}>{text}</span>
  }

  return (
    // biome-ignore lint/security/noDangerouslySetInnerHtml: search query is HTML-escaped before highlighting
    <span className={className} dangerouslySetInnerHTML={{ __html: html }} />
  )
}
