import { useEffect, useState } from 'react'
import { getSupabaseClient, isSupabaseConfigured } from '@/lib/supabaseClient'

interface AuthState {
  configured: boolean
  email: string | null
  loading: boolean
}

/**
 * Magic-link auth (SPEC.md §12 option B, §16 acceptance "multi-device sync"). Single-user app —
 * this exists so the same learner can open Ascent on a phone and a laptop and see the same
 * progress, not for any multi-tenant/social purpose (SPEC.md §0: "no signup flow... no social
 * feature" — the magic link is the *sync* login, not a product signup).
 */
export function useSupabaseAuth() {
  const [state, setState] = useState<AuthState>({
    configured: isSupabaseConfigured(),
    email: null,
    loading: isSupabaseConfigured(),
  })

  useEffect(() => {
    const client = getSupabaseClient()
    if (!client) return

    client.auth.getSession().then(({ data }) => {
      setState((s) => ({ ...s, email: data.session?.user.email ?? null, loading: false }))
    })

    const { data: subscription } = client.auth.onAuthStateChange((_event, session) => {
      setState((s) => ({ ...s, email: session?.user.email ?? null }))
    })
    return () => subscription.subscription.unsubscribe()
  }, [])

  async function sendMagicLink(email: string): Promise<{ error: string | null }> {
    const client = getSupabaseClient()
    if (!client) return { error: 'Supabase is not configured.' }
    const { error } = await client.auth.signInWithOtp({ email, options: { emailRedirectTo: window.location.href } })
    return { error: error?.message ?? null }
  }

  async function signOut(): Promise<void> {
    await getSupabaseClient()?.auth.signOut()
  }

  return { ...state, sendMagicLink, signOut }
}
