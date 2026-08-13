import { describe, expect, it } from 'vitest'
import { parseMarkdownBlocks, parseMarkdownSegments } from './markdownSegments'

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

  it('parses bold text', () => {
    expect(parseMarkdownSegments('always divide by the **original** value')).toEqual([
      { type: 'text', value: 'always divide by the ' },
      { type: 'bold', value: 'original' },
      { type: 'text', value: ' value' },
    ])
  })
})

describe('parseMarkdownBlocks', () => {
  it('splits blank-line-separated text into paragraphs', () => {
    const blocks = parseMarkdownBlocks('First paragraph.\n\nSecond paragraph.')
    expect(blocks).toEqual([
      { type: 'paragraph', segments: [{ type: 'text', value: 'First paragraph.' }] },
      { type: 'paragraph', segments: [{ type: 'text', value: 'Second paragraph.' }] },
    ])
  })

  it('detects ## and ### headings and strips the prefix', () => {
    const blocks = parseMarkdownBlocks('## Percentages\n\n### Reverse percentage\n\nSome body text.')
    expect(blocks).toEqual([
      { type: 'heading', level: 2, segments: [{ type: 'text', value: 'Percentages' }] },
      { type: 'heading', level: 3, segments: [{ type: 'text', value: 'Reverse percentage' }] },
      { type: 'paragraph', segments: [{ type: 'text', value: 'Some body text.' }] },
    ])
  })

  it('runs inline math/bold parsing within each block', () => {
    const blocks = parseMarkdownBlocks('## Title\n\nText with $x^2$ and **bold**.')
    expect(blocks[1]).toEqual({
      type: 'paragraph',
      segments: [
        { type: 'text', value: 'Text with ' },
        { type: 'inline-math', value: 'x^2' },
        { type: 'text', value: ' and ' },
        { type: 'bold', value: 'bold' },
        { type: 'text', value: '.' },
      ],
    })
  })
})

describe('lists', () => {
  it('parses a bullet block into one list', () => {
    const blocks = parseMarkdownBlocks('- first\n- second\n- third')
    expect(blocks).toHaveLength(1)
    expect(blocks[0]).toMatchObject({ type: 'list', ordered: false })
    if (blocks[0].type !== 'list') throw new Error('expected a list')
    expect(blocks[0].items).toHaveLength(3)
    expect(blocks[0].items[0]).toEqual([{ type: 'text', value: 'first' }])
  })

  it('parses a numbered block as an ordered list', () => {
    const blocks = parseMarkdownBlocks('1. step one\n2. step two')
    expect(blocks[0]).toMatchObject({ type: 'list', ordered: true })
  })

  it('keeps math and bold inside list items', () => {
    const blocks = parseMarkdownBlocks('- **Spot it:** when $x > 0$')
    if (blocks[0].type !== 'list') throw new Error('expected a list')
    expect(blocks[0].items[0]).toEqual([
      { type: 'bold', value: 'Spot it:' },
      { type: 'text', value: ' when ' },
      { type: 'inline-math', value: 'x > 0' },
    ])
  })

  it('leaves a paragraph that merely starts with a number alone', () => {
    // "1. 5" is a decimal in prose, not a list marker — an all-or-nothing rule is what stops
    // a sentence like this from rendering as a one-item list.
    const blocks = parseMarkdownBlocks('The ratio came to 1. 5 times the original figure.')
    expect(blocks[0].type).toBe('paragraph')
  })

  it('does not treat a mixed block as a list', () => {
    const blocks = parseMarkdownBlocks('- a bullet\nand a trailing sentence')
    expect(blocks[0].type).toBe('paragraph')
  })
})
