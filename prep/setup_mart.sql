DROP DATABASE IF EXISTS mart_flow;
CREATE DATABASE mart_flow;
CREATE TABLE adt (
    pid integer NOT NULL,
    grp VARCHAR (32) NOT NULL,
    duration integer NOT NULL
);
