-- CRUD Insert Select Update Delete

use vk;

INSERT INTO vk.users (id, firstname, lastname, email, phone)
values(1, 'Nikola', 'Tesla', 'test@gmail.com', '9125756233' );

INSERT INTO vk.users (id, firstname, lastname, email, phone)
values(4, 'Sonya', 'Tesla', 'test+sonya@gmail.com', '129125756233');



-- IGNORE key word helps skip error message during running a script in case
-- of duplicating data
use vk;
INSERT IGNORE INTO vk.users (id, firstname, lastname, email, phone)
values(2, 'Nikola', 'Tesla', 'test+1@gmail.com', '9125756235' );



-- without id, because it has autoincrement
use vk;
INSERT INTO vk.users (firstname, lastname, email, phone)
values('Nikola', 'Tesla', 'test@gmail.com', '9125756233' );


-- without id, because it has autoincrement
use vk;
INSERT INTO vk.users (firstname, lastname, email, phone)
values('Nikola1', 'Tesla1', 'test+3@gmail.com', NULL );


use vk;
INSERT INTO vk.users
values(6, 'Nikola2', 'Tesla2', 'test+4@gmail.com',NULL,NULL );



-- insert several rows of data - quick version
use vk;
INSERT INTO vk.users (id, firstname, lastname, email,password_hash, phone)
values
(14, 'Nikola14', 'Tesla14', 'test+14@gmail.com', NULL, '90123123463'),
(12, 'Nikola12', 'Tesla12', 'test+12@gmail.com', NULL, '90123123461'),
(9, 'Nikola5', 'Tesla5', 'test+7@gmail.com', NULL, '90123123458');


-- Using the SET command ONLY FOR ONE row
use vk;
INSERT INTO vk.users
SET
firstname = 'Nikolay',
lastname = 'Suvorov',
email = 'test+15@gmail.com',
password_hash = NULL,
phone = NULL;


use vk;
INSERT INTO vk.users
SET
firstname = 'Nikolay',
lastname = 'Suvorov',
email = 'test+16@gmail.com',
password_hash = NULL,
phone = NULL;


-- INSERT with SELECT command
use vk;
INSERT INTO vk.users (id, firstname, lastname, email,password_hash, phone)
SELECT
18, 'Tolik', 'Vaclav', 'test+18@gmail.com', NULL, '90123123464';

-- --------------------------------------------
select * from users;

select distinct firstname from users;

select * from vk.users LIMIT 10;

-- for pagination
select * from vk.users LIMIT 6 offset 5;
select * from vk.users LIMIT 6 offset 10;
select * from vk.users LIMIT 6 offset 5;
select * from vk.users LIMIT 6 offset 0;



-- ---------------------

INSERT INTO friend_requests (initiator_user_id, target_user_id, status)
values ('1', '3', 'requested');

INSERT INTO friend_requests (initiator_user_id, target_user_id, status)
values ('1', '4', 'requested');

INSERT INTO friend_requests (initiator_user_id, target_user_id, status)
values ('1', '5', 'requested');

INSERT INTO friend_requests (initiator_user_id, target_user_id, status)
values ('1', '6', 'requested');

-- --------------------------------------------------------------------
update friend_requests
set status = 'approved'
where initiator_user_id = 1 and target_user_id = 2;

-- --------------------------------------------------------------------





















