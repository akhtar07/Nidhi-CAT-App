-- Phone reminders via ntfy (app/src/notify/ntfy.ts).
--
-- Stored as jsonb rather than one column per field because these are two cohesive blobs the
-- app reads and writes whole, and neither is ever queried on server-side: `ntfy` is the
-- learner's channel config, `ntfy_state` is the app's own "already sent this" bookkeeping.
-- Flattening them would add six columns and a migration every time the reminder rules change.
--
-- No secret lands here that is not already a secret on the device: ntfy topics are
-- unauthenticated, so the topic name is the only credential and it is the learner's own.

alter table public.settings add column if not exists ntfy jsonb;
alter table public.settings add column if not exists ntfy_state jsonb;
