import pyproj as proj
from shapely import geometry

# setup your projections
crs_wgs = proj.Proj(init='epsg:4326') # assuming you're using WGS84 geographic
crs_bng = proj.Proj(init='epsg:27700') # use a locally appropriate projected CRS

# then cast your geographic coordinate pair to the projected system

x, y = proj.transform(crs_wgs, crs_bng, [-99.19739576015266], [19.429819436501024])


# create your two points
point_1 = geometry.Point(x_1, y_1)
point_2 = geometry.Point(x_2, y_2)

# create your circle buffer from one of the points
distance = 1000
circle_buffer = point_1.buffer(distance)

# and you can then check if the other point lies within
if point_2.within(circle_buffer):
    print('point 2 is within the distance buffer of point 1')
# or similarly
if circle_buffer.contains(point_2):
    print('circle buffer contains point 2')

# but a simpler method is to simply check the distance
if point_1.distance(point_2) < distance:
    print('point 1 is within the distance of point 2')


from shapely.ops import nearest_points
import pyproj as proj
from shapely import geometry

fp = 'df_manzana.shp'
blocks_poly = gpd.read_file(fp)
blocks_poly.crs = {'init' :'epsg:4326'}
point = Point(-99.19,19.42)
point_g = [point]
crs = {'init' :'epsg:4326'} #http://www.spatialreference.org/ref/epsg/2263/
geo_df = GeoDataFrame(crs=crs, geometry=point_g)
join = gpd.sjoin(geo_df, blocks_poly, how="inner", op="within")

nearest_geoms = nearest_points(geo_df, blocks_poly)