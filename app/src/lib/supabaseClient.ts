import { createClient, type SupabaseClient } from '@supabase/supabase-js'

/**
 * CLAUDE.md: "No API keys in client code, ever." This is not a violation — Supabase's anon key
 * is the one credential explicitly designed to ship in a client bundle (Supabase's own docs call
 * it "safe to use in a browser"); every table it can touch is locked down by the Row Level
 * Security policies in supabase/migrations/0001_init.sql, so the key alone grants no access to
 * anyone else's data. The service-role key (which DOES bypass RLS) never appears here — it's
 * used only inside the Edge Function (supabase/functions/daily-nudge), which runs on Supabase's
 * servers, never shipped to the browser.
 *
 * Both values are genuinely unset in this repo (no live Supabase project exists yet — see
 * PROGRESS.md Milestone 16) — `getSupabaseClient()` returns null until a real
 * VITE_SUPABASE_URL/VITE_SUPABASE_ANON_KEY pair is supplied via `app/.env.local` (gitignored) or
 * a CI/build-time env var, at which point sync and auth activate with no further code changes.
 */

const SUPABASE_URL = import.meta.env.VITE_SUPABASE_URL
const SUPABASE_ANON_KEY = import.meta.env.VITE_SUPABASE_ANON_KEY

let client: SupabaseClient | null | undefined

export function getSupabaseClient(): SupabaseClient | null {
  if (client !== undefined) return client
  client = SUPABASE_URL && SUPABASE_ANON_KEY ? createClient(SUPABASE_URL, SUPABASE_ANON_KEY) : null
  return client
}

export function isSupabaseConfigured(): boolean {
  return getSupabaseClient() !== null
}
