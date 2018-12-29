from gensim.test.utils import common_texts, get_tmpfile
from gensim.models import Word2Vec
from flask import Flask
from flask import request, render_template, flash
from flask import render_template
import flask
import io
import geopandas as gpd
from shapely.geometry import Point, LineString, Polygon
from geopandas import GeoDataFrame
import pandas as pd
import numpy as np
import shapely as sh
import pyproj as proj
import csv
import gensim as gensim
import geopandas as gp
import random
from sklearn.preprocessing import MultiLabelBinarizer


fp = '09_Manzanas_INV2016_shp/09_Manzanas_INV2016.shp'
man_inv = gpd.read_file(fp)
man_inv.crs = {'init' :'epsg:4326'}


man_inv['MZA_UNIQUE'] = man_inv['MZA'].str.lstrip("0") + ".0-" + man_inv['AGEB'] + "-" + man_inv['LOC'].str.lstrip("0") + "-" + man_inv['MUN'].str.lstrip("0") + "-" + man_inv['ENT'].str.lstrip("0")   




man_inv_final = pd.DataFrame({ "MZA_UNIQUE": man_inv['MZA_UNIQUE'], "POBTOT": man_inv['POBTOT'],"GRAPROES": man_inv['GRAPROES']})

#Remove missing values
man_inv_final.loc[man_inv_final['POBTOT'] == 'None','POBTOT'] = 0
man_inv_final.loc[man_inv_final['POBTOT'] == 'N.D.','POBTOT'] = 0
man_inv_final['POBTOT'] = man_inv_final['POBTOT']

man_inv_final.loc[man_inv_final['GRAPROES'] == 'N.D.', 'GRAPROES'] = 0
man_inv_final.loc[man_inv_final['GRAPROES'] == 'None', 'GRAPROES'] = 0
man_inv_final.loc[man_inv_final['GRAPROES'] == '*', 'GRAPROES'] = 0

# Discretize into bins

man_inv_final['POBTOT'] = pd.cut(man_inv_final['POBTOT'],10)
man_inv_final['GRAPROES'] = pd.cut(man_inv_final['GRAPROES'],5)


## build dummies to append

dummy1 = man_inv_final[['MZA_UNIQUE','POBTOT']]
dummy2 = man_inv_final[['MZA_UNIQUE','GRAPROES']]

dummy1 = dummy1.rename(columns = {"POBTOT": "codigo_act"})
dummy2 = dummy2.rename(columns = {"GRAPROES": "codigo_act"})

#### we will append these dummies

#defining the correct projection for Mexico City 

crs_wgs = proj.Proj(init='epsg:6372')

#import the data and take a quick look

cdmx_eu = pd.read_csv('denue_inegi_09_.csv')
cdmx_eu.head


# Some analysis

cdmx_eu["MZA_UNIQUE"] = cdmx_eu["manzana"].astype(str) + "-" + cdmx_eu["ageb"] + "-" + cdmx_eu["cve_loc"].astype(str) + "-" + cdmx_eu["cve_mun"].astype(str) + "-" + cdmx_eu["cve_ent"].astype(str)


cdmx_actividad_y_manzanaunica = cdmx_eu[["MZA_UNIQUE","codigo_act"]]

cdmx_actividad_y_manzanaunica = cdmx_actividad_y_manzanaunica.append(dummy1)
cdmx_actividad_y_manzanaunica = cdmx_actividad_y_manzanaunica.append(dummy2)

cdmx_actividad_y_manzanaunica.loc[cdmx_actividad_y_manzanaunica['codigo_act'] == 'NaN', 'codigo_act'] = 0

cdmx_actividad_y_manzanaunica.loc[cdmx_actividad_y_manzanaunica['codigo_act'].isna(), 'codigo_act']  = 0

## Building the Context

## Instead of words, our algorithm will be fed with businesses. Especifically, types of business. Analogous to NLP word2vec, we will build the context around each business. In this case, we will use 500m, though this will be a variable that we will modify while evaluating performance. 

grouped = cdmx_actividad_y_manzanaunica.groupby(['MZA_UNIQUE'])


sentences = []
for group in grouped:
  sentences.append(group)



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
    final_grouping[i].append(str(current_block.iloc[j,1]))
    
# shuffle in place
random.shuffle(final_grouping)

larger_than_zero = list(filter(lambda x: len(x) > 1, final_grouping))
train = larger_than_zero[0:int(len(larger_than_zero)*.8)]
test = larger_than_zero[int(len(larger_than_zero)*.8):int(len(larger_than_zero))]

model = gensim.models.Word2Vec(train, size=300,window=200,min_count=2,workers=10, sg=0)
model.train(train, total_examples=len(train), epochs=300, compute_loss=True)

model.save("word2vec.model")

correct_predictions = 0
incorrect_predictions = 0
for i in range(len(test)):
  
  missing_biz = test[i].pop(0)
  if(len(test[i]) > 0):
    code_prediction = model.predict_output_word(test[i])
    testing_list = []
    print(i)
    # empty sequences return a boolean false when checked like this ;)
    if not code_prediction:
	    for j in range(len(code_prediction)):
	      testing_list.append(code_prediction[j][0])
	    if (missing_biz in testing_list[0]):
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



