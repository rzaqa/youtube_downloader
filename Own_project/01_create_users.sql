-- таблица хранящая основную информацию о пользователях

drop database if exists test_cult;
create database test_cult;
use test_cult;

drop table if exists users;
create table users (
    id SERIAL primary key, -- bigint unsigned not null auto_increment unique
    firstname VARCHAR(100),
    lastname VARCHAR(100),
    email VARCHAR(100) UNIQUE, -- will be created index for email UNIQUE
    password_hash VARCHAR(100),
    seller CHAR(1),
    buyer CHAR(1),
    administrator CHAR (1),
    created_at DATETIME default NOW(),
    updated_at DATETIME ON UPDATE NOW(),

    index users_firstname_lastname_idx(firstname, lastname)
);