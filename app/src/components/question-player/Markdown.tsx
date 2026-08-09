import { Fragment, type ReactNode } from 'react'
import { BlockMath, InlineMath } from 'react-katex'
import 'katex/dist/katex.min.css'
import { parseMarkdownBlocks, parseMarkdownSegments, type MarkdownSegment } from './markdownSegments'

function renderMathError(error: Error) {
  return (
    <span className="text-destructive" title={error.message}>
      [math render error]
    </span>
  )
}

function renderSegments(segments: MarkdownSegment[], keyPrefix: string): ReactNode[] {
  return segments.map((segment, i) => {
    const key = `${keyPrefix}-${i}`
    switch (segment.type) {
      case 'text':
        return (
          <Fragment key={key}>
            {segment.value.split('\n').map((line, j, arr) => (
              <Fragment key={j}>
                {line}
                {j < arr.length - 1 && <br />}
              </Fragment>
            ))}
          </Fragment>
        )
      case 'bold':
        return <strong key={key}>{segment.value}</strong>
      case 'inline-math':
        return <InlineMath key={key} math={segment.value} renderError={renderMathError} />
      case 'block-math':
        return <BlockMath key={key} math={segment.value} renderError={renderMathError} />
      case 'image':
        return <img key={key} alt={segment.alt} src={segment.src} className="my-2 max-w-full rounded" />
    }
  })
}

/** Renders a single-paragraph `*Markdown` field (question stems, solutions, options). */
export function Markdown({ text }: { text: string }) {
  return <>{renderSegments(parseMarkdownSegments(text), 'seg')}</>
}

/** Renders a multi-paragraph `*Markdown` field with `##`/`###` headings (Lesson.bodyMarkdown). */
export function MarkdownBlocks({ text }: { text: string }) {
  const blocks = parseMarkdownBlocks(text)
  return (
    <div className="space-y-3">
      {blocks.map((block, i) => {
        const key = `block-${i}`
        const content = renderSegments(block.segments, key)
        if (block.type === 'heading') {
          return block.level === 2 ? (
            <h2 key={key} className="text-lg font-semibold">
              {content}
            </h2>
          ) : (
            <h3 key={key} className="font-semibold">
              {content}
            </h3>
          )
        }
        return (
          // A plain <p> would be invalid here: BlockMath ($$...$$) renders a
          // <div>, and a paragraph can't contain one.
          <div key={key} className="leading-relaxed">
            {content}
          </div>
        )
      })}
    </div>
  )
}
