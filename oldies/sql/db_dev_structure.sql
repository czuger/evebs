DROP DATABASE IF EXISTS eve_business_server_dev;
DROP DATABASE IF EXISTS eve_business_server_test;

DROP USER IF EXISTS eve_business_server;

CREATE USER eve_business_server WITH CREATEDB UNENCRYPTED PASSWORD '123456';

CREATE DATABASE eve_business_server_dev WITH OWNER = eve_business_server;
CREATE DATABASE eve_business_server_test WITH OWNER = eve_business_server;

-- \connect eve_business_server;
--
-- CREATE SCHEMA dev AUTHORIZATION eve_business_server;
-- CREATE SCHEMA test AUTHORIZATION eve_business_server;
