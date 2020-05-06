select 1 * 2*3*4*5 as summ;

-- В случае, если надо обновить значение id каталога
update catalogs SET id = id + 10

select 3 + NULL; -- result is NULL

select '3'+'5'; -- result is 8

select 'abc' + 'def'; -- result is 0

select 8 / 0; -- result is NULL

select 5 % 2, 5 DIV 2, 5 / 2; -- result is 1, 2, 2.5
select 5 MOD 2; -- result is 1

-- -------------------------------------------------------------

SELECT * FROM catalogs WHERE name IS NULL;
-- -------------------------------------------------------------
CREATE TABLE tbl (
    x INT,
    y INT,
    summ INT AS (x + y) STORED -- then data will be stored in DB

)
-- -------------------------------------------------------------

SELECT * FROM catalogs;

SELECT * FROM catalogs where id > 2;

SELECT * FROM catalogs where id > 2 AND id < 5;

SELECT * FROM catalogs where id BETWEEN 2 AND 5;

SELECT * FROM catalogs where id NOT BETWEEN 2 AND 5;

SELECT * FROM catalogs where id IN (1,2,5);

SELECT * FROM catalogs where id NOT IN (1,2,5);


SELECT * FROM catalogs where name LIKE 'processors';

/*
 LIKE
 % - for or more or NO ONE symbols
 _ - for ONE only symbol
 */


SELECT * FROM catalogs where name LIKE '%s';
SELECT * FROM catalogs where name NOT LIKE '%s';
-- -------------------------------------------------------------
SELECT * FROM vk.profiles WHERE birthday >= '1990-01-01' and birthday < '2000-01-01';

INSERT INTO vk.profiles (
                         gender, birthday, photo_id, created_at, hometown, is_active
)
VALUES (
        'm', '1998 May 20', '1234556', '2020-05-05', 'Moscow', 'True'
       );


SELECT * FROM vk.profiles WHERE birthday BETWEEN LIKE '199%'



SELECT 7 RLIKE '[0-9]', 7 RLIKE '[0123456789]';

SELECT 7 RLIKE '[[:digit:]]', 'hello' RLIKE '[[:digit:]]';

-- -------------------------------------------------------------
SELECT id, catalog_id, price, name products ORDER BY catalog_id, price;

SELECT id, catalog_id, price, name products ORDER BY catalog_id DESC, price DESC;


SELECT id, catalog_id, price, name products LIMIT 2; -- id 1 and id 2
SELECT id, catalog_id, price, name products LIMIT 2, 2; -- id 3 and id 4
SELECT id, catalog_id, price, name products LIMIT 4, 2; -- id 5 nad id 6
-- -------------------------------------------------------------


SELECT DISTINCT catalog_id from products;

-- -------------------------------------------------------------
SELECT id, catalog_id, price, name FROM products WHERE catalog_id = 2 AND price > 5000;
UPDATE products SET price = price * 0,9 WHERE catalog_id = 2 AND price > 5000;

DELETE FROM products ORDER BY price DESC LIMIT 2;
-- -------------------------------------------------------------



