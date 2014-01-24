	# from code import interact; interact(local=locals())


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

def getMovieID(moviesDf,movieTitle):
	"""(case doesn't matter nor whether article is at beginning) (finds first movie)
	"""
	movie_lower=movieTitle.lower()
	movie_info=moviesDf[(moviesDf['TitleLower']==movie_lower) | (moviesDf['TitleNoArticleLower']==movie_lower) ]
	if movie_info.empty:
		print '%s not found' % movieTitle
	return movie_info.index[0]


def recommendations(movies_1,movies_2):
	# Create a connection and a cursor object
	db = DbAccess('twolu',usr='root')

	#-------------------------------------------------GET DATA FROM SQL------------------------------------------------------#
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

	#-----------------------------------------FIND MOVIEIDS OF INPUT MOVIES------------------------------------------------------------#
	ITEMIDS1=[getMovieID(moviesDf,movie) for movie in movies_1]
	ITEMIDS2=[getMovieID(moviesDf,movie) for movie in movies_2]

	#-----------------------------------------READ IN SVD AND GET SIMILARITIES-----------------------------------------------------------#	
	#Import SVD from file
	svd2=SVD()
	svd2.load_model('svd-10M-k100') #calculated on 10M rating database, with parameter k=100

	sims=svd2.get_matrix_similarity()

	#------------------------------------------------GET RECOMMENDED MOVIEIDS--------------------------------------------------------------#
	numInput1s=len(ITEMIDS1)
	numInput2s=len(ITEMIDS2)

	ITEMIDS=ITEMIDS1+ITEMIDS2

	numInputs=len(ITEMIDS)

	sims_to_inputs_1=[sims.get_row(i) for i in ITEMIDS1]
	sims_to_inputs_2=[sims.get_row(i) for i in ITEMIDS2]

	sims_to_inputs=[sims.get_row(i) for i in ITEMIDS]

	avg_sims_1=sum(sims_to_inputs_1)/numInput1s
	avg_sims_2=sum(sims_to_inputs_2)/numInput2s


	avg_sims=sum(sims_to_inputs)/numInputs

	diff_sims=abs(avg_sims_1-avg_sims_2)/2

	var_sims=sum([abs(i-avg_sims) for i in sims_to_inputs])/numInputs

	recs_tuples=(avg_sims-0.25*var_sims-0.25*diff_sims).top_items(5,lambda x: ITEMIDS.count(x)==0)

	#------------------------------------------------CONVERT TO TITLES--------------------------------------------------------------#
	recsIDs=[i[0] for i in recs_tuples]

	return moviesDf.Title.loc[recsIDs].tolist()


def main():

	# ITEMIDS1=[1,588,364] #Toy Story,Aladdin,Lion King
	# ITEMIDS2=[1240,589,1200] #Terminator,T2,Aliens
	# ITEMIDS1=[1]
	# ITEMIDS2=[1240]
	movies_1=['Toy Story','Aladdin']
	movies_2=['Terminator','Aliens']

	print recommendations(movies_1,movies_2)

if __name__ == '__main__':
	main()