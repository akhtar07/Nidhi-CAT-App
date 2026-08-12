-- Professionalization pass: manual question bookmarks (study-flow feature), synced the same way
-- as every other StorageAdapter-backed table — see app/src/storage/supabase/toRow.ts for the
-- camelCase -> snake_case mapping. Inert until a real Supabase project exists, same as
-- 0001_init.sql — see that file's header and PROGRESS.md.

create table if not exists public.bookmarks (
  id text not null,
  user_id uuid not null references auth.users (id) on delete cascade,
  question_id text not null,
  micro_topic_id text not null,
  created_at bigint not null,
  primary key (user_id, id)
);

alter table public.bookmarks enable row level security;

create policy "own rows only" on public.bookmarks for all using (auth.uid() = user_id) with check (auth.uid() = user_id);
