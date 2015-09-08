CREATE USER eve_business_server WITH CREATEDB UNENCRYPTED PASSWORD '123456';

CREATE DATABASE eve_business_server WITH OWNER = eve_business_server;

\connect eve_business_server;

CREATE SCHEMA dev AUTHORIZATION eve_business_server;
CREATE SCHEMA test AUTHORIZATION eve_business_server;
