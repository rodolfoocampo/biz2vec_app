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



app = Flask(__name__)


## Parse coordinate 

@app.route('/parse-coordinate', methods=['POST', 'GET'])
def show_user_profile():

    if request.method == 'POST':

    # checar si hay que parsear el request a texto

      coordinates = request.form['location']
      output = which_block_intersects(coordinates)
      #image_location = "/Users/rodolfoocampo/Documents/Datalab/Proyectos/tensorflow-for-poets-2/real_images/" + coord6 + ".jpg"
      resp = flask.Response(output)
      resp.headers['Access-Control-Allow-Origin'] = '*'
      return resp
    return

@app.route('/model?coordinate=<biz_code>')
def hello_world(biz_code):
	model = Word2Vec.load("word2vec.model")
	prediction = model.predict_output_word([str(biz_code)])
	print(prediction)
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


	manzana = str(join.iloc[0]["CVE_MZA"]).lstrip("0") + "-" + str(join.iloc[0]["CVE_AGEB"]) + "-" + str(join.iloc[0]["CVE_LOC"]).lstrip("0") + "-"  + str(join.iloc[0]["CVE_MUN"]).lstrip("0") + "-" + str(join.iloc[0]["CVE_ENT"]).lstrip("0")
	return manzana





