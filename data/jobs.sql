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
            references chats,
    owner_chat_id  text
);

