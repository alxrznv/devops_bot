CREATE USER repluser REPLICATION LOGIN PASSWORD 'replpassword';
ALTER USER dbuser WITH PASSWORD 'dbpassword';
CREATE DATABASE dbdatabase;
GRANT ALL PRIVILEGES ON DATABASE dbdatabase TO dbuser;

\c dbdatabase;

CREATE TABLE IF NOT EXISTS phones (
    id SERIAL PRIMARY KEY,
    phone VARCHAR(20) NOT NULL
);

CREATE TABLE IF NOT EXISTS emails (
    id SERIAL PRIMARY KEY,
    email VARCHAR(100) NOT NULL
);

INSERT INTO emails (email) VALUES ('test@w.ru');
INSERT INTO phones (phone) VALUES ('80000000000');
