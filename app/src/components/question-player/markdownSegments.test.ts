import { describe, expect, it } from 'vitest'
import { parseMarkdownSegments } from './markdownSegments'

describe('parseMarkdownSegments', () => {
  it('returns a single text segment for plain text', () => {
    expect(parseMarkdownSegments('no math here')).toEqual([{ type: 'text', value: 'no math here' }])
  })

  it('splits inline math out of surrounding text', () => {
    expect(parseMarkdownSegments('If $f(x) = 4x + 9$, find $f(-2)$.')).toEqual([
      { type: 'text', value: 'If ' },
      { type: 'inline-math', value: 'f(x) = 4x + 9' },
      { type: 'text', value: ', find ' },
      { type: 'inline-math', value: 'f(-2)' },
      { type: 'text', value: '.' },
    ])
  })

  it('prefers block math over inline math for $$...$$', () => {
    expect(parseMarkdownSegments('$$x^2 + 1$$')).toEqual([{ type: 'block-math', value: 'x^2 + 1' }])
  })

  it('parses image syntax', () => {
    expect(parseMarkdownSegments('See ![triangle](assets/tri.png) above.')).toEqual([
      { type: 'text', value: 'See ' },
      { type: 'image', alt: 'triangle', src: 'assets/tri.png' },
      { type: 'text', value: ' above.' },
    ])
  })
})
