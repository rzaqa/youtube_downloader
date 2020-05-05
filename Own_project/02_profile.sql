-- Эта таблица сохраняет данные профиля пользователя
-- фотография, адрес доставки, id пользователя

use test_cult;

DROP TABLE IF EXISTS profile;
CREATE TABLE profile (
    id SERIAL,
    user_id BIGINT UNSIGNED NOT NULL,   -- foreign key
    photo_link BIGINT UNSIGNED NULL,
    address BIGINT UNSIGNED NULL,

    FOREIGN KEY (user_id) REFERENCES users(id)
);