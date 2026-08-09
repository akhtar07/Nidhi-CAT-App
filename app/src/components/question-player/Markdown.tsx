import { Fragment } from 'react'
import { BlockMath, InlineMath } from 'react-katex'
import 'katex/dist/katex.min.css'
import { parseMarkdownSegments } from './markdownSegments'

/** Renders a Question `*Markdown` field — see markdownSegments.ts for what's supported and why. */
export function Markdown({ text }: { text: string }) {
  const segments = parseMarkdownSegments(text)
  return (
    <>
      {segments.map((segment, i) => {
        switch (segment.type) {
          case 'text':
            return (
              <Fragment key={i}>
                {segment.value.split('\n').map((line, j, arr) => (
                  <Fragment key={j}>
                    {line}
                    {j < arr.length - 1 && <br />}
                  </Fragment>
                ))}
              </Fragment>
            )
          case 'inline-math':
            return <InlineMath key={i} math={segment.value} renderError={renderMathError} />
          case 'block-math':
            return <BlockMath key={i} math={segment.value} renderError={renderMathError} />
          case 'image':
            return <img key={i} alt={segment.alt} src={segment.src} className="my-2 max-w-full rounded" />
        }
      })}
    </>
  )
}

function renderMathError(error: Error) {
  return (
    <span className="text-destructive" title={error.message}>
      [math render error]
    </span>
  )
}
