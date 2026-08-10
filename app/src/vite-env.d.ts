/// <reference types="vite/client" />
/// <reference types="vite-plugin-pwa/client" />

interface ImportMetaEnv {
  /** Milestone 16 — unset in this repo (no live Supabase project yet); see lib/supabaseClient.ts. */
  readonly VITE_SUPABASE_URL?: string
  readonly VITE_SUPABASE_ANON_KEY?: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
