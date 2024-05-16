CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username TEXT,
    password TEXT
);

CREATE TABLE admins (
    id SERIAL PRIMARY KEY,
    username TEXT,
    password TEXT
);

CREATE TABLE restaurants (
    id SERIAL PRIMARY KEY,
    name TEXT,
    groups TEXT,
    ratings INTEGER,
    rating REAL,
    des TEXT
);
