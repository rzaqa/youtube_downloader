-- Задание 1 - Заполнить все таблицы БД vk данными (по 10-100 записей в каждой таблице)
-- файл для наполнения БД приложен к ДЗ - fulldb-vk-04-05-2020.sql


-- Задание 2 - Написать скрипт, возвращающий список имен (только firstname)
-- пользователей без повторений в алфавитном порядке

use vk;
SELECT distinct firstname from users;



-- Задание 3 - Написать скрипт, отмечающий несовершеннолетних пользователей как
-- неактивных (поле is_active = false). Предварительно добавить такое поле в
-- таблицу profiles со значением по умолчанию = true (или 1)

ALTER TABLE vk.profiles ADD COLUMN is_active ENUM('true', 'false') DEFAULT 'true';

UPDATE vk.profiles
SET is_active='false'
WHERE (
    SELECT
  (
    (YEAR(CURRENT_DATE) - YEAR(birthday)) -
    (DATE_FORMAT(CURRENT_DATE, '%m%d') < DATE_FORMAT(birthday, '%m%d'))
  ) AS age FROM profiles);






-- ALTER TABLE vk.profiles DROP COLUMN is_active;



-- Задание 4 - Написать скрипт, удаляющий сообщения «из будущего» (дата больше сегодняшней)




-- Задание 5 - Написать название темы курсового проекта (в комментарии)




