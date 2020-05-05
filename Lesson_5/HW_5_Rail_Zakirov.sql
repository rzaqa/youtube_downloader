/*
 Задание 1 - Пусть в таблице users поля created_at и updated_at оказались незаполненными.
 Заполните их текущими датой и временем.
*/
-- вспомогательные запросы для подготовки таблицы
/*ALTER TABLE vk.users DROP COLUMN created_at;
ALTER TABLE vk.users DROP COLUMN updated_at;
ALTER TABLE vk.users ADD COLUMN created_at DATETIME;
ALTER TABLE vk.users ADD COLUMN updated_at DATETIME;
*/
UPDATE vk.users SET created_at = now() where users.created_at IS NULL;
UPDATE vk.users SET updated_at = now() where users.updated_at IS NULL;



/*
Задание 2 - Таблица users была неудачно спроектирована. Записи created_at и updated_at
были заданы типом VARCHAR и в них долгое время помещались значения в
формате "20.10.2017 8:10". Необходимо преобразовать поля к типу DATETIME,
сохранив введеные ранее значения.
*/

-- певрый вариант, не совсем в нем уверен, когда напрямую менять формат данных
ALTER TABLE vk.users MODIFY created_at DATETIME;
ALTER TABLE vk.users MODIFY updated_at DATETIME;

-- второй способ, который я нагуглил, но у меня выполняется с ошибкой. Почему, может подскажете?
ALTER TABLE users ADD COLUMN created_at_2 DATETIME;
ALTER TABLE users ADD COLUMN updated_at_2 DATETIME;

UPDATE vk.users
SET created_at_2 = STR_TO_DATE(created_at,'YYYY-MM-DD hh:mm:ss');
UPDATE vk.users
SET updated_at_2 = STR_TO_DATE(updated_at,'YYYY-MM-DD hh:mm:ss');

ALTER TABLE users
DROP created_at, DROP updated_at,
RENAME COLUMN created_at_2 TO created_at, RENAME COLUMN updated_at_2 TO updated_at;

/*
Задание 3 - В таблице складских запасов storehouses_products в поле value могут встречаться
самые разные цифры: 0, если товар закончился и выше нуля, если на складе имеются
запасы. Необходимо отсортировать записи таким образом, чтобы они выводились в порядке
увеличения значения value. Однако, нулевые запасы должны выводиться в конце, после всех записей.
*/




/*
Задание 4 - (по желанию) Из таблицы users необходимо извлечь пользователей, родившихся в августе и мае.
Месяцы заданы в виде списка английских названий ('may', 'august')
 */

SELECT * FROM users WHERE birthday LIKE '%may%' OR birthday LIKE '%august%';



/*
Задание 5 - (по желанию) Из таблицы catalogs извлекаются записи при помощи запроса.
SELECT * FROM catalogs WHERE id IN (5, 1, 2);
Отсортируйте записи в порядке, заданном в списке IN.
 */




/*
Задание 6 - Подсчитайте средний возраст пользователей в таблице users
 */


/*
Задание 7 - Подсчитайте количество дней рождения, которые приходятся на каждый из дней недели.
Следует учесть, что необходимы дни недели текущего года, а не года рождения.
 */




/*
 Задание 8 - (по желанию) Подсчитайте произведение чисел в столбце таблицы
 value
 1
 2
 3
 4
 5
 */
SELECT 1 * 2 * 3 * 4 * 5 as summ_values;



