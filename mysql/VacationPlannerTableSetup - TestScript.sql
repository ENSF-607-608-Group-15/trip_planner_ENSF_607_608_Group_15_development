use n8ic4928wg3p4wnn;

set @qId = NULL;

call AddUser("Poz", "awesomepassword");
-- call AddUser("Poz", "awesomepassword"); # Should get username Invalid

call AddUser("test", "testpassword");

call AddUser("a", "a");

call AddUser("Neos", "this-is-garbage8");

SELECT * FROM users;

call AddQueries('Poz', '2024-10-30', '2024-11-5',  'Calgary', 'All You Can Eats', 'Mexico', 1000, true, false, false, false);
SELECT LAST_INSERT_ID() INTO @qId;

select * from queries;

select passHashMatch("Poz", "awesomepassword");
select passHashMatch("a", "a");

call AddResponse('Poz', @qId, 'I wanna go someplace nice', 'How about hawaii?');

select * from chatgptresponses;

SELECT CONCAT('KILL ', id, ';') 
FROM information_schema.PROCESSLIST 
WHERE user = 'egfwe479rau7ia8z';
