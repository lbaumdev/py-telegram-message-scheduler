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

 not null
);

