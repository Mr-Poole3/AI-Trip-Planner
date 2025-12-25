import { marked, Renderer } from 'marked'
import DOMPurify from 'dompurify'
import hljs from 'highlight.js'
import 'highlight.js/styles/github.css'
import type { HotelData } from '@/types/chat'

// Configure Marked Renderer
const renderer = new Renderer()
renderer.code = (code: string, infostring?: string) => {
  const lang = (infostring || '').trim()
  let highlighted = ''
  try {
    if (lang && hljs.getLanguage(lang)) {
      highlighted = hljs.highlight(code, { language: lang }).value
    } else {
      highlighted = hljs.highlightAuto(code).value
    }
  } catch {
    highlighted = code
  }
  const classAttr = lang ? ` class="language-${lang}"` : ''
  return `<pre><code${classAttr}>${highlighted}</code></pre>`
}

marked.setOptions({ gfm: true, breaks: true, renderer })

export const renderMarkdown = (text: string | undefined) => {
  const parsed = marked.parse(text || '')
  if (typeof parsed === 'string') {
    return DOMPurify.sanitize(parsed)
  }
  return DOMPurify.sanitize(text || '')
}

export type TextSegment = { type: 'text', content: string }
export type HotelSegment = { type: 'hotel', hotel: HotelData }
export type Segment = TextSegment | HotelSegment

export const isHotelSegment = (segment: Segment): segment is HotelSegment => {
  return segment.type === 'hotel'
}

export const parseTextWithHotelCards = (text: string | undefined, hotelsData: HotelData[]): Segment[] => {
  if (!text) return [{ type: 'text', content: '' }]

  const segments: Segment[] = []
  const hotelCardRegex = /\[HOTEL_CARD:(\d+)\]/g

  let lastIndex = 0
  let match

  while ((match = hotelCardRegex.exec(text)) !== null) {
    if (match.index > lastIndex) {
      const textContent = text.substring(lastIndex, match.index)
      if (textContent.trim()) {
        segments.push({ type: 'text', content: textContent })
      }
    }

    const hotelIndex = parseInt(match[1])
    if (hotelIndex >= 0 && hotelsData.length > 0 && hotelIndex < hotelsData.length) {
      segments.push({ type: 'hotel', hotel: hotelsData[hotelIndex] })
    }

    lastIndex = match.index + match[0].length
  }

  if (lastIndex < text.length) {
    const textContent = text.substring(lastIndex)
    if (textContent.trim()) {
      segments.push({ type: 'text', content: textContent })
    }
  }

  if (segments.length === 0) {
    segments.push({ type: 'text', content: text })
  }

  return segments
}

export const formatTime = (timestamp: number) => {
  return new Date(timestamp).toLocaleString('zh-CN', {
    month: 'short',
    day: 'numeric',
    hour: 'numeric',
    minute: 'numeric'
  })
}
