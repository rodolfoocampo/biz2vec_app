from gensim.test.utils import common_texts, get_tmpfile
from gensim.models import Word2Vec
import gensim as gensim
from flask import Flask
from flask import request, render_template, flash
from flask import render_template
import flask
import io
import geopandas as gpd
from shapely.geometry import Point, LineString, Polygon
from geopandas import GeoDataFrame
import pandas as pd
import pyproj as proj




#defining the correct projection for Mexico City 

crs = {'init' :'epsg:6372'}



#import the data and take a quick look

cdmx_eu = pd.read_csv('denue_inegi_09_.csv')


# Some analysis


cdmx_points = cdmx_eu[['codigo_act','latitud','longitud']]
cdmx_points['coordinates'] = list(zip(cdmx_points.longitud, cdmx_points.latitud))
cdmx_points['coordinatesP'] = cdmx_points['coordinates'].apply(Point)
cdmx_gdf = gpd.GeoDataFrame(cdmx_points, geometry='coordinatesP', crs = crs)

final_grouping = []
for i in range(len(cdmx_gdf)):
  point = cdmx_gdf['coordinatesP'].loc[i]
  radius = point.buffer(0.001, resolution=100)
  radius_poly = [radius]
  radius_df = GeoDataFrame(crs=crs, geometry=radius_poly)
  join = gpd.sjoin(cdmx_gdf,radius_df, how="inner", op="intersects")
  join['codigo_act'] = join['codigo_act'].astype(str)
  print(i)
  final_grouping.append(list(join['codigo_act']))




## Easily retrieve the activity name from the activity code and viceversa
# encoding activities


  

## Building the Context

## Instead of words, our algorithm will be fed with businesses. Especifically, types of business. Analogous to NLP word2vec, we will build the context around each business. In this case, we will use 500m, though this will be a variable that we will modify while evaluating performance. 






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


    


model = gensim.models.Word2Vec(final_grouping, size=150,window=15,min_count=2,workers=10, sg=0)
model.train(final_grouping, total_examples=len(final_grouping), epochs=10, compute_loss=True)

model.save("word2vec_radius.model")

prediction = model.predict_output_word(['461211', '461110', '488492', '493119', '522490', '522110', '522210', '522110'])

print(prediction)