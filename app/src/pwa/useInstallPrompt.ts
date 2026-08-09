import { useEffect, useState } from 'react'

interface BeforeInstallPromptEvent extends Event {
  prompt(): Promise<void>
  userChoice: Promise<{ outcome: 'accepted' | 'dismissed' }>
}

/** Chrome/Android-family browsers fire 'beforeinstallprompt' once the PWA installability
 * criteria (manifest + service worker + served securely) are met; Safari/iOS never fires it
 * and relies on the OS-level "Add to Home Screen" share-sheet action instead — there is no
 * programmatic install prompt to capture there, so canInstall staying false on iOS is
 * expected, not a bug. */
export function useInstallPrompt() {
  const [event, setEvent] = useState<BeforeInstallPromptEvent | null>(null)
  const [installed, setInstalled] = useState(false)

  useEffect(() => {
    function onBeforeInstallPrompt(e: Event) {
      e.preventDefault()
      setEvent(e as BeforeInstallPromptEvent)
    }
    function onAppInstalled() {
      setInstalled(true)
      setEvent(null)
    }
    window.addEventListener('beforeinstallprompt', onBeforeInstallPrompt)
    window.addEventListener('appinstalled', onAppInstalled)
    return () => {
      window.removeEventListener('beforeinstallprompt', onBeforeInstallPrompt)
      window.removeEventListener('appinstalled', onAppInstalled)
    }
  }, [])

  async function promptInstall() {
    if (!event) return
    await event.prompt()
    const choice = await event.userChoice
    if (choice.outcome === 'accepted') setInstalled(true)
    setEvent(null)
  }

  return { canInstall: event !== null, installed, promptInstall }
}
