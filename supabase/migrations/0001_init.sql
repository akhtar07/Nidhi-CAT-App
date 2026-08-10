-- Milestone 16 (SPEC.md §12 option B). Mirrors app/src/types/state.ts's learner-state types —
-- one table per StorageAdapter-synced type (see app/src/storage/supabase/toRow.ts for the exact
-- camelCase-field -> snake_case-column mapping). Column names here MUST stay in lockstep with
-- toRow.ts; there is no schema-generation pipeline for this side the way /content has one.
--
-- mock_session is deliberately NOT a table here — SPEC.md's crash-recovery requirement is
-- local-only (see SupabaseSyncAdapter's header comment), so it never leaves IndexedDB.
--
-- Every table is owned per-row by auth.uid() and locked down with Row Level Security so the
-- anon key (shipped in the client bundle — see app/src/lib/supabaseClient.ts) can only ever
-- read or write its own signed-in user's rows, never anyone else's.
--
-- Apply with the Supabase CLI once a real project exists: `supabase db push`, or paste this
-- file into the SQL editor in the Supabase dashboard. Inert until then — see PROGRESS.md.

create table if not exists public.attempts (
  id text not null,
  user_id uuid not null references auth.users (id) on delete cascade,
  question_id text not null,
  micro_topic_ids text[] not null,
  started_at bigint not null,
  submitted_at bigint not null,
  time_spent_sec integer not null,
  given text,
  correct boolean not null,
  confidence text,
  error_tag text,
  mode text not null,
  marked_for_review boolean not null,
  primary key (user_id, id)
);

create table if not exists public.mastery_states (
  micro_topic_id text not null,
  user_id uuid not null references auth.users (id) on delete cascade,
  status text not null,
  learner_elo double precision not null,
  last_n_correct boolean[] not null,
  median_time_sec double precision not null,
  hard_tier_cleared boolean not null,
  attempts_count integer not null,
  mastered_at bigint,
  criteria123_first_met_at bigint,
  anti_frustration_triggered boolean,
  next_review_at bigint,
  stability double precision not null,
  difficulty double precision not null,
  last_reviewed_at bigint,
  primary key (user_id, micro_topic_id)
);

create table if not exists public.plan_days (
  date text not null,
  user_id uuid not null references auth.users (id) on delete cascade,
  items jsonb not null,
  status text not null,
  primary key (user_id, date)
);

create table if not exists public.mock_results (
  id text not null,
  user_id uuid not null references auth.users (id) on delete cascade,
  mock_id text not null,
  taken_at bigint not null,
  section_scores jsonb not null,
  question_timings jsonb not null,
  percentile_estimate double precision,
  started_at bigint,
  primary key (user_id, id)
);

create table if not exists public.item_elo (
  question_id text not null,
  user_id uuid not null references auth.users (id) on delete cascade,
  elo double precision not null,
  primary key (user_id, question_id)
);

create table if not exists public.settings (
  id text not null default 'singleton',
  user_id uuid not null references auth.users (id) on delete cascade,
  daily_minutes integer not null,
  exam_date text not null,
  weak_section_bias text,
  email_opt_in boolean not null default false,
  diagnostic_completed_at bigint,
  notifications_enabled boolean,
  last_nudge_shown_date text,
  primary key (user_id, id)
);

create table if not exists public.srs_cards (
  id text not null,
  user_id uuid not null references auth.users (id) on delete cascade,
  card_type text not null,
  ref_id text not null,
  micro_topic_id text not null,
  stability double precision not null,
  difficulty double precision not null,
  next_review_at bigint not null,
  last_reviewed_at bigint,
  added_at bigint not null,
  primary key (user_id, id)
);

-- SPEC.md §11: "Never more than one email per day. Hard-limit it in code." Enforced at the
-- database level, not just in the Edge Function's own logic — a duplicate insert for the same
-- (user_id, sent_date) fails the primary key constraint, so even a retried/duplicated cron
-- invocation can't double-send. Only the Edge Function (using the service-role key, server-side
-- only) ever writes here — no RLS insert policy for the anon/authenticated role.
create table if not exists public.email_log (
  user_id uuid not null references auth.users (id) on delete cascade,
  sent_date date not null,
  email_type text not null,
  sent_at timestamptz not null default now(),
  primary key (user_id, sent_date)
);

alter table public.attempts enable row level security;
alter table public.mastery_states enable row level security;
alter table public.plan_days enable row level security;
alter table public.mock_results enable row level security;
alter table public.item_elo enable row level security;
alter table public.settings enable row level security;
alter table public.srs_cards enable row level security;
alter table public.email_log enable row level security;

create policy "own rows only" on public.attempts for all using (auth.uid() = user_id) with check (auth.uid() = user_id);
create policy "own rows only" on public.mastery_states for all using (auth.uid() = user_id) with check (auth.uid() = user_id);
create policy "own rows only" on public.plan_days for all using (auth.uid() = user_id) with check (auth.uid() = user_id);
create policy "own rows only" on public.mock_results for all using (auth.uid() = user_id) with check (auth.uid() = user_id);
create policy "own rows only" on public.item_elo for all using (auth.uid() = user_id) with check (auth.uid() = user_id);
create policy "own rows only" on public.settings for all using (auth.uid() = user_id) with check (auth.uid() = user_id);
create policy "own rows only" on public.srs_cards for all using (auth.uid() = user_id) with check (auth.uid() = user_id);

-- email_log: readable by its own owner (so a future "you were last emailed on X" UI is possible
-- without a new migration), never writable by anon/authenticated — only the Edge Function's
-- service-role key bypasses RLS to insert here.
create policy "read own email log" on public.email_log for select using (auth.uid() = user_id);
