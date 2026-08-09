/**
 * Minimal parser for the `*Markdown` content fields (Question.stemMarkdown,
 * Lesson.bodyMarkdown, etc). Not a general markdown grammar — extended only
 * as far as the actual content needs, checked directly against the content
 * bank each time rather than guessed at, to avoid pulling in a markdown
 * dependency not listed in SPEC.md §7:
 *  - inline `$...$` / block `$$...$$` KaTeX (all question content)
 *  - `**bold**` (Lesson prose, Milestone 6)
 *  - `## `/`### ` headings and blank-line-separated paragraphs (Lesson
 *    prose — question stems are single paragraphs, so this is a no-op for
 *    them)
 *  - `![alt](src)` images, for forward compatibility with future
 *    PYQ-sourced content — nothing uses this yet
 */

export type MarkdownSegment =
  | { type: 'text'; value: string }
  | { type: 'inline-math'; value: string }
  | { type: 'block-math'; value: string }
  | { type: 'bold'; value: string }
  | { type: 'image'; alt: string; src: string }

export type MarkdownBlock =
  | { type: 'heading'; level: 2 | 3; segments: MarkdownSegment[] }
  | { type: 'paragraph'; segments: MarkdownSegment[] }

const TOKEN_RE = /\$\$([\s\S]+?)\$\$|\$([^$\n]+?)\$|\*\*([^*]+?)\*\*|!\[([^\]]*)\]\(([^)]+)\)/g

export function parseMarkdownSegments(text: string): MarkdownSegment[] {
  const segments: MarkdownSegment[] = []
  let lastIndex = 0

  for (const match of text.matchAll(TOKEN_RE)) {
    const index = match.index
    if (index > lastIndex) {
      segments.push({ type: 'text', value: text.slice(lastIndex, index) })
    }

    const [, blockMath, inlineMath, bold, imageAlt, imageSrc] = match
    if (blockMath !== undefined) {
      segments.push({ type: 'block-math', value: blockMath })
    } else if (inlineMath !== undefined) {
      segments.push({ type: 'inline-math', value: inlineMath })
    } else if (bold !== undefined) {
      segments.push({ type: 'bold', value: bold })
    } else {
      segments.push({ type: 'image', alt: imageAlt ?? '', src: imageSrc ?? '' })
    }

    lastIndex = index + match[0].length
  }

  if (lastIndex < text.length) {
    segments.push({ type: 'text', value: text.slice(lastIndex) })
  }

  return segments
}

/** Splits on blank lines into paragraphs, detecting `## `/`### ` heading prefixes. */
export function parseMarkdownBlocks(text: string): MarkdownBlock[] {
  return text
    .trim()
    .split(/\n{2,}/)
    .map((raw) => raw.trim())
    .filter((raw) => raw.length > 0)
    .map((raw) => {
      if (raw.startsWith('### ')) {
        return { type: 'heading', level: 3 as const, segments: parseMarkdownSegments(raw.slice(4)) }
      }
      if (raw.startsWith('## ')) {
        return { type: 'heading', level: 2 as const, segments: parseMarkdownSegments(raw.slice(3)) }
      }
      return { type: 'paragraph', segments: parseMarkdownSegments(raw) }
    })
}
