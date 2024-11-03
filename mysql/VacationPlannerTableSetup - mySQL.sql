-- drop database if exists VacationPlannerDB;

-- create database VacationPlannerDB;

-- use VacationPlannerDB;

drop table if exists uers;
drop table if exists queries;
drop table if exists chatgptresponses;


create table users (
  userId int auto_increment primary key,
  userName varchar(255) not null,
  passHash varchar(255) not null
);

-- drop table if exists userqueries;
-- create table userqueries (
--   queryId int primary key references queries(queryId),
--   userId int not null references users(userId)
-- );

create table queries (
  queryId int auto_increment primary key,
  userId int not null references users(userId),
  beginDate date not null,
  endDate date not null,
  departureCity varchar(100) not null,
  tripTheam varchar(255) not null,
  location varchar(100) not null,
  budget double not null,
  flying boolean not null,
  familyFriendly boolean not null,
  disabilityFriendly boolean not null,
  pdfOutput boolean not null,
  groupDiscount boolean not null
);

-- drop table if exists queryResponses;
-- create table queryresponses (
--   chatGPTresponsesId int primary key references chatgptresponses(chatGPTresponsesId),
--   queryId int not null references queries(queryId)
-- );

create table chatgptresponses (
  chatGPTresponsesId int auto_increment primary key,
  userId int not null references users(userId),
  queryId int not null references queries(queryId),
  `query` varchar(4000) not null,
  response varchar(10000) not null
);


drop FUNCTION if exists passHashMatch;
DELIMITER $$

CREATE FUNCTION passHashMatch(p_userName VARCHAR(255), p_hash VARCHAR(255)) RETURNS BOOLEAN DETERMinISTIC
begin

    declare hasUserName int;
    declare ph VARCHAR(255);

	select COUNT(*) into hasUserName from Users where userName = p_userName;
    select passHash into ph from Users where userName = p_userName;

	IF hasUserName >= 1 AND p_hash = ph THEN 
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

	select count(*) into userexists from users where username = p_username;
    
    if userExists = 0 then
		insert into users (userName, passHash)
		values (p_userName, p_passHash);
	else
        select 'Username Invalid' as `Error`;
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
in p_pdfOutput boolean,
in p_groupDiscount boolean
)

begin

	declare unId int;
    declare queryid int;
    
    select userId into unId from users where userName = p_userName;

    insert into queries (userId, beginDate, endDate, departureCity, tripTheam, location, budget, flying, familyFriendly, disabilityFriendly, pdfOutput, groupDiscount)
    values (unId, p_beginDate, p_endDate, p_departureCity, p_tripTheam, p_location, p_budget, p_flying, p_familyFriendly, p_disabilityFriendly, p_pdfOutput, p_groupDiscount);
    
    set queryid = last_insert_id();

    select queryid;

end$$

CREATE PROCEDURE AddResponse (
in p_userName varchar(255), 
in p_queryId int,
in p_query varchar(4000), 
in p_response varchar(10000)
)

begin

	declare unId int;
    
    select userId into unId from users where userName = p_userName;

    insert into chatGPTresponses (userID, queryId, `query`, response)
    values (unId, p_queryId, p_query, p_response);
    
end$$

DELIMITER ;