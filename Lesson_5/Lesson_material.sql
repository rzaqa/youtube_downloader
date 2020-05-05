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














