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




app = Flask(__name__)


## Parse coordinate 

@app.route('/parse-coordinate', methods=['POST', 'GET'])
def show_user_profile():

    if request.method == 'POST':

    # checar si hay que parsear el request a texto

      coordinates = request.form['location']
      output = which_block_intersects(coordinates)
      resp = flask.Response(output)
      resp.headers['Access-Control-Allow-Origin'] = '*'
      return resp
    return


def prediction(biz_codes = [], *args):
	model = Word2Vec.load("word2vec.model")
	prediction = model.predict_output_word(biz_codes)
	return (str(prediction))





@app.route('/')

def hello(name=None):
    return render_template('form.html', name=name)


def which_block_intersects(coordinates):

	coord2 = coordinates.replace("(","")
	coord3 = coord2.replace(")","")
	split = coord3.split(',')
	latitude = float(split[0])
	longitude = float(split[1])


	fp = 'df_manzana.shp'
	blocks_poly = gpd.read_file(fp)
	blocks_poly.crs = {'init' :'epsg:4326'}
	point = Point(longitude,latitude)
	point_g = [point]
	crs = {'init' :'epsg:4326'} #http://www.spatialreference.org/ref/epsg/2263/
	geo_df = GeoDataFrame(crs=crs, geometry=point_g)
	join = gpd.sjoin(geo_df, blocks_poly, how="inner", op="within")
	manzana = str(join.iloc[0]["CVE_MZA"]).lstrip("0") + ".0-" + str(join.iloc[0]["CVE_AGEB"]) + "-" + str(join.iloc[0]["CVE_LOC"]).lstrip("0") + "-"  + str(join.iloc[0]["CVE_MUN"]).lstrip("0") + "-" + str(join.iloc[0]["CVE_ENT"]).lstrip("0")
	#final_grouping = businesses_in_block(manzana)

	## remove this before cloud deployment 
	if __name__ == "__main__":
  		app.run(host='0.0.0.0')

  	######
  	cdmx_actividad_y_manzanaunica = pd.read_csv('bizbyblock.csv')
  	catalog = pd.read_csv('activity-name-catalog.csv')

	grouped = cdmx_actividad_y_manzanaunica.groupby(['manzana-ageb-loc-mun-edo'])
	print(manzana)
	sentences = []
	for group in grouped:
	  sentences.append(group)

	final_grouping = []
	for i in range(len(sentences)):

	  
	  holder = sentences[i]
	  current_block = holder[1]
	  if (holder[0] == manzana):
		for j in range(len(current_block)):
			
			final_grouping.append(str(current_block.iloc[j,3]))



	model = Word2Vec.load("word2vec.model")
	code_prediction = model.predict_output_word(final_grouping)

	name_and_confidence = []
	for i in range(len(code_prediction)):
		for j in range(len(catalog)):
			
			if(str(catalog['codigo_act'].loc[j]) == (str(code_prediction[i][0]))):
				name_and_confidence.append(tuple((catalog['nombre_act'].loc[j],code_prediction[i][1])))

	  #temp_list = []
	  #temp_list.append(code_prediction[i][0])
	  #name_and_confidence.append(tuple((catalog['nombre_act'].loc[catalog['codigo_act'].isin(temp_list)],code_prediction[i][1])))

	return (str(name_and_confidence))


	#return manzana

def businesses_in_block(manzana):
	cdmx_actividad_y_manzanaunica = pd.read_csv('bizbyblock.csv')
	grouped = cdmx_actividad_y_manzanaunica.groupby(['manzana-ageb-loc-mun-edo'])

	sentences = []
	for group in grouped:
	  sentences.append(group)

	final_grouping = []
	for i in range(len(sentences)):
	  final_grouping.append([])
	  holder = sentences[i]
	  current_block = holder[1]
	  if (holder[0] == manzana):
		  for j in range(len(current_block)):
		    final_grouping[i].append(str(current_block.iloc[j,2]))

	return final_grouping[0]






