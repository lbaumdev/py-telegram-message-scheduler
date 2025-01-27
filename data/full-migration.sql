create table if not exists chats
(
    id               integer not null
        constraint chats_pk
            primary key autoincrement,
    title            text,
    adder_id         text    not null,
    created_at       integer not null,
    telegram_chat_id text    not null
);

create table if not exists jobs
(
    id             integer not null
        constraint jobs_pk
            primary key autoincrement,
    name           text    not null,
    schedule       text    not null,
    owner_id       text    not null,
    message        text    not null,
    created_at     integer not null,
    updated_at     integer not null,
    target_chat_id text    not null
        constraint jobs_chats_id_fk
            references chats
);

-- 2025-01-27
alter table jobs
    add owner_chat_id text;


