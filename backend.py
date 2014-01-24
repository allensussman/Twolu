from recsys.algorithm.factorize import SVD
import numpy as np
import pandas as pd
from DbAccess import DbAccess

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


def makeMoviesTable(db):
	"""return the movieIDs and titles in db.movies as a dataframe with index movieID and columns which are the title in various formats
	"""
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


def getMovieInfo(movieDf,movie_title):
	"""get info of movie_title in movieDf
	"""
	movie_lower=movie_title.lower()
	movie_info=moviesDf[(moviesDf['TitleLower']==movie_lower) | (moviesDf['TitleNoArticleLower']==movie_lower) ]
	if movie_info.empty:
		print '%s not found' % movie_title

def recommendations(movie_1,movie_2):
	#make lowercase versions
	first_movie_lower=movie_1.lower()
	second_movie_lower=movie_2.lower()

	# Create a connection and a cursor object
	db = DbAccess('twolu100K',usr='root')

	moviesDf=getMoviesTable(db)

	ITEMIDS1=

	# #-----------------------------------------FIND MOVIEIDS OF INPUT MOVIES------------------------------------------------------------#
	# #(case doesn't matter nor whether article is at beginning) (finds first movie)  return -1 or -2 if input movies not found
	# first_movie_info=moviesDf[(moviesDf['TitleLower']==first_movie_lower) | (moviesDf['TitleNoArticleLower']==first_movie_lower) ]
	# if first_movie_info.empty:
	# 	return -1
	# ITEMIDS1=[first_movie_info.index[0]]
	# second_movie_info=moviesDf[(moviesDf['TitleLower']==second_movie_lower) | (moviesDf['TitleNoArticleLower']==second_movie_lower) ]
	# if second_movie_info.empty:
	# 	return -2
	# ITEMIDS2=[second_movie_info.index[0]]

	#Import SVD from file
	svd2=SVD()
	svd2.load_model('svd-10M-k100') #calculated on 10M rating database, with parameter k=100

	sims=svd2.get_matrix_similarity()

	numInput1s=len(ITEMIDS1)
	numInput2s=len(ITEMIDS2)

	ITEMIDS=ITEMIDS1+ITEMIDS2

	numInputs=len(ITEMIDS)
	# print numInputs

	sims_to_inputs_1=[sims.get_row(i) for i in ITEMIDS1]
	sims_to_inputs_2=[sims.get_row(i) for i in ITEMIDS2]

	sims_to_inputs=[sims.get_row(i) for i in ITEMIDS]
	# print sims_to_inputs

	avg_sims_1=sum(sims_to_inputs_1)/numInput1s
	avg_sims_2=sum(sims_to_inputs_2)/numInput2s


	avg_sims=sum(sims_to_inputs)/numInputs
	# print avg_sims

	diff_sims=abs(avg_sims_1-avg_sims_2)/2
	print diff_sims

	var_sims=sum([abs(i-avg_sims) for i in sims_to_inputs])/numInputs
	# print var_sims


	recs_tuples=(avg_sims-0.25*var_sims-0.25*diff_sims).top_items(5,lambda x: ITEMIDS.count(x)==0)
	return [i[0] for i in recs_tuples]

def main():

	# ITEMIDS1=[1,588,364] #Toy Story,Aladdin,Lion King
	# ITEMIDS2=[1240,589,1200] #Terminator,T2,Aliens
	# ITEMIDS1=[1]
	# ITEMIDS2=[1240]
	movie_1='Toy Story'
	movie_2='Terminator'


	return recommendations(movie_1,movie_2)

if __name__ == '__main__':
	main()