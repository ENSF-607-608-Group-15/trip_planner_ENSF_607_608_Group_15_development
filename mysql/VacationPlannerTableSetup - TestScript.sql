-- use users;

set @qId = NULL;

call AddUser("Poz", "awesomepassword");
-- call AddUser("Poz", "awesomepassword"); # Should get username Invalid

call AddUser("test", "testpassword");

SELECT * FROM users;

call AddQueries('Poz', '2024-10-30', '2024-11-5',  'Calgary', 'All You Can Eats', 'Mexico', 1000, true, false, false, false, false);
SELECT LAST_INSERT_ID() INTO @qId;

select * from queries;

select passHashMatch("Poz", "awesomepassword");

call AddResponse('Poz', @qId, 'I wanna go someplace nice', 'How about hawaii?');

select * from chatgptresponses;


