from DbAccess import DbAccess 
import json

def main():
	# Create a connection and a cursor object
	db = DbAccess('twolu',usr='root')

	# get movies
	db.cursor.execute(
	    '''
	    SELECT Title
	    FROM movies
	    ''')

	data = db.cursor.fetchall()
	movieTitleList=[movieTitle[0] for movieTitle in data]
	with open('movieTitles.json','w') as outfile:
		json.dump(movieTitleList,outfile)


if __name__ == '__main__':
	main()