/**
 * Minimal parser for the `*Markdown` content fields (Question.stemMarkdown,
 * solutionMarkdown, etc). Every one of the 239 generated questions uses only
 * plain text + inline `$...$` KaTeX (checked directly against the content
 * bank before writing this) — so rather than pull in a full markdown
 * dependency not listed in SPEC.md §7, this hand-rolled tokenizer covers
 * exactly what SPEC.md §7 already commits to (KaTeX) plus `$$...$$` block
 * math and `![alt](src)` images for forward-compatibility with future
 * PYQ-sourced content, without guessing at a general markdown grammar.
 */

export type MarkdownSegment =
  | { type: 'text'; value: string }
  | { type: 'inline-math'; value: string }
  | { type: 'block-math'; value: string }
  | { type: 'image'; alt: string; src: string }

const TOKEN_RE = /\$\$([\s\S]+?)\$\$|\$([^$\n]+?)\$|!\[([^\]]*)\]\(([^)]+)\)/g

export function parseMarkdownSegments(text: string): MarkdownSegment[] {
  const segments: MarkdownSegment[] = []
  let lastIndex = 0

  for (const match of text.matchAll(TOKEN_RE)) {
    const index = match.index
    if (index > lastIndex) {
      segments.push({ type: 'text', value: text.slice(lastIndex, index) })
    }

    const [, blockMath, inlineMath, imageAlt, imageSrc] = match
    if (blockMath !== undefined) {
      segments.push({ type: 'block-math', value: blockMath })
    } else if (inlineMath !== undefined) {
      segments.push({ type: 'inline-math', value: inlineMath })
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
