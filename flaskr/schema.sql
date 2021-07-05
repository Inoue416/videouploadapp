DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS posts;
DROP TABLE IF EXISTS tweets;
DROP TABLE IF EXISTS itas;

CREATE TABLE users (
  id SERIAL NOT NULL,
  i_o INTEGER NOT NULL,
  fit_id TEXT UNIQUE NOT NULL,
  username TEXT NOT NULL,
  password TEXT NOT NULL,
  gender TEXT NOT NULL,
  age INTEGER NOT NULL,
  PRIMARY KEY (id)
);

CREATE TABLE posts (
  author_id INTEGER NOT NULL,
  file_id TEXT NOT NULL,
  gender TEXT NOT NULL,
  age INTEGER NOT NULL,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE tweets (
  id SERIAL NOT NULL,
  file_id TEXT UNIQUE NOT NULL,
  file_title TEXT UNIQUE NOT NULL,
  kana TEXT UNIQUE NOT NULL,
  num INTEGER NOT NULL,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY(id)
);

CREATE TABLE itas (
  id SERIAL NOT NULL,
  file_id TEXT UNIQUE NOT NULL,
  file_title TEXT UNIQUE NOT NULL,
  kana TEXT UNIQUE NOT NULL,
  num INTEGER NOT NULL,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY(id)
);
