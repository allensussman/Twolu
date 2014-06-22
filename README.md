# Twolu
Twolu is a movie recommender for two people with differing tastes.  Check it out in action at http://www.two-lu.com.

### Dependencies

#### Python

- python-recsys==0.2
- pandas==0.12.0
- rottentomatoes==1.1
- flask==0.10.1
- mysql-connector-python==1.1.4
    
#### Other

- MySQL
    
### To run

1. Install dependencies.
2. Clone repo.
2. Download the [Movielens 10M rating dataset](http://files.grouplens.org/datasets/movielens/ml-10m.zip) and unzip it to `ml-10M100K/` in the repo's top-level directory.
3. In your MySQL client, execute `create_sql_db.sql` to create a SQL database from the dataset.
4. From the cmd line, run `python perform_SVD.py` to perform SVD on the dataset, creating the file `svd-10M-k100.zip` (among others).
5. From the cmd line, run `python twolu.py` to start Twolu on `0.0.0.0:5000`.
6. Go to `0.0.0.0:5000` from your favorite browser.