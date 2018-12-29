import pandas as pd
import numpy as np
import shapely as sh
import pyproj as proj
import csv
import gensim as gensim
import geopandas as gp
import random
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import confusion_matrix
from sklearn.externals import joblib
from random import randint




#defining the correct projection for Mexico City 

crs_wgs = proj.Proj(init='epsg:6372')

#import the data and take a quick look

cdmx_eu = pd.read_csv('denue_inegi_09_.csv')
cdmx_eu.head



# Some analysis

activity_counts = cdmx_eu["nombre_act"].value_counts()

cdmx_eu["manzana-ageb-loc-mun-edo"] = cdmx_eu["manzana"].astype(str) + "-" + cdmx_eu["ageb"] + "-" + cdmx_eu["cve_loc"].astype(str) + "-" + cdmx_eu["cve_mun"].astype(str) + "-" + cdmx_eu["cve_ent"].astype(str)
cdmx_eu.head

cdmx_actividad_y_manzanaunica = cdmx_eu[["nombre_act","manzana-ageb-loc-mun-edo","codigo_act"]]
cdmx_actividad_y_manzanaunica.head

units_per_block = cdmx_actividad_y_manzanaunica["manzana-ageb-loc-mun-edo"].value_counts()
units_per_block.mean()


## Easily retrieve the activity name from the activity code and viceversa

# encoding activities

business_pairs = cdmx_eu[["nombre_act","codigo_act"]]
unique_business_pairs = business_pairs.drop_duplicates()
dic = unique_business_pairs.to_dict("records")


def find_activity_code(dataframe, name):
  row = unique_business_pairs.loc[unique_business_pairs['nombre_act'] == name]
  return int(row["codigo_act"])
   
  
def find_activity_name(dataframe, code):
  row = unique_business_pairs.loc[unique_business_pairs['codigo_act'] == code]
  return str(row["nombre_act"])
  

# Build an actual dictionary


activity_set = set(unique_business_pairs["nombre_act"])

biz2int = {}
int2biz = {}

for index, activity in enumerate(activity_set):
  biz2int[activity] = index
  int2biz[index] = activity
  

 ## Building the Context

## Instead of words, our algorithm will be fed with businesses. Especifically, types of business. 
## Analogous to NLP word2vec, we will build the context around each business. In this case, we will use 500m,
## though this will be a variable that we will modify while evaluating performance. 

cdmx_actividad_y_manzanaunica.to_csv('bizbyblock.csv')

grouped = cdmx_actividad_y_manzanaunica.groupby(['manzana-ageb-loc-mun-edo'])


sentences = []
for group in grouped:
  sentences.append(group)


# function to test if there is a retail business in the block

def is_retail(lista):
  retail = False
  for x in lista:
    if x.startswith('46'):
      retail = True
      return retail
  return retail


### function to create count list
#We create a list of lists. Each inside list contains a sentence: a group of businesses that appear together within a block.
# sentences contains tuples, so we grab each tuple. If we grab the second part of the tuple, we get a dataframe that contains 
# all businesses within a given block. We iterate through that dataframe grabbing the type of business code and putting it inside 
#one of the lists

# further explanation because something weird happens:
# current_block.iloc[j,2] grabs the activity code.
# sentences[i] gives you the ith tuple. If you assign that tuple to a value, in this case --holder--. If you
# grab holder[1], you get the second part of the tuple which is a dataframe. Here we assign that dataframe to current_block which is literally the
# the street block we are at right now. Then we want to iterate within the block to grab each business code. That is in the 3rd colum, (0-indexed, so
# with the value 2)
#

final_grouping = []
for i in range(len(sentences)):
  final_grouping.append([])
  holder = sentences[i]
  current_block = holder[1]
  for j in range(len(current_block)):
    final_grouping[i].append(str(current_block.iloc[j,2]))


filtered = list(filter(lambda x: len(x) > 1 and is_retail(x), final_grouping))

retail_only = []
for i in range(len(filtered)):
  retail_only.append(list(filter(lambda x: x.startswith('46'), filtered[i])))

retail_only = list(filter(lambda x: len(x) > 1, retail_only))


train = retail_only[0:int(len(retail_only)*.8)]
test = retail_only[int(len(retail_only)*.8):int(len(retail_only))]



unique_codes = unique_business_pairs["codigo_act"].values ## this is the catalog
def create_count_array(list, catalog):
  array = np.asarray(list)
  count_list = np.zeros(catalog.shape)
  for i in range(array.shape[0]):
    val = np.where(unique_codes == int(array[i]))[0][0]
    count_list[val] = count_list[val] + 1 
  return count_list


## this function finds occurrences greater than zero, which means the existence of one or more types of businesses in a block, extracts the indices and 
## substracts one to a random index. It then creates a zeroed array with the same size as the sample and adds a one to the index from which removed it. Basically, 
## removing one business from each block and building a context-business pair


def remove_business_and_create_label(array):
  indices = np.where(array > 0)[0]
  rand_index = indices[randint(0,indices.size-1)]
  array[rand_index] = array[rand_index] - 1 
  label = np.zeros(array.size)
  label[rand_index] = 1
  return label


####  do it for train set



train = np.asarray(train)
x_values_train = []
for i in range(len(train)):
  count_list = create_count_array(train[i],unique_codes)
  x_values_train.append(count_list)

x_values_train = np.asarray(x_values_train)

y_values_train = np.empty(x_values_train.shape)
for i in range(x_values_train.shape[0]):
  array = x_values_train[i]
  label = remove_business_and_create_label(array)
  y_values_train[i] = label



test = np.asarray(test)
x_values_test = []
for i in range(len(train)):
  count_list = create_count_array(train[i],unique_codes)
  x_values_test.append(count_list)

x_values_test = np.asarray(x_values_test)

y_values_test = np.empty(x_values_test.shape)
for i in range(x_values_test.shape[0]):
  array = x_values_test[i]
  label = remove_business_and_create_label(array)
  y_values_test[i] = label


classifier = RandomForestClassifier(n_estimators = 100, criterion = 'entropy', random_state = 42)
classifier.fit(x_values_train, y_values_train)
print('Random Forest')
print(classifier.score(x_values_test, y_values_test))