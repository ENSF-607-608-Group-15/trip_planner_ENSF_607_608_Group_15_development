-- use VacationPlannerDB;

use n8ic4928wg3p4wnn;

# Tests adding user and error if user exists
call AddUser("Poz", "awesomepassword");
call AddUser("Poz", "awesomepassword"); # Should get username Invalid
call AddQueries('Poz', '2024-10-30', '2024-11-5',  'Calgary', 'All You Can Eats', 'Mexico', 1000, true, false, false, false);
call AddResponse('Poz', 'I wanna go someplace nice', 'How about hawaii?');

# Tests deleting user, and error if tring to delete a non existing user
call DeleteUser("Poz");
select * from users;
select count(*) as userexists from users where userName = 'Poz';
call DeleteUser("NotAUsername");

#Testing pashHashMatch function when user does not exist
select passHashMatch("Poz", "awesomepassword"); # Should get false

# Adding initial users for db.
call AddUser("Poz", "awesomepassword");
call AddUser("test", "testpassword");
call AddUser("a", "a");
call AddUser("Neos", "this-is-garbage8");

# Testing to ensure passHashMatch works as expected.
select passHashMatch("Poz", "awesomepassword"); # Should get true

# Should have 4 users as above.
SELECT * FROM users; 

# Testing adding queries, extra queries for following SQL quries.
call AddQueries('Poz', '2024-10-30', '2024-11-5',  'Calgary', 'All You Can Eats', 'Mexico', 1000, true, false, false, false);
call AddQueries('Poz', '2024-10-30', '2024-11-5',  'Calgary', 'All You Can Eats', 'Mexico', 1000, true, false, false, false);
call AddQueries('Poz', '2024-10-30', '2024-11-5',  'Calgary', 'All You Can Eats', 'Mexico', 1000, true, false, false, false);

select * from queries; # Should show lines as above.

# Testing adding responses, extra responses for following SQL quries.
call AddResponse('Poz', 'I wanna go someplace nice', 'How about hawaii?');
call AddResponse('Poz', 'I wanna go someplace nice', 'How about hawaii?');
call AddResponse('Poz', 'I wanna go someplace nice', 'How about hawaii?');

select * from chatgptresponses; # Should show lines as above.

# This is a table that joins all of the three tables into one large one. Due to poor normalization, there is a lot of redundent information.
select * from users as u
left join queries as q on u.userId = q.userId
left join chatgptresponses as r on u.userId = r.userId
order by u.userId, q.queryId, r.chatGPTresponsesId;

# Testing to ensure passwords are hashed.
select HEX(passHash) as "Password Hash" from users;

call DeleteUser("Poz");
SELECT * FROM vacationplannerdb.users; # Poz should be missing
SELECT * FROM vacationplannerdb.chatgptresponses; # Should be void of user Poz responses
SELECT * FROM vacationplannerdb.queries; # Should be void of user Poz quries
call AddUser("Poz", "awesomepassword");

# Find Users with No Queries
select u.userId, u.userName 
from users u 
left join queries q on u.userId = q.userId 
where q.queryId is null;

# Count of ChatGPT Responses Provided for Each User
select u.userName, count(c.chatGPTresponsesId) as responseCount
from users u
left join chatgptresponses c on u.userId = c.userId
group by u.userName;

# Userid and their reponse ids
select u.userName, u.userId, c.chatGPTresponsesId
from users as u
left join chatgptresponses as c on c.userId = u.userId;

# Userid and their query id
select u.userName, u.userId, q.queryId
from users as u
left join queries as q on u.userId = q.userId;






