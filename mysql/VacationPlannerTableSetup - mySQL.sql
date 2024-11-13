-- drop database if exists VacationPlannerDB;

-- create database VacationPlannerDB;

-- use VacationPlannerDB;

use n8ic4928wg3p4wnn;

drop table if exists users;
drop table if exists queries;
drop table if exists chatgptresponses;


create table users (
  userId int auto_increment primary key,
  userName varchar(255) not null,
  passHash blob not null,
  CHECK (CHAR_LENGTH(userName) >= 1)
);

create table queries (
  queryId int auto_increment primary key,
  userId int not null references users(userId),
  beginDate date not null,
  endDate date not null,
  departureCity varchar(100) not null,
  tripTheam varchar(4000) not null,
  location varchar(100) not null,
  budget double not null,
  flying boolean not null,
  familyFriendly boolean not null,
  disabilityFriendly boolean not null,
  groupDiscount boolean not null
);

create table chatgptresponses (
  chatGPTresponsesId int auto_increment primary key,
  userId int not null references users(userId),
  `query` varchar(4000) not null,
  response varchar(10000) not null
);


drop FUNCTION if exists passHashMatch;
drop procedure if exists AddQueries;
drop procedure if exists AddResponse;
drop procedure if exists AddUser;
drop procedure if exists DeleteUser;

DELIMITER $$

CREATE FUNCTION passHashMatch(p_userName VARCHAR(255), p_hash VARCHAR(255)) RETURNS BOOLEAN DETERMINISTIC
begin

    declare hasUserName int;
    declare ph blob;
    declare input_passHash blob;
    
    set input_passHash = AES_ENCRYPT(p_hash, p_userName);

	select COUNT(*) into hasUserName from users where userName = p_userName;
    select passHash into ph from users where userName = p_userName;

	IF hasUserName >= 1 AND input_passHash = ph THEN 
		RETURN TRUE;
	ELSE 
		RETURN FALSE;
	end IF;

end$$

CREATE PROCEDURE AddUser (
in p_userName varchar(255),
in p_passHash varchar(255)
)

begin
	declare userExists int;
	declare input_passHash blob;
    
    set input_passHash = AES_ENCRYPT(p_passHash, p_userName);

	select count(*) into userexists from users where username = p_username;
    
    if userExists = 0 then
		insert into users (userName, passHash)
		values (p_userName, input_passHash);
	else
        select 'Username Invalid' as `Error`;
    end if;

end$$

CREATE PROCEDURE DeleteUser (
in p_userName varchar(255)
)

begin
	declare userExists int;
    declare unId int;

	select count(*) into userexists from users where username = p_username;
    select userId into unId from users where userName = p_userName;
    
    if userExists = 1 then
		delete from users where userName = p_userName;
        delete from chatgptresponses where userId = unId;
        delete from queries where userId = unId;
	else
        select 'User does not exist.' as `Error`;
    end if;

end$$

CREATE PROCEDURE AddQueries (
in p_userName varchar(255), 
in p_beginDate date, 
in p_endDate date, 
in p_departureCity varchar(100), 
in p_tripTheam varchar(255),
in p_location varchar(100),
in p_budget double,
in p_flying boolean,
in p_familyFriendly boolean,
in p_disabilityFriendly boolean,
in p_groupDiscount boolean
)

begin

	declare unId int;
    
    select userId into unId from users where userName = p_userName;

    insert into queries (userId, beginDate, endDate, departureCity, tripTheam, location, budget, flying, familyFriendly, disabilityFriendly, groupDiscount)
    values (unId, p_beginDate, p_endDate, p_departureCity, p_tripTheam, p_location, p_budget, p_flying, p_familyFriendly, p_disabilityFriendly, p_groupDiscount);

end$$

CREATE PROCEDURE AddResponse (
in p_userName varchar(255), 
in p_query varchar(4000), 
in p_response varchar(10000)
)

begin

	declare unId int;
    
    select userId into unId from users where userName = p_userName;

    insert into chatgptresponses (userID, `query`, response)
    values (unId, p_query, p_response);
    
end$$

DELIMITER ;