# Finds the recommendations for two people who want to watch two sets of movies.  Also finds the rotten tomatoes URLs for the posters and movie info.

from recsys.algorithm.factorize import SVD
import pandas as pd
from DbAccess import DbAccess
from rottentomatoes import RT
from time import time


def createMovieIDTitleDataFrame(database):
	""" Returns pandas DataFrame of movie IDs and titles (in various forms) from database
	"""
	# Create a connection and a cursor object
	db = DbAccess(database,usr='root')

	#-------------------------------------------------------GET DATA FROM SQL-----------------------------------------------------------#
	# get movies
	db.cursor.execute(
	    '''
	    SELECT MovieID,Title
	    FROM movies
	    ''')

	data = db.cursor.fetchall()

	moviesDf=pd.DataFrame.from_records(data,index='MovieID',columns=['MovieID','TitleWithYear'])

	#-----------------------------------------------------MASSAGE MOVIE DATA------------------------------------------------------------#
	#remove year and alternate spellings
	moviesDf['TitleArticleAtEnd']=moviesDf['TitleWithYear'].apply(lambda x: x.split(' (')[0])

	#make column where articles (a, an, the...) are at beginning
	moviesDf['Title']=moviesDf['TitleArticleAtEnd'].apply(moveArticle)

	#make column with initial articles removed
	moviesDf['TitleNoArticle']=moviesDf['TitleArticleAtEnd'].apply(removeArticle)

	# make everything lower case so I can do case insensitive search
	moviesDf['TitleLower']=moviesDf['Title'].apply(lowerCase)
	moviesDf['TitleNoArticleLower']=moviesDf['TitleNoArticle'].apply(lowerCase)

	return moviesDf

#move article in movie title from end to beginning
def moveArticle(x):
    if x.endswith(', The'):
        return 'The ' + x.split(', The')[0]
    elif x.endswith(', A'):
        return 'A ' + x.split(', A')[0]
    elif x.endswith(', An'):
        return 'An ' + x.split(', An')[0]
    elif x.endswith(', Il'):
        return 'Il ' + x.split(', Il')[0]
    elif x.endswith(', Das'):
        return 'Das ' + x.split(', Das')[0]

    return x

#remove article from movie title
def removeArticle(x):
    if x.endswith(', The'):
        return x.split(', The')[0]
    if x.endswith(', A'):
        return x.split(', A')[0]
    if x.endswith(', An'):
        return x.split(', An')[0]
    if x.endswith(', Il'):
        return x.split(', Il')[0]
    if x.endswith(', Das'):
        return x.split(', Das')[0]
    return x

#change string to lower case
def lowerCase(x):
    return x.lower()

def getMovieID(moviesDf,movieTitle):
	""" Returns movieID of movieTitle in the dataframe moviesDf
	(case doesn't matter nor whether article is at beginning) (finds first movie)
	"""
	movie_lower=movieTitle.lower()
	movie_info=moviesDf[(moviesDf['TitleLower']==movie_lower) | (moviesDf['TitleNoArticleLower']==movie_lower) | (moviesDf['TitleWithYear']==movieTitle)]
	if movie_info.empty:
		print '%s not found' % movieTitle
	return movie_info.index[0] #TO DO: returns first movie that matches. but this is not always the right one.  Fix this.

def getSimilarityMatrix(svd_model_file):
	""" Returns similarity matrix from svd_model_file
	"""
	#Import SVD from file
	svd=SVD()
	svd.load_model(svd_model_file)

	return svd.get_matrix_similarity()

def getRecMovieIDs(InputIDs1,InputIDs2,sims):
	"""
	Returns IDs of recommended movies
	InputIDs1: list (!) of IDs of movies user 1 wants to watch
	InputIDs2: list (!) of IDs of movies user 2 wants to watch
	sims: movie similarity matrix
	"""

	numInput1s=len(InputIDs1)
	numInput2s=len(InputIDs2)

	InputIDs=InputIDs1+InputIDs2

	numInputs=len(InputIDs)


	sims_to_inputs_1=[sims.get_row(i) for i in InputIDs1]
	sims_to_inputs_2=[sims.get_row(i) for i in InputIDs2]

	sims_to_inputs=[sims.get_row(i) for i in InputIDs]

	avg_sims_1=sum(sims_to_inputs_1)/numInput1s
	avg_sims_2=sum(sims_to_inputs_2)/numInput2s


	avg_sims=sum(sims_to_inputs)/numInputs

	diff_sims=abs(avg_sims_1-avg_sims_2)/2

	# this is sort of like variance in similarities to the inputs
	var_sims=sum([abs(i-avg_sims) for i in sims_to_inputs])/numInputs

	# (avg_sim-0.25*var_sim-0.25*diff_sims) is my proxy for how good of a mutual recommendation a movie is
	# get the 5 items which maximize this, and are not one of the input movies 
	recs_tuples=(avg_sims-0.25*var_sims-0.25*diff_sims).top_items(5,lambda x: InputIDs.count(x)==0) 

	return [i[0] for i in recs_tuples]

def getPosterUrl(movieTitle,rt):
	return rt.search(movieTitle)[0]['posters']['original']

def backend(movieTitles1,movieTitles2,database,svd_model_file):
	""" Returns recommended movies for two people
	movieTitles1: list (!) of movies person 1 wants to watch
	movieTitles2: list (!) of movies person 2 wants to watch
	"""

	#-----------------------------------------CREATE MOVIE ID AND TITLES DATAFRAME-----------------------------------------------------------#
	moviesDf=createMovieIDTitleDataFrame(database)

	#-----------------------------------------FIND MOVIEIDS OF INPUT MOVIES------------------------------------------------------------#
	# TO DO: Fix handling of not finding a movie
	ITEMIDS1=[getMovieID(moviesDf,movie) for movie in movieTitles1]
	ITEMIDS2=[getMovieID(moviesDf,movie) for movie in movieTitles2]

	#-------------------------------------------------GET SIMILARITIES-----------------------------------------------------------------#	
	sims=getSimilarityMatrix(svd_model_file)

	#------------------------------------------------GET RECOMMENDED MOVIEIDS--------------------------------------------------------------#
	recsIDs = getRecMovieIDs(ITEMIDS1,ITEMIDS2,sims)

	#------------------------------------------------CONVERT TO TITLES--------------------------------------------------------------#
	recTitles=moviesDf.Title.loc[recsIDs].tolist()

	#------------------------------------------------GET POSTER URLS--------------------------------------------------------------#
	rt=RT()

	recMoviesInfo=[rt.search(title)[0] for title in recTitles]
	posterUrls=[movie['posters']['original'] for movie in recMoviesInfo]
	movieUrls=[movie['links']['alternate'] for movie in recMoviesInfo]
	
	#------------------------------------------------RETURN--------------------------------------------------------------#

	return zip(recTitles,posterUrls,movieUrls)

def main():
	movies_1=['Toy Story','Aladdin']
	movies_2=['Terminator','Aliens']
	database='twolu'
	svd_model_file='svd-10M-k100'

	print backend(movies_1,movies_2,database,svd_model_file)

if __name__ == '__main__':
	main()