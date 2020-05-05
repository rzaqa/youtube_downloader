DROP TABLE IF EXISTS news;
CREATE TABLE news(
    news_id BIGINT UNSIGNED NOT NULL PRIMARY KEY,
    new_news TEXT
);

DROP TABLE IF EXISTS user_news;
CREATE TABLE user_news(
    user_id BIGINT UNSIGNED NOT NULL,
    news_id BIGINT UNSIGNED NOT NULL,

    FOREIGN KEY (news_id) REFERENCES news(news_id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

DROP TABLE IF EXISTS music;
CREATE TABLE music(
    id SERIAL primary key,
    user_id BIGINT UNSIGNED NOT NULL,
    media_type_id BIGINT UNSIGNED NOT NULL,
    music_file BLOB,

    FOREIGN KEY (media_type_id) REFERENCES media(media_type_id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

