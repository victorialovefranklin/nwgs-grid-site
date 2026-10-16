-- NWGS Grid™ backend schema (Supabase / Postgres)
-- Author: Victoria Love Franklin — PhD Data Science Student · Published Research Scholar · Developer
-- Copyright © 2026 Victoria Love Franklin. All rights reserved. See LICENSE.
--
-- Run once: Supabase dashboard → SQL Editor → New query → paste this file → Run.
-- Safe to re-run: every statement checks whether the object already exists.
--
-- Security model (Row Level Security):
--   * Signed-in people see and change only their own profile and alert rules.
--   * Anyone may SUBMIT feedback or a license request; nobody can read them through
--     the public website. You read them in Table Editor (or via the secret key).
--   * The weekly GitHub run uses the secret key, which bypasses these rules.

-- ---------- profiles (one row per signed-in person) ----------
create table if not exists public.profiles (
  id          uuid primary key references auth.users(id) on delete cascade,
  email       text not null,
  created_at  timestamptz not null default now(),
  alerts_paused boolean not null default false
);
alter table public.profiles enable row level security;
drop policy if exists "own profile read"   on public.profiles;
drop policy if exists "own profile update" on public.profiles;
create policy "own profile read"   on public.profiles for select to authenticated using (id = auth.uid());
create policy "own profile update" on public.profiles for update to authenticated using (id = auth.uid()) with check (id = auth.uid());

-- create the profile automatically when someone signs in for the first time
create or replace function public.handle_new_user() returns trigger
language plpgsql security definer set search_path = public as $$
begin
  insert into public.profiles (id, email) values (new.id, new.email)
  on conflict (id) do update set email = excluded.email;
  return new;
end $$;
drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created after insert on auth.users
  for each row execute function public.handle_new_user();

-- ---------- saved alert rules ----------
create table if not exists public.alert_rules (
  id          bigint generated always as identity primary key,
  user_id     uuid not null default auth.uid() references auth.users(id) on delete cascade,
  pathogen    text not null check (pathogen in ('SARS-CoV-2','RSV','Influenza A')),
  area_type   text not null check (area_type in ('state','county')),
  area_code   text not null check (char_length(area_code) between 2 and 5),  -- state code (TN) or county FIPS (47037)
  area_label  text not null check (char_length(area_label) <= 120),
  min_level   text not null check (min_level in ('Elevated','High')),
  active      boolean not null default true,
  created_at  timestamptz not null default now(),
  unique (user_id, pathogen, area_type, area_code, min_level)
);
create index if not exists alert_rules_user on public.alert_rules(user_id);
alter table public.alert_rules enable row level security;
drop policy if exists "own rules" on public.alert_rules;
create policy "own rules" on public.alert_rules for all to authenticated
  using (user_id = auth.uid()) with check (user_id = auth.uid());

-- no more than 25 rules per person
create or replace function public.limit_alert_rules() returns trigger
language plpgsql as $$
begin
  if (select count(*) from public.alert_rules where user_id = new.user_id) >= 25 then
    raise exception 'Limit of 25 alert rules reached';
  end if;
  return new;
end $$;
drop trigger if exists alert_rules_limit on public.alert_rules;
create trigger alert_rules_limit before insert on public.alert_rules
  for each row execute function public.limit_alert_rules();

-- ---------- feedback and license requests (write-only from the site) ----------
create table if not exists public.feedback (
  id          bigint generated always as identity primary key,
  created_at  timestamptz not null default now(),
  user_id     uuid default auth.uid(),
  email       text check (email is null or char_length(email) <= 200),
  page        text check (char_length(page) <= 60),
  message     text not null check (char_length(message) between 3 and 5000),
  run_id      text check (char_length(run_id) <= 40),
  status      text not null default 'new'
);
alter table public.feedback enable row level security;
drop policy if exists "anyone can send feedback" on public.feedback;
create policy "anyone can send feedback" on public.feedback for insert to anon, authenticated
  with check (status = 'new' and (user_id is null or user_id = auth.uid()));

create table if not exists public.license_requests (
  id            bigint generated always as identity primary key,
  created_at    timestamptz not null default now(),
  user_id       uuid default auth.uid(),
  name          text not null check (char_length(name) between 1 and 200),
  email         text not null check (char_length(email) between 3 and 200),
  organization  text check (char_length(organization) <= 200),
  intended_use  text not null check (intended_use in ('Research','Commercial','Teaching','Public health practice','Other')),
  parts         text check (char_length(parts) <= 500),
  message       text check (char_length(message) <= 5000),
  status        text not null default 'new'
);
alter table public.license_requests enable row level security;
drop policy if exists "anyone can request a license" on public.license_requests;
create policy "anyone can request a license" on public.license_requests for insert to anon, authenticated
  with check (status = 'new' and (user_id is null or user_id = auth.uid()));

-- ---------- weekly runs and alert log (written only by the GitHub run) ----------
create table if not exists public.pipeline_runs (
  run_id        text primary key,
  data_as_of    date not null,
  data_pulled_utc timestamptz,
  gate_status   text,
  release_tag   text,
  loaded_at     timestamptz not null default now()
);
alter table public.pipeline_runs enable row level security;
drop policy if exists "runs are public" on public.pipeline_runs;
create policy "runs are public" on public.pipeline_runs for select to anon, authenticated using (true);

create table if not exists public.alert_log (
  id          bigint generated always as identity primary key,
  rule_id     bigint not null references public.alert_rules(id) on delete cascade,
  run_id      text not null,
  sent_at     timestamptz not null default now(),
  detail      text,
  unique (rule_id, run_id)
);
alter table public.alert_log enable row level security;
drop policy if exists "own alert log" on public.alert_log;
create policy "own alert log" on public.alert_log for select to authenticated
  using (exists (select 1 from public.alert_rules r where r.id = rule_id and r.user_id = auth.uid()));
