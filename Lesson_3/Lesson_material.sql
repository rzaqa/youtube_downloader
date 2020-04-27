drop database if exists vk;
create database vk;
use vk;

drop table if exists users;
create table users (
    id SERIAL primary key, -- bigint unsigned not null auto_increment unique
    firstname VARCHAR(100),
    lastname VARCHAR(100),
    email VARCHAR(100) UNIQUE, -- делаем уникальным адрес, избежать повторной регистрации
    password_hash VARCHAR(100),
    phone BIGINT UNSIGNED UNIQUE, -- делаем уникальным номер телефона, избежать повторной регистрации

    index(phone),
    index users_firstname_lastname_idx(firstname, lastname)
);

-- 1 x 1
drop table if exists profiles;
CREATE table profiles(
    user_id SERIAL primary key,
    gender CHAR(1),
    birthday DATE,
    photo_id BIGINT UNSIGNED NULL,
    hometown VARCHAR(100),
    created_at DATETIME default NOW()
)

alter table profiles
add constraint fk_user_id
foreign key(user_id) references users(id)
ON UPDATE CASCADE
ON DELETE restrict;

drop table if exists messages;
CREATE table messages(
    id SERIAL primary key,
    from_user_id bigint unsigned not null,
    to_user_id bigint unsigned not null,
    body TEXT,
    created_at DATETIME default NOW(),
    FOREIGN KEY (from_user_id) references users (id),
    FOREIGN KEY ( to_user_id) references users (id)
);

DROP TABLE IF EXISTS friend_requests;
CREATE TABLE friend_requests(
    initiator_user_id BIGINT UNSIGNED NOT NULL,
    target_user_id BIGINT UNSIGNED NOT NULL,
    `status` enum('requested', 'approved', 'unfriended', 'declined'),
    `created_at` DATETIME default NOW(),
    updated_at DATETIME ON UPDATE NOW(),

    PRIMARY KEY (initiator_user_id, target_user_id),
    FOREIGN KEY (initiator_user_id) references users (id),
    FOREIGN KEY ( target_user_id) references users (id)
);

drop table if exists comminities;
CREATE table comminities(
    id SERIAL primary key,
    name VARCHAR(100),
    admin_user_id BIGINT UNSIGNED NOT NULL,

    FOREIGN KEY ( admin_user_id) references users (id)
);

drop table if exists users_comminities;
CREATE table users_comminities(
    user_id BIGINT UNSIGNED NOT NULL,
    community_id BIGINT UNSIGNED NOT NULL,

    PRIMARY KEY (user_id, community_id),
    FOREIGN KEY (user_id) references users (id),
    FOREIGN KEY (community_id) references comminities (id)
);

DROP TABLE IF EXISTS media_types;
CREATE TABLE media_types(
    id SERIAL primary key,
    name VARCHAR(100)
);

DROP TABLE IF EXISTS media;
CREATE TABLE media(
    id SERIAL primary key,
    user_id BIGINT UNSIGNED NOT NULL,
    media_type_id BIGINT UNSIGNED NOT NULL,
    body TEXT,
    filename VARCHAR(255),
    `size` INT,
    metadata JSON,

    FOREIGN KEY(user_id) references users(id),
    FOREIGN KEY(media_type_id) references media_types(id)
)

DROP TABLE IF EXISTS likes;
CREATE TABLE likes(
    id SERIAL primary key,
    user_id BIGINT UNSIGNED NOT NULL,
    media_id BIGINT UNSIGNED NOT NULL,
    `created_at` DATETIME default NOW(),
    FOREIGN KEY (media_id) REFERENCES media(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
)


DROP TABLE IF EXISTS photo_albums;
CREATE TABLE photo_albums(
    id SERIAL,
    name VARCHAR(100) DEFAULT NULL,
    user_id BIGINT UNSIGNED NOT NULL,

    FOREIGN KEY (user_id) REFERENCES users(id),
    PRIMARY KEY (id)
);

DROP TABLE IF EXISTS photos;
CREATE TABLE photos(
    id SERIAL PRIMARY KEY ,
    album_id BIGINT UNSIGNED NULL,
    media_id BIGINT UNSIGNED NOT NULL,

    FOREIGN KEY (album_id) REFERENCES photo_albums(id),
    FOREIGN KEY (media_id) REFERENCES media(id)

);

