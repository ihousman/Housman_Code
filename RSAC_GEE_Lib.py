from r_numpy_lib import *
import ee
from ee import mapclient
import os, sys,shutil, urllib
from datetime import datetime
########################################
MY_SERVICE_ACCOUNT = '584587499163@developer.gserviceaccount.com'# replace with your service account
MY_PRIVATE_KEY_FILE = 'housman_api_key.p12'
ee.Initialize(ee.ServiceAccountCredentials(MY_SERVICE_ACCOUNT, MY_PRIVATE_KEY_FILE))
def polygon_list_to_polygon_string(polygon_list):
    #polygon = ee.Feature.Polygon(polygon_list)
    polygon_string = "[";
    for i in range(len(polygon_list)):
        polygon_string = polygon_string  + str(polygon_list[i]) + ','

    polygon_string = polygon_string[:-1] + ']'
    return polygon_string
def prepare_shapefile(in_shp):
    s_info = shape_info(in_shp)
    mbr_coords = s_info['coords']
    out_mbr_coords = [[mbr_coords[0],mbr_coords[1]], [mbr_coords[0], mbr_coords[-1]], [mbr_coords[2], mbr_coords[-1]], [mbr_coords[2], mbr_coords[1]],[mbr_coords[0],mbr_coords[1]]]
    out_string_mbr_coords = polygon_list_to_polygon_string(out_mbr_coords)
    out_mbr_ee_polygon = ee.Feature.Polygon(out_mbr_coords)
    return out_mbr_coords, out_string_mbr_coords, out_mbr_ee_polygon

def from_country(country_name):
    tf = ee.FeatureCollection('ft:1tdSwUL7MVpOauSgRzqVTOwdfy17KDbw-1d9omPw').filter(ee.Filter().eq('Country',country_name))
    tf_geom = tf.geometry()
    info = tf.getInfo()
    coordinates = info['features'][0]['geometry']['coordinates']
    coord_string = polygon_list_to_polygon_string(coordinates)
    return tf, tf_geom, coordinates, coord_string

def fc_to_raster(fc, properties = ['ECO_NUM']):
    mr = ee.Reducer.mean()
    return fc.reduceToImage(properties, mr)

#Returns an image object
#Start date syntax: start_date = [year,month,day] e.g. [2001,7,1,2001]
#End date syntax: end_date = [year,month,day] e.g. [2001,10,1]
end_date = [2,1]
def get_image_collection(collection_name, start_date, end_date):
    start_date_obj = datetime(start_date[0], start_date[1], start_date[2])
    end_date_obj = datetime(end_date[0], end_date[1], end_date[2])
    image = ee.ImageCollection(collection_name).filterDate(start_date_obj, end_date_obj)
##    if ee_clip_poly != '' and ee_clip_poly != None:
##        image = image.clip(ee_clip_poly)
    return image
    #.reduce(ee.Reducer.percentile(percentile)).multiply(1000).toInt().clip(polygon)

def download_image(image, output_name, region_string, resolution = 30, EPSG = 32613):
    #//Code to get a download URL
    #//Currently written that it can easily be pasted into a Python script as a dictionary, and use the urllib.urlretrieve function to grab the .zip file
    path = image.getDownloadUrl({'name': base(output_name),
    'scale': resolution,
    'crs': 'EPSG:' + str(EPSG),
    'region': '' + region_string + ''
    })

    print("'" +output_name + "': '" + path + "',")

    #Map = ee.mapclient.MapClient()
    #Map.addOverlay(mapclient.MakeOverlay(image.getMapId()))#{'min': 0, 'max': 3000})))

    print 'Downloading', output_name
    urllib.urlretrieve(path, output_name)


def download_and_unzip_image(image, output_name, region_string, resolution = 30, EPSG = 32613):
    if os.path.splitext(output_name)[1] != '.zip':
        output_zip = os.path.splitext(output_name)[0] + '.zip'
    else:
        output_zip = output_name
    out_unzip_dir = os.path.splitext(output_name)[0] + '/'
    if os.path.exists(output_zip) == False:
        print 'gotta download it'
        download_image(image, output_zip, region_string, resolution, EPSG)
    else:
        print 'Already downloaded', output_zip
    smart_unzip(output_zip, out_unzip_dir)

##in_shp = 'L:/Shapefiles/ETH_adm0.shp'
##poly_list,poly_string, poly_ee = prepare_shapefile(in_shp)


##country_poly = from_country('Ethiopia')
##
##fc = ee.FeatureCollection(1015262)
##image = fc_to_raster(fc)
##
##print type(country_poly[-2])
###collection = 'srtm90_v4'
##country = 'Ethiopia'
##EPSG = 32637
##resolution =500
##out_dir = 'K:/GEE_Data/LC/'
####check_dir(out_dir)
##out_dem = out_dir + 'Ethiopia_Ecoregions.zip'
##
###image = ee.Image(collection)
###image = ee.Image('MCD12Q1/MCD12Q1_005_2001_01_01').select(['Land_Cover_Type_1'])
##download_and_unzip_image(image, out_dem, country_poly[-1], resolution, EPSG)