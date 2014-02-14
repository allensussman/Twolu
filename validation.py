from DbAccess import DbAccess
import pandas as pd
import time
import recsys.algorithm
recsys.algorithm.VERBOSE = True
from recsys.utils.svdlibc import SVDLIBC
from  sklearn.cross_validation import KFold
import backend as be

def createValidationSets(database,nTrainingTestFolds,nFeaturesTruthFolds):
	#-----------------------------------GET RATINGS DATA FROM SQL, PUT IT IN RIGHT FORMAT----------------------------------------------#
	ratingsDfpivoted=getRatings(database)

	#------------------------------CREATE NTRAININGTESTFOLDS TRAINING AND TEST SETS DIVIED BY USER---------------------------------------#
	[ratingsInTrain,ratingsInTest]=createTrainingTestSets(ratingsDfpivoted,nTrainingTestFolds)

	#---------------------------------CREATE NFEATURESTRUTHFOLDS FEATURES AND TRUTH FOR EVERY TEST SET--------------------------------------#
	[ratingsInFeatures, ratingsInTruth] = createFeaturesTruthSets(ratingsInTest,nFeaturesTruthFolds)

	#------------------------------------------------WRITE EVERYTHING TO FILES----------------------------------------------------------#
	writeSetsToFiles(ratingsInTrain,ratingsInTest,ratingsInFeatures,ratingsInTruth)

	return [ratingsInFeatures,ratingsInTruth]

def getRatings(database):
	""" Gets userID, movieID, and rating information from database, returns as a pivoted dataframe
	"""
	# Create a connection and a cursor object
	db = DbAccess(database,usr='root')

	start=time.time()
	db.cursor.execute(
	    '''
	    SELECT UserID,MovieID,Rating
	    FROM ratings;
	    ''')
	end=time.time()
	elapsed=end-start
	print "elapsed time for SQL query = ",elapsed

	start=time.time()
	data = db.cursor.fetchall()
	end=time.time()
	elapsed=end-start
	print "elapsed time for fetchall = ",elapsed

	start=time.time()
	ratingsDf=pd.DataFrame.from_records(data,columns=['userID','movieID','ratings'])
	end=time.time()
	elapsed=end-start
	print "elapsed time for making dataframe = ",elapsed

	# changed from:
	# return ratingsDf.pivot('userID','movieID','ratings')
	# because that didn't work for the 10M-rating dataset (gave an error)
	# though this took an hour
	start=time.time()
	ratingsDfpivoted=ratingsDf.pivot_table(rows='userID',cols='movieID',values='ratings')
	end=time.time()
	elapsed=end-start
	print "elapsed time for pivoting dataframe = ",elapsed

	return ratingsDfpivoted

def createTrainingTestSets(ratingsDfpivoted,nTrainingTestFolds):
	""" Returns nTrainingTestFolds-Fold training and test sets from ratingsDfpivoted
	"""	
	numUsers=ratingsDfpivoted.shape[0]

	users5Fold=KFold(numUsers, n_folds=nTrainingTestFolds,indices=False,shuffle=True)

	users5FoldArray=[(train, test) for train, test in users5Fold]

	ratingsInTrain=[ratingsDfpivoted[fold[0]] for fold in users5FoldArray]
	ratingsInTest=[ratingsDfpivoted[fold[1]] for fold in users5FoldArray]

	return [ratingsInTrain,ratingsInTest]

def createFeaturesTruthSets(ratingsInTest,nFeaturesTruthFolds):
	""" Returns nFeaturesTruthFolds-Fold feature and truth sets for each test set in ratingsInTest
	"""
	numMovies=ratingsInTest[0].shape[1]

	movies5Fold=KFold(numMovies, n_folds=nFeaturesTruthFolds,indices=False,shuffle=True)
	movies5FoldArray=[(features, truth) for features, truth in movies5Fold]

	ratingsInFeatures=[[test_set.ix[:,fold[0]] for fold in movies5FoldArray] for test_set in ratingsInTest]
	ratingsInTruth=[[test_set.ix[:,fold[1]] for fold in movies5FoldArray] for test_set in ratingsInTest]

	return [ratingsInFeatures,ratingsInTruth]

def writeSetsToFiles(ratingsInTrain,ratingsInTest,ratingsInFeatures,ratingsInTruth):
	for i_val_set in range(len(ratingsInTrain)):
	    ratingsInTrain[i_val_set].unstack().reset_index().dropna().to_csv('validation_1/ratings_train_%d.dat' % i_val_set,sep=':',cols=['userID','movieID',0],header=False,index=False)
	    ratingsInTest[i_val_set].to_csv('validation_1/ratings_test_%d.dat' % i_val_set,sep=':',header=False,index=False)

	    for j_fold in range(len(ratingsInFeatures)):
	    	ratingsInFeatures[i_val_set][j_fold].to_csv('validation_1/ratings_features_%d_%d.dat' % (i_val_set,j_fold) ,sep=':',header=False,index=False)	
	    	ratingsInTruth[i_val_set][j_fold].to_csv('validation_1/ratings_truth_%d_%d.dat' % (i_val_set,j_fold) ,sep=':',header=False,index=False)	

def createSVD(ratingsFile,outputFile):
	svdlibc = SVDLIBC(ratingsFile)
	svdlibc.to_sparse_matrix(sep=':', format={'col':0, 'row':1, 'value':2, 'ids': int})
	svdlibc.compute(k=100)
	svd.save_model(outputFile)
	return svdlibc.export()

def main():

	[ratingsInFeatures,ratingsInTruth]=createValidationSets('twolu100K',5,5)

	ratingsInTest_0=ratingsInTest[0]

	numMovies=ratingsInTest_0.shape[1]
	movies5Fold=KFold(numMovies, n_folds=5,indices=False,shuffle=True)
	movies5FoldArray=[(features, truth) for features, truth in movies5Fold]

	ratingsInFeatures=[ratingsInTest_0.ix[:,fold[0]] for fold in movies5FoldArray]
	ratingsInTruth=[ratingsInTest_0.ix[:,fold[1]] for fold in movies5FoldArray]

	ratingsInFeatures_0=ratingsInFeatures[0]
	ratingsInTruth_0=ratingsInTruth[0]

	ratingsInFeatures0User1=ratingsInFeatures_0.iloc[0]
	FiveRatingsFeatures0User1=ratingsInFeatures0User1[ratingsInFeatures0User1==5].keys()
	print FiveRatingsFeatures0User1


	ratingsInFeatures0User2=ratingsInFeatures_0.iloc[1]
	FiveRatingsFeatures0User2=ratingsInFeatures0User2[ratingsInFeatures0User2==5].keys()
	print FiveRatingsFeatures0User2



if __name__ == '__main__':
	main()