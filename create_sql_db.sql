CREATE DATABASE twolu;
CREATE TABLE twolu.movies(MovieID INTEGER,Title TEXT,Genres TEXT);
LOAD DATA LOCAL INFILE '~/Google Drive/Insight/Twolu/repo/ml-10M100K/movies.dat' INTO TABLE twolu.movies FIELDS TERMINATED BY '::';
SELECT * FROM twolu.movies LIMIT 100