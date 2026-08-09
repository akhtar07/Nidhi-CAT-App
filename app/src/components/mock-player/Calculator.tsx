import { useRef, useState } from 'react'

/** SPEC.md §9.1: "Basic on-screen calculator only. Four functions plus percent and square root
 * at most. Draggable." Deliberately no more than that — the real CAT calculator is this basic,
 * and the whole point is to build the habit of not reaching for a scientific one. */
export function Calculator({ onClose }: { onClose: () => void }) {
  const [display, setDisplay] = useState('0')
  const [pending, setPending] = useState<{ value: number; op: string } | null>(null)
  const [pos, setPos] = useState({ x: 24, y: 96 })
  const dragRef = useRef<{ startX: number; startY: number; origX: number; origY: number } | null>(null)

  function onPointerDown(e: React.PointerEvent) {
    dragRef.current = { startX: e.clientX, startY: e.clientY, origX: pos.x, origY: pos.y }
    ;(e.target as Element).setPointerCapture(e.pointerId)
  }
  function onPointerMove(e: React.PointerEvent) {
    if (!dragRef.current) return
    const { startX, startY, origX, origY } = dragRef.current
    setPos({ x: origX + (e.clientX - startX), y: origY + (e.clientY - startY) })
  }
  function onPointerUp() {
    dragRef.current = null
  }

  function inputDigit(d: string) {
    setDisplay((prev) => (prev === '0' ? d : prev + d))
  }
  function inputDot() {
    setDisplay((prev) => (prev.includes('.') ? prev : prev + '.'))
  }
  function clear() {
    setDisplay('0')
    setPending(null)
  }
  function applyOp(op: string) {
    const current = Number(display)
    if (pending) {
      const result = compute(pending.value, current, pending.op)
      setDisplay(String(result))
      setPending({ value: result, op })
    } else {
      setPending({ value: current, op })
    }
    setDisplay('0')
  }
  function equals() {
    if (!pending) return
    const result = compute(pending.value, Number(display), pending.op)
    setDisplay(String(result))
    setPending(null)
  }
  function percent() {
    setDisplay((prev) => String(Number(prev) / 100))
  }
  function sqrt() {
    setDisplay((prev) => String(Math.sqrt(Number(prev))))
  }

  return (
    <div
      className="fixed z-50 w-56 rounded-lg border border-border bg-background shadow-lg"
      style={{ left: pos.x, top: pos.y }}
    >
      <div
        className="flex cursor-move items-center justify-between rounded-t-lg bg-muted px-2 py-1 text-xs"
        onPointerDown={onPointerDown}
        onPointerMove={onPointerMove}
        onPointerUp={onPointerUp}
      >
        <span>Calculator</span>
        <button type="button" onClick={onClose} className="px-1 text-muted-foreground hover:text-foreground">
          ✕
        </button>
      </div>
      <div className="p-2">
        <div className="mb-2 rounded bg-muted px-2 py-1 text-right text-lg tabular-nums">{display}</div>
        <div className="grid grid-cols-4 gap-1 text-sm">
          {['7', '8', '9', '/'].map((k) => (
            <CalcButton key={k} onClick={() => (k === '/' ? applyOp('/') : inputDigit(k))}>
              {k}
            </CalcButton>
          ))}
          {['4', '5', '6', '*'].map((k) => (
            <CalcButton key={k} onClick={() => (k === '*' ? applyOp('*') : inputDigit(k))}>
              {k}
            </CalcButton>
          ))}
          {['1', '2', '3', '-'].map((k) => (
            <CalcButton key={k} onClick={() => (k === '-' ? applyOp('-') : inputDigit(k))}>
              {k}
            </CalcButton>
          ))}
          <CalcButton onClick={sqrt}>√</CalcButton>
          <CalcButton onClick={() => inputDigit('0')}>0</CalcButton>
          <CalcButton onClick={inputDot}>.</CalcButton>
          <CalcButton onClick={() => applyOp('+')}>+</CalcButton>
          <CalcButton onClick={percent}>%</CalcButton>
          <CalcButton onClick={clear}>C</CalcButton>
          <CalcButton onClick={equals} className="col-span-2 bg-primary text-primary-foreground">
            =
          </CalcButton>
        </div>
      </div>
    </div>
  )
}

function compute(a: number, b: number, op: string): number {
  switch (op) {
    case '+':
      return a + b
    case '-':
      return a - b
    case '*':
      return a * b
    case '/':
      return b === 0 ? NaN : a / b
    default:
      return b
  }
}

function CalcButton({
  children,
  onClick,
  className = '',
}: {
  children: React.ReactNode
  onClick: () => void
  className?: string
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`rounded border border-border py-1.5 hover:bg-muted ${className}`}
    >
      {children}
    </button>
  )
}
