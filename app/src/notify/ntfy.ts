/**
 * ntfy transport (https://ntfy.sh).
 *
 * ## Why ntfy at all, when SPEC.md §11 already describes notifications
 *
 * §11 Phase 1 is a service-worker local notification, which can only fire *while the app is
 * open* — it cannot wake a closed phone, which is the one thing a reminder actually needs to
 * do. §11 Phase 2 solves that with a server (Supabase Edge Function + cron), which exists but
 * only sends email. ntfy fills the gap without a backend: the app POSTs to a topic and the
 * ntfy app on the phone rings, even with Ascent closed.
 *
 * ## Why this does not violate "no API keys in client code, ever" (CLAUDE.md)
 *
 * There is no key. Publishing to a public ntfy topic is unauthenticated — the topic name is
 * the only secret, it is typed in by the learner at runtime, and it lives in learner state like
 * any other setting. Nothing is baked into the bundle. The flip side, which the Settings copy
 * says out loud, is that the topic name *is* a password: anyone who guesses it can read the
 * notifications, so the UI generates a random one rather than letting someone pick "nidhi".
 *
 * ## Scheduled delivery and why the sequence id matters
 *
 * ntfy accepts a `delay` (up to 3 days out) so the app can schedule this evening's reminder
 * while it is open this morning. Crucially it also accepts a `sequence_id`: re-publishing with
 * the same one *replaces* the pending message rather than adding a second, and
 * `DELETE /<topic>/<sequence_id>` cancels it before delivery. That is what makes the daily
 * reminder honest — when the day's plan gets finished, the pending nudge is cancelled instead
 * of firing anyway and telling her she is behind when she is not.
 *
 * Verified against docs.ntfy.sh/publish (delay limits, sequence-id replace/cancel) and against
 * ntfy.sh itself for CORS: it answers a preflight with `access-control-allow-origin: *` and
 * allows POST/DELETE, so a static GitHub Pages build can publish directly from the browser.
 */

export const DEFAULT_NTFY_SERVER = 'https://ntfy.sh'

/** ntfy caps scheduled delivery at 3 days out; anything further is rejected by the server. */
export const MAX_DELAY_SECONDS = 3 * 24 * 60 * 60

export interface NtfyConfig {
  /** Base URL, no trailing slash. Self-hosted servers work identically. */
  server: string
  topic: string
}

export interface NtfyMessage {
  title: string
  body: string
  /** ntfy tag names double as emoji, e.g. 'books', 'alarm_clock'. */
  tags?: string[]
  /** 1 = min … 5 = max. 3 is ntfy's default. */
  priority?: 1 | 2 | 3 | 4 | 5
  /** Opened when the notification is tapped. */
  click?: string
  /** Unix seconds. Omit to deliver immediately. */
  deliverAt?: number
  /** Stable id for replace/cancel. See the module docstring. */
  sequenceId?: string
}

export interface NtfyResult {
  ok: boolean
  error: string | null
}

function normaliseServer(server: string): string {
  const trimmed = server.trim().replace(/\/+$/, '')
  return trimmed || DEFAULT_NTFY_SERVER
}

/** Topic names are path segments; ntfy itself only permits these characters. */
export function isValidTopic(topic: string): boolean {
  return /^[A-Za-z0-9_-]{1,64}$/.test(topic.trim())
}

/**
 * A random topic name. Offered in Settings because the topic *is* the password — a guessable
 * one means a stranger can subscribe to her study reminders.
 */
export function suggestTopic(): string {
  const bytes = new Uint8Array(9)
  crypto.getRandomValues(bytes)
  const suffix = Array.from(bytes, (b) => b.toString(36).padStart(2, '0')).join('').slice(0, 14)
  return `ascent-${suffix}`
}

/**
 * Publishes one message. Never throws: a study app must not break because a notification
 * server was unreachable, so every failure comes back as `{ ok: false, error }` for the caller
 * to show or ignore.
 *
 * Uses the JSON body form rather than `X-Title`-style headers, because HTTP header values are
 * ASCII-only and topic names appear in these titles.
 */
export async function publish(config: NtfyConfig, message: NtfyMessage): Promise<NtfyResult> {
  if (!isValidTopic(config.topic)) return { ok: false, error: 'Topic must be letters, numbers, - or _.' }

  const payload: Record<string, unknown> = {
    topic: config.topic.trim(),
    title: message.title,
    message: message.body,
  }
  if (message.tags?.length) payload.tags = message.tags
  if (message.priority) payload.priority = message.priority
  if (message.click) payload.click = message.click
  if (message.sequenceId) payload.sequence_id = message.sequenceId
  if (message.deliverAt) {
    const seconds = Math.round(message.deliverAt - Date.now() / 1000)
    if (seconds > MAX_DELAY_SECONDS) {
      return { ok: false, error: 'ntfy cannot schedule more than 3 days ahead.' }
    }
    // Below ntfy's 10-second floor a delayed message is rejected; sending it immediately is the
    // right behaviour anyway, since the scheduled moment has effectively arrived.
    if (seconds >= 10) payload.delay = String(Math.round(message.deliverAt))
  }

  try {
    const res = await fetch(normaliseServer(config.server), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })
    if (!res.ok) return { ok: false, error: `${res.status} ${res.statusText}` }
    return { ok: true, error: null }
  } catch (e) {
    return { ok: false, error: (e as Error).message }
  }
}

/**
 * Cancels a not-yet-delivered scheduled message. Best-effort and deliberately quiet: if it has
 * already been delivered, or the network is down, there is nothing useful to say to the learner
 * and nothing she could do about it.
 */
export async function cancelScheduled(config: NtfyConfig, sequenceId: string): Promise<boolean> {
  if (!isValidTopic(config.topic)) return false
  try {
    const res = await fetch(`${normaliseServer(config.server)}/${config.topic.trim()}/${sequenceId}`, {
      method: 'DELETE',
    })
    return res.ok
  } catch {
    return false
  }
}
