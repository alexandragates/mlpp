


# libraries

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sklearn.tree as tree
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.cross_validation import train_test_split


def get_correlations(dataframe):
	'''
	makes correlations of each of the columns of the dataframe
	inputs: dataframe
	outputs: correlations of the variables
	'''
	return dataframe.corr()


# explore data
# scatterplot to see correlations between variables that aren't delinquency, personID, or zipcode.

def make_scatter(dataframe):
	'''
	function to make scatterplots showing how each variable changes based on whether they are
	delinquent or not
	input: dataframe
	output: scatterplots!
	'''
	for col in list(dataframe):
		for cols in list(dataframe):
			dataframe.plot.scatter(col, cols, figsize = (10,5))
			plt.title(col + ' vs ' + cols)
			plt.xlabel(col)
			plt.ylabel(cols)
			
			plt.show()

def make_boxplots(dataframe, by):
	'''
	function to make boxplots showing how each variable changes based on whether they are
	delinquent or not
	input: dataframe
	output: boxplots!
	'''
	for col in list(dataframe):
		dataframe.boxplot(col, by=by)
		plt.title('vs ' + col)
		plt.xlabel(by)
		plt.ylabel(col)
		plt.show()


def make_zscore_df(dataframe):
	'''
	calculates a dataframe of the z-score of all data points to identify which are outliers
	inputs: dataframe and the columns that won't be used to 
	'''    
	cols = list(dataframe)
	zscore_df = pd.DataFrame(columns=['num_outliers'])
	
	for col in cols:
		col_zscore = col + '_zscore'
		zscore_single_col = (dataframe[col] - dataframe[col].mean())/dataframe[col].std()
		zscore_df.loc[:,col_zscore] = zscore_single_col
	return zscore_df


# calculate number of outliers in the row
def calculate_outliers_per_row(zscore_df, score, threshold):
	'''
	function to calculate the number of outliers in the row and put that sum in a column
	inputs: zscore df made from make zscore df function and a predetermined z-score
	output:
	'''
	trans = zscore_df.transpose()
	sumsgreat = (trans > score).sum()
	sumsless = (trans < -score).sum()
	sums = sumsgreat + sumsless
	zscore_df['num_outliers'] = sumsgreat + sumsless
 
	# figure out which rows have any and many outliers.
	trans2 = zscore_df.transpose()
	rows_with_any_outliers = []
	rows_with_many_outliers = []
	for x in list(trans2):
		if trans2[x]['num_outliers'] > threshold: # if more than 33% of the entries in it are outliers, remove that row from the z-score table.
			rows_with_many_outliers.append(x)
			trans2 = trans2.drop([x], axis=1)
		if trans2[x]['num_outliers'] > 0:
			rows_with_any_outliers.append(x)
	return rows_with_many_outliers, rows_with_any_outliers


# are there any nas?
def find_nas(dataframe):
	'''
	find if there are any columns with nas in the DataFrame
	input: dataframe
	output: each column with a boolean True or False if have any nas
	'''
	return dataframe.isna().any()

def cols_with_nas(series):
	return series.index[series].tolist()



# created function to fill nas based on specific inputs user want to use.
def fillnas_with_data(dataframe, stat, variables):
    '''
    fill the nas with different values based on inputs.
    inputs:
        dataframe: either with outliers, without rows with many outliers, or without rows with at least one outlier
        stat: either median or mean
        variables: the variables to be filled.
    outputs: dataframe with nas filled
    '''
    for var in variables:
        if stat == 'median' or 'Median':
            fill_type = 'median_' + var
            fill_name = dataframe[var].median()
            dataframe[var] = dataframe[var].fillna(fill_name)
        elif stat == 'mean' or 'Mean' or 'average' or 'Average':
            fill_type = 'mean_' + var
            fill_name = dataframe[var].mean()
            dataframe[var] = dataframe[var].fillna(fill_name)
        else:
            print('Error: please only use median, Median, mean, Mean, average, or Average')
    return dataframe


# discretize variable of choice by any buckets with equal-width bins or quantile bins
# Wanted the user to have the choice of either cut or qcut. I chose cut because I didn't want each bin to have the same 
    # number of entries, and I chose age because I'm curious how the analysis changes by age range.

def discretize_variables(dataframe, col_name, buckets, cut_type):
    '''
    function to discretize variables.
    inputs:
        dataframe: cred_df, cred_df_no_outliers, cred_df_less_outliers
        col_name: the name of the column from the dataframe user wants to discretize
        buckets: number of buckets want to discretize by
        cut_type: way to make the buckets - either equal-width bins (cut), or quantile bins (qcut)
    output:
        dataframe with a column that's changed from continuous to discrete.
    '''
    if cut_type == 'cut' or 'Cut':
        dataframe[col_name] = pd.cut(dataframe[col_name], buckets)
    elif cut_type == 'qcut' or 'Qcut':
        dataframe[col_name] = pd.qcut(dataframe[col_name], buckets)
    else:
        print('Error: Please only use cut or qcut')
    return dataframe


# create binary/dummy variables from categorical variable
def dummify_categories(dataframe, col_name):
    '''
    function to create dummy variables from categorized data.
    inputs: 
        dataframe: either cred_df, cred_df_no_outliers, or cred_df_less_outliers
        col_name: column name of column to dummify
    outputs: pandas series of dummy data
    '''
    dummies = pd.get_dummies(dataframe[col_name], prefix=col_name)
    return dummies


def knn_model(X, Y, test_size, knn):
	'''
	function that initializes the model
	inputs: 
		X: dataframe without predictor and other columns that make no sense to include
		Y: dataframe with only the predictor column
		test_size: the test size requirement for train_test_split
		knn: initialized model
	outputs:
		x_train: dataframe to train with x data
		x_test: dataframe to test with x data
		y_train: dataframe to train with y data
		y_test: dataframe to test with y data
	'''
	x_train, x_test, y_train, y_test = train_test_split(X, Y, test_size=test_size)
	return x_train, x_test, y_train, y_test
    
def knn_fit(x_train, y_train, knn):
	'''
	function to fit the model
	inputs: 
		x_train: dataframe to train with x data
		y_train: dataframe to train with y data
		knn: initialized model
	output:
		the fit model
	'''
	return knn.fit(x_train, y_train)


def predict_classifier(fit, X, knn):
	'''
	function to predict the probability
	inputs:
		fit: the fit model
		X: dataframe without predictor and other columns that make no sense to include
		knn: initialized model
	outputs: 
		list of prediction probabilities for each data point
	'''
	return knn.predict_proba(X)

def accuracy_classifier(fit, x_test, y_test, knn):
	'''
	function to determine accuracy of the model
	inputs:
		fit: the fit model
		x_test: dataframe to test with x data
		y_test: dataframe to test with y data
		knn: initialized model
	output:
		single accuracy score
	'''
	return knn.score(x_test, y_test)