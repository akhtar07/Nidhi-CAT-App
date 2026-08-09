import { useRef, useState } from 'react'
import { Link } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { storage } from '@/storage'

/**
 * SPEC.md §5.2: "Ship an Export / Import JSON button in Settings before
 * Milestone 5 — if IndexedDB is cleared, all her work vanishes." Built now
 * (Milestone 5) since the storage layer it depends on (Milestone 2) is the
 * prerequisite, and there was no Settings page to hang the button off
 * before this. Only the export/import feature — the rest of Settings
 * (§5.2's dailyMinutes/examDate/weakSectionBias/emailOptIn fields) belongs
 * to whichever milestone actually builds the planner UI around them.
 */
export function Settings() {
  const [status, setStatus] = useState<string | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  async function handleExport() {
    const bundle = await storage.exportAll()
    const blob = new Blob([JSON.stringify(bundle, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `ascent-backup-${new Date().toISOString().slice(0, 10)}.json`
    a.click()
    URL.revokeObjectURL(url)
    setStatus('Exported.')
  }

  async function handleImportFile(file: File) {
    try {
      const text = await file.text()
      const bundle = JSON.parse(text)
      await storage.importAll(bundle)
      setStatus('Imported — this replaced all existing local data.')
    } catch (e) {
      setStatus(`Import failed: ${(e as Error).message}`)
    }
  }

  return (
    <main className="mx-auto max-w-2xl space-y-6 p-6">
      <div>
        <Link to="/" className="text-sm text-primary underline">
          Back
        </Link>
        <h1 className="mt-2 text-2xl font-semibold">Settings</h1>
      </div>

      <section className="space-y-2">
        <h2 className="font-medium">Backup</h2>
        <p className="text-sm text-muted-foreground">
          All progress lives only in this browser. Export regularly — clearing site data or switching devices
          loses everything otherwise.
        </p>
        <div className="flex gap-2">
          <Button onClick={() => void handleExport()}>Export JSON</Button>
          <Button variant="outline" onClick={() => fileInputRef.current?.click()}>
            Import JSON
          </Button>
          <input
            ref={fileInputRef}
            type="file"
            accept="application/json"
            className="hidden"
            onChange={(e) => {
              const file = e.target.files?.[0]
              if (file) void handleImportFile(file)
              e.target.value = ''
            }}
          />
        </div>
        {status && <p className="text-sm text-muted-foreground">{status}</p>}
      </section>
    </main>
  )
}
