import pandas as pd
import numpy as np
import shapely as sh
import pyproj as proj
import csv
import gensim as gensim
import geopandas as gp
import random
from sklearn.preprocessing import MultiLabelBinarizer





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

## Instead of words, our algorithm will be fed with businesses. Especifically, types of business. Analogous to NLP word2vec, we will build the context around each business. In this case, we will use 500m, though this will be a variable that we will modify while evaluating performance. 
cdmx_actividad_y_manzanaunica.to_csv('bizbyblock.csv')

grouped = cdmx_actividad_y_manzanaunica.groupby(['manzana-ageb-loc-mun-edo'])


sentences = []
for group in grouped:
  sentences.append(group)



def is_retail(lista):
  retail = False
  for x in lista:
    if x.startswith('46'):
      retail = True
      return retail
  return retail




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
    


# shuffle in place
random.shuffle(final_grouping)

filtered = list(filter(lambda x: len(x) > 1 and is_retail(x), final_grouping))

retail_only = []
for i in range(len(filtered)):
  retail_only.append(list(filter(lambda x: x.startswith('46'), filtered[i])))

retail_only = list(filter(lambda x: len(x) > 1, retail_only))

#function to count how many retail classes remain

sett = []
for i in range(len(retail_only)):
  for j in range(len(retail_only[i])):
    sett.append(retail_only[i][j])
###############

train = retail_only[0:int(len(retail_only)*.8)]
test = retail_only[int(len(retail_only)*.8):int(len(retail_only))]
    

model = gensim.models.Word2Vec(train, size=200,window=200,min_count=2,workers=10, sg=0)
model.train(train, total_examples=len(train), epochs=200, compute_loss=True)

model.save("word2vec.model")

correct_predictions = 0
incorrect_predictions = 0
for i in range(len(test)):
  
  missing_biz = test[i].pop(0)
  if(len(test[i]) > 0):
    code_prediction = model.predict_output_word(test[i])
    testing_list = []
    for j in range(len(code_prediction)):
      testing_list.append(code_prediction[j][0])
    if (missing_biz in testing_list):
      correct_predictions = correct_predictions + 1
    else:
      incorrect_predictions = incorrect_predictions + 1

accuracy = float(correct_predictions)/(float(correct_predictions)+float(incorrect_predictions))


print('Correct predictions: ')
print(correct_predictions)
print('Incorrect predictions: ')
print(incorrect_predictions)
print('Accuracy: ')
print(accuracy)

