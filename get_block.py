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


fp = 'df_manzana.shp'
blocks_poly = gpd.read_file(fp)
blocks_poly.crs = {'init' :'epsg:4326'}
point = Point(-99.19,19.42)
point_g = [point]
crs = {'init' :'epsg:4326'} #http://www.spatialreference.org/ref/epsg/2263/
geo_df = GeoDataFrame(crs=crs, geometry=point_g)
join = gpd.sjoin(geo_df, blocks_poly, how="inner", op="within")


manzana = str(join.iloc[0]["CVE_MZA"]).lstrip("0") + "-" + str(join.iloc[0]["CVE_AGEB"]) + "-" + str(join.iloc[0]["CVE_LOC"]).lstrip("0") + "-"  + str(join.iloc[0]["CVE_MUN"]).lstrip("0") + "-" + str(join.iloc[0]["CVE_ENT"]).lstrip("0")


