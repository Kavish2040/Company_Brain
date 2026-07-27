-- The derived index (ARCHITECTURE §5).
--
-- Every table here is a CACHE. `cb index rebuild` truncates and repopulates all
-- of it from the markdown store, and invariant 2 says that must reproduce the
-- index exactly. Nothing in this file may become authoritative: no defaults that
-- invent data, no triggers that edit content, no columns the markdown cannot
-- regenerate.
--
-- The tables §5 lists that are NOT here — principals, acl_grants, review_queue,
-- sources, ingest_runs — are deliberately omitted. They are workflow state
-- rather than derived data, they survive a rebuild, and they belong with the
-- connector and store work rather than with the index.

create extension if not exists vector;

-- Sensitivity is an ordered enum, so a ceiling comparison is `<=` in SQL rather
-- than a set membership test. That ordering is the whole point: a grant with a
-- `restricted` ceiling admits internal and public content beneath it, and
-- comparing loose sets instead is the cross-product bug invariant 5a describes.
do $$
begin
  if not exists (select 1 from pg_type where typname = 'cb_sensitivity') then
    create type cb_sensitivity as enum ('public', 'internal', 'restricted');
  end if;
end
$$;

create table if not exists nodes (
    id              text primary key,
    type            text        not null,
    title           text        not null,
    acl_ref         text        not null,
    sensitivity     cb_sensitivity not null,
    status          text        not null,
    content_sha256  text        not null default ''
);

-- The permission filter is one indexed predicate in the same query as the
-- search, never a post-filter (ARCHITECTURE §5, §6.4).
create index if not exists nodes_acl_idx on nodes (acl_ref, sensitivity);
create index if not exists nodes_type_idx on nodes (type);

create table if not exists chunks (
    id            text primary key,          -- "<node_id>#<ordinal>"
    node_id       text not null references nodes (id) on delete cascade,
    ordinal       int  not null,
    heading_path  text not null,
    text          text not null,
    token_count   int  not null default 0,
    -- acl_ref and sensitivity are denormalised from the node on purpose: it
    -- keeps the ACL join off the hot path of a vector scan.
    acl_ref       text not null,
    sensitivity   cb_sensitivity not null,
    -- Generated, so it can never drift from `text`. English is the only
    -- configuration the corpus needs today; a per-node language column is the
    -- migration to write when that stops being true.
    tsv tsvector generated always as (to_tsvector('english', heading_path || ' ' || text)) stored
);

create index if not exists chunks_acl_idx on chunks (acl_ref, sensitivity);
create index if not exists chunks_node_idx on chunks (node_id);
create index if not exists chunks_tsv_idx on chunks using gin (tsv);

-- 1536 dims: `text-embedding-3-large` reduced from its native 3072, because
-- pgvector's HNSW index caps at 2000 for `vector`. Changing this number is a
-- migration plus a full re-embed, not a config tweak (see index/base.py).
create table if not exists embeddings (
    chunk_id text primary key references chunks (id) on delete cascade,
    model    text not null,
    vec      vector(1536) not null
);

-- Cosine, matching `index.base.cosine` and the embedders' normalised output.
create index if not exists embeddings_vec_idx
    on embeddings using hnsw (vec vector_cosine_ops);

-- §5 keys edges (subject, predicate, object). That collides in our model: an
-- edge's subject is usually NULL, meaning "the node holding this edge", so two
-- documents both reporting `mentions -> tools/zendesk` would be one row and the
-- second document would lose its relation. The container is therefore part of
-- the key, and `subject` keeps its resolved value for traversal.
create table if not exists edges (
    container_id  text not null references nodes (id) on delete cascade,
    predicate     text not null,
    subject       text not null,          -- resolved: edge.subject or container_id
    object        text not null,
    raw_subject   text,                   -- NULL when the edge meant its container
    confidence    double precision not null,
    provenance    text not null,
    status        text not null,
    evidence      jsonb not null default '[]'::jsonb,
    primary key (container_id, predicate, subject, object)
);

-- Traversal reads accepted edges in both directions (invariant 10).
create index if not exists edges_subject_idx on edges (subject) where status = 'accepted';
create index if not exists edges_object_idx  on edges (object)  where status = 'accepted';
create index if not exists edges_container_idx on edges (container_id);

-- Lexeme frequencies, rebuilt from the chunk tsvectors. Exists so `stats()` can
-- report a term count as cheaply as the in-memory index does; nothing queries it
-- on a read path.
create table if not exists terms (
    term         text primary key,
    chunk_count  int not null
);
