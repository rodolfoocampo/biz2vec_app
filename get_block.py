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





coord2 = coordinates.replace("(","")
coord3 = coord2.replace(")","")
split = coord3.split(',')
latitude = split[0]
longitude = split[1]


fp = 'df_manzana.shp'
blocks_poly = gpd.read_file(fp)
blocks_poly.crs = {'init' :'epsg:4326'}
point = Point(longitude,latitude)
point_g = [point]
crs = {'init' :'epsg:4326'} #http://www.spatialreference.org/ref/epsg/2263/
geo_df = GeoDataFrame(crs=crs, geometry=point_g)
join = gpd.sjoin(geo_df, blocks_poly, how="inner", op="within")


manzana = str(join.iloc[0]["CVE_MZA"]).lstrip("0") + "-" + str(join.iloc[0]["CVE_AGEB"]) + "-" + str(join.iloc[0]["CVE_LOC"]).lstrip("0") + "-"  + str(join.iloc[0]["CVE_MUN"]).lstrip("0") + "-" + str(join.iloc[0]["CVE_ENT"]).lstrip("0")

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
  if (holder[0] == selected_coordinate)
	  for j in range(len(current_block)):
	    final_grouping[i].append(str(current_block.iloc[j,2]))


coordinates = '(19.10,-99.80)'
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


