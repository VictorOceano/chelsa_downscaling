#!/usr/bin/env python

#This file is part of chelsa_highres.
#
#chelsa_highres is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.

#chelsa_highres is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with chelsa_cmip6.  If not, see <https://www.gnu.org/licenses/>.


import saga_api
import sys
import os
import argparse
import datetime
import os.path
import psutil
import shutil


def Load_Tool_Libraries(Verbose):
    saga_api.SG_UI_Msg_Lock(True)
    if os.name == 'nt':    # Windows
        os.environ['PATH'] = os.environ['PATH'] + ';' + os.environ['SAGA_32'] + '/dll'
        saga_api.SG_Get_Tool_Library_Manager().Add_Directory(os.environ['SAGA_32' ] + '/tools', False)
    else:                  # Linux
        saga_api.SG_Get_Tool_Library_Manager().Add_Directory('/usr/local/lib/saga/', False)        # Or set the Tool directory like this!
    saga_api.SG_UI_Msg_Lock(False)

    if Verbose == True:
                print 'Python - Version ' + sys.version
                print saga_api.SAGA_API_Get_Version()
                print 'number of loaded libraries: ' + str(saga_api.SG_Get_Tool_Library_Manager().Get_Count())
                print

    return saga_api.SG_Get_Tool_Library_Manager().Get_Count()


def Load_Tool_Libraries(Verbose):
    saga_api.SG_UI_Msg_Lock(True)
    if os.name == 'nt':    # Windows
        os.environ['PATH'] = os.environ['PATH'] + ';' + os.environ['SAGA_32'] + '/dll'
        saga_api.SG_Get_Tool_Library_Manager().Add_Directory(os.environ['SAGA_32' ] + '/tools', False)
    else:                  # Linux
        saga_api.SG_Get_Tool_Library_Manager().Add_Directory('/usr/local/lib/saga/', False)        # Or set the Tool directory like this!
    saga_api.SG_UI_Msg_Lock(False)

    if Verbose == True:
                print 'Python - Version ' + sys.version
                print saga_api.SAGA_API_Get_Version()
                print 'number of loaded libraries: ' + str(saga_api.SG_Get_Tool_Library_Manager().Get_Count())
                print

    return saga_api.SG_Get_Tool_Library_Manager().Get_Count()


def load_sagadata(path_to_sagadata):

    saga_api.SG_Set_History_Depth(0)    # History will not be created
    saga_api_dataobject = 0             # initial value

    # CSG_Grid -> Grid
    if any(s in path_to_sagadata for s in (".sgrd", ".sg-grd", "sg-grd-z")):
        saga_api_dataobject = saga_api.SG_Get_Data_Manager().Add_Grid(unicode(path_to_sagadata))

    # CSG_Grids -> Grid Collection
    if any(s in path_to_sagadata for s in ("sg-gds", "sg-gds-z")):
        saga_api_dataobject = saga_api.SG_Get_Data_Manager().Add_Grids(unicode(path_to_sagadata))

    # CSG_Table -> Table
    if any(s in path_to_sagadata for s in (".txt", ".csv", ".dbf")):
        saga_api_dataobject = saga_api.SG_Get_Data_Manager().Add_Table(unicode(path_to_sagadata))

    # CSG_Shapes -> Shapefile
    if '.shp' in path_to_sagadata:
        saga_api_dataobject = saga_api.SG_Get_Data_Manager().Add_Shapes(unicode(path_to_sagadata))

    # CSG_PointCloud -> Point Cloud
    if any(s in path_to_sagadata for s in (".spc", ".sg-pts", ".sg-pts-z")):
        saga_api_dataobject = saga_api.SG_Get_Data_Manager().Add_PointCloud(unicode(path_to_sagadata))

    if saga_api_dataobject == None or saga_api_dataobject.is_Valid() == 0:
        print 'ERROR: loading [' + path_to_sagadata + ']'
        return 0

    print 'File: [' + path_to_sagadata + '] has been loaded'
    return saga_api_dataobject


def import_gdal(File):
    #_____________________________________
    # Create a new instance of tool 'Import Raster'
    Tool = saga_api.SG_Get_Tool_Library_Manager().Create_Tool('io_gdal', '0')
    if Tool == None:
        print 'Failed to create tool: Import Raster'
        return False

    Parm = Tool.Get_Parameters()
    Parm('FILES').Set_Value(File)
    Parm('MULTIPLE').Set_Value('automatic')
    Parm('TRANSFORM').Set_Value(False)
    Parm('RESAMPLING').Set_Value('Nearest Neighbour')

    print 'Executing tool: ' + Tool.Get_Name().c_str()
    if Tool.Execute() == False:
        print 'failed'
        return False
    print 'okay'

    #_____________________________________
    output = Tool.Get_Parameter(saga_api.CSG_String('GRIDS')).asGridList().Get_Grid(0)
    # _____________________________________

    return output


def import_ncdf(ncdffile):
    #_____________________________________
    # Create a new instance of tool 'Import NetCDF'
    Tool = saga_api.SG_Get_Tool_Library_Manager().Create_Tool('io_gdal', '6')
    if Tool == None:
        print 'Failed to create tool: Import NetCDF'
        return False

    Parm = Tool.Get_Parameters()
    Parm('FILE').Set_Value(ncdffile)
    Parm('SAVE_FILE').Set_Value(False)
    Parm('SAVE_PATH').Set_Value('')
    Parm('TRANSFORM').Set_Value(True)
    Parm('RESAMPLING').Set_Value('Nearest Neighbour')

    print 'Executing tool: ' + Tool.Get_Name().c_str()
    if Tool.Execute() == False:
        print 'failed'
        return False
    print 'okay'

    #_____________________________________

    output = Tool.Get_Parameter(saga_api.CSG_String('GRIDS')).asGridList()
    return output


def change_latlong(obj):
    #_____________________________________
    # Create a new instance of tool 'Change Longitudinal Range for Grids'
    Tool = saga_api.SG_Get_Tool_Library_Manager().Create_Tool('pj_proj4', '13')
    if Tool == None:
        print('Failed to create tool: Change Longitudinal Range for Grids')
        return False

    Tool.Get_Parameters().Reset_Grid_System()

    Tool.Get_Parameter('INPUT').asList().Add_Item(obj.asGrid())
    Tool.Set_Parameter('DIRECTION', 0)
    Tool.Set_Parameter('PATCH', True)

    print('Executing tool: ' + Tool.Get_Name().c_str())
    if Tool.Execute() == False:
        print('failed')
        return False
    print('okay')

    List = Tool.Get_Parameter(saga_api.CSG_String('OUTPUT')).asGridList().Get_Grid(0)

    return List


def set_2_latlong(File):
    #_____________________________________
    # Create a new instance of tool 'Set Coordinate Reference System'
    Tool = saga_api.SG_Get_Tool_Library_Manager().Create_Tool('pj_proj4', '0')
    if Tool == None:
        print('Failed to create tool: Set Coordinate Reference System')
        return False

    Tool.Set_Parameter('CRS_PROJ4', '+proj=longlat +datum=WGS84 +no_defs ')
    Tool.Set_Parameter('CRS_FILE', '')
    Tool.Set_Parameter('CRS_EPSG', 4326)
    Tool.Set_Parameter('CRS_EPSG_AUTH', 'EPSG')
    Tool.Set_Parameter('PRECISE', False)
    Tool.Get_Parameter('GRIDS').asList().Add_Item(File)

    print('Executing tool: ' + Tool.Get_Name().c_str())
    if Tool.Execute() == False:
        print('failed')
        return False
    print('okay')

    #_____________________________________
    # Save results to file:
    #Path = os.path.split(File)[0] + os.sep

    return True


def proj_2_template(obj,template):
    #_____________________________________
    # Create a new instance of tool 'Coordinate Transformation (Grid)'
    Tool = saga_api.SG_Get_Tool_Library_Manager().Create_Tool('pj_proj4', '4')
    if Tool == None:
        print('Failed to create tool: Coordinate Transformation (Grid)')
        return False

    Tool.Set_Parameter('CRS_PROJ4', '+proj=stere +lat_0=90 +lat_ts=70 +lon_0=-45 +k=1 +x_0=0 +y_0=0 +datum=WGS84 +units=m +no_defs')
    Tool.Set_Parameter('CRS_FILE', '')
    Tool.Set_Parameter('CRS_EPSG', 4326)
    Tool.Set_Parameter('CRS_EPSG_AUTH', 'EPSG')
    Tool.Set_Parameter('PRECISE', False)
    Tool.Set_Parameter('SOURCE', obj.asGrid())
    Tool.Set_Parameter('RESAMPLING', 0)
    Tool.Set_Parameter('BYTEWISE', False)
    Tool.Set_Parameter('KEEP_TYPE', False)
    Tool.Set_Parameter('TARGET_AREA', False)
    Tool.Set_Parameter('TARGET_DEFINITION', 'user defined')
    Tool.Set_Parameter('TARGET_USER_SIZE', template.Get_Cellsize())
    Tool.Set_Parameter('TARGET_USER_XMIN', template.Get_XMin())
    Tool.Set_Parameter('TARGET_USER_XMAX', template.Get_XMax())
    Tool.Set_Parameter('TARGET_USER_YMIN', template.Get_YMin())
    Tool.Set_Parameter('TARGET_USER_YMAX', template.Get_YMax())
    Tool.Set_Parameter('TARGET_USER_COLS', template.Get_NX())
    Tool.Set_Parameter('TARGET_USER_ROWS', template.Get_NY())
    Tool.Set_Parameter('TARGET_USER_FITS', 'nodes')
    Tool.Set_Parameter('OUT_X_CREATE', False)
    Tool.Set_Parameter('OUT_Y_CREATE', False)

    print('Executing tool: ' + Tool.Get_Name().c_str())
    if Tool.Execute() == False:
        print('failed')
        return False
    print('okay')

    Data = Tool.Get_Parameter('GRID').asGrid()

    return Data


def resample(obj,template):
    #_____________________________________
    # Create a new instance of tool 'Resampling'
    Tool = saga_api.SG_Get_Tool_Library_Manager().Create_Tool('grid_tools', '0')
    if Tool == None:
        print('Failed to create tool: Resampling')
        return False

    Tool.Get_Parameters().Reset_Grid_System()

    Tool.Get_Parameter('INPUT').asList().Add_Item(obj.asGrid())
    Tool.Set_Parameter('KEEP_TYPE', False)
    Tool.Set_Parameter('SCALE_DOWN', 'B-Spline Interpolation')
    Tool.Set_Parameter('TARGET_DEFINITION', 0)
    Tool.Set_Parameter('TARGET_USER_SIZE', template.Get_Cellsize())
    Tool.Set_Parameter('TARGET_USER_XMIN', template.Get_XMin())
    Tool.Set_Parameter('TARGET_USER_XMAX', template.Get_XMax())
    Tool.Set_Parameter('TARGET_USER_YMIN', template.Get_YMin())
    Tool.Set_Parameter('TARGET_USER_YMAX', template.Get_YMax())
    Tool.Set_Parameter('TARGET_USER_COLS', template.Get_NX())
    Tool.Set_Parameter('TARGET_USER_ROWS', template.Get_NY())
    Tool.Set_Parameter('TARGET_USER_FITS', 'nodes')

    print('Executing tool: ' + Tool.Get_Name().c_str())
    if Tool.Execute() == False:
        print('failed')
        return False
    print('okay')

    Data = Tool.Get_Parameter(saga_api.CSG_String('OUTPUT')).asGridList().Get_Grid(0)

    return Data


def export_geotiff(OBJ,outputfile):
    #_____________________________________
    # Create a new instance of tool 'Export GeoTIFF'
    Tool = saga_api.SG_Get_Tool_Library_Manager().Create_Tool('io_gdal', '2')
    if Tool == None:
        print 'Failed to create tool: Export GeoTIFF'
        return False

    Parm = Tool.Get_Parameters()
    Parm.Reset_Grid_System()
    Parm('GRIDS').asList().Add_Item(OBJ)
    Parm('FILE').Set_Value(outputfile)
    Parm('OPTIONS').Set_Value('COMPRESS=DEFLATE PREDICTOR=2')

    print 'Executing tool: ' + Tool.Get_Name().c_str()
    if Tool.Execute() == False:
        print 'failed'
        return False
    print 'okay - geotiff created'

    #_____________________________________
    # remove this tool instance, if you don't need it anymore
    saga_api.SG_Get_Tool_Library_Manager().Delete_Tool(Tool)

    return True


def lapse_rate_based_downscaling(dem, lapse, reference_dem, temperature):
    #_____________________________________
    # Create a new instance of tool 'Grid Calculator'
    Tool = saga_api.SG_Get_Tool_Library_Manager().Create_Tool('grid_calculus', '1')
    if Tool == None:
        print('Failed to create tool: Grid Calculator')
        return False

    Tool.Get_Parameters().Reset_Grid_System()

    Tool.Set_Parameter('RESAMPLING', 'B-Spline Interpolation')
    Tool.Set_Parameter('FORMULA', 'd+b*(a-c)')
    Tool.Set_Parameter('NAME', 'tas')
    Tool.Set_Parameter('FNAME', False)
    Tool.Set_Parameter('USE_NODATA', False)
    Tool.Set_Parameter('TYPE', 7)
    Tool.Set_Parameter('RESAMPLING', 2)
    Tool.Get_Parameter('GRIDS').asList().Add_Item(dem.asGrid())
    Tool.Get_Parameter('XGRIDS').asList().Add_Item(lapse.asGrid())
    Tool.Get_Parameter('XGRIDS').asList().Add_Item(reference_dem.asGrid())
    Tool.Get_Parameter('XGRIDS').asList().Add_Item(temperature.asGrid())

    print('Executing tool: ' + Tool.Get_Name().c_str())
    if Tool.Execute() == False:
        print('failed')
        return False
    print('okay')

    #_____________________________________
    # Save results to file:
    Data = Tool.Get_Parameter('RESULT').asGrid()

    return Data


def temp_srad_cc_correction(temperature, quotient, cloud_cover, name):
    #_____________________________________
    # Create a new instance of tool 'Grid Calculator'
    Tool = saga_api.SG_Get_Tool_Library_Manager().Create_Tool('grid_calculus', '1')
    if Tool == None:
        print('Failed to create tool: Grid Calculator')
        return False

    Tool.Get_Parameters().Reset_Grid_System()

    Tool.Set_Parameter('RESAMPLING', 'B-Spline Interpolation')
    Tool.Set_Parameter('FORMULA', 'a+(b-1/b)*(1-c)')
    Tool.Set_Parameter('NAME', name)
    Tool.Set_Parameter('FNAME', False)
    Tool.Set_Parameter('USE_NODATA', False)
    Tool.Set_Parameter('TYPE', 7)
    Tool.Get_Parameter('GRIDS').asList().Add_Item(temperature.asGrid())
    Tool.Get_Parameter('GRIDS').asList().Add_Item(quotient.asGrid())
    Tool.Get_Parameter('XGRIDS').asList().Add_Item(cloud_cover.asGrid())

    print('Executing tool: ' + Tool.Get_Name().c_str())
    if Tool.Execute() == False:
        print('failed')
        return False
    print('okay')

    #_____________________________________
    # Save results to file:
    Data = Tool.Get_Parameter('RESULT').asGrid()

    return Data


def tlapse(z1,z2,t1,t2,equ):
    #_____________________________________
    # Create a new instance of tool 'Grid Calculator'
    Tool = saga_api.SG_Get_Tool_Library_Manager().Create_Tool('grid_calculus', '1')
    if Tool == None:
        print('Failed to create tool: Grid Calculator')
        return False

    Tool.Get_Parameters().Reset_Grid_System()

    Tool.Set_Parameter('RESAMPLING', 3)
    Tool.Set_Parameter('FORMULA', equ)
    Tool.Set_Parameter('NAME', 'Calculation')
    Tool.Set_Parameter('FNAME', False)
    Tool.Set_Parameter('USE_NODATA', False)
    Tool.Set_Parameter('TYPE', 7)
    Tool.Get_Parameter('GRIDS').asList().Add_Item(z1.asGrid())
    Tool.Get_Parameter('GRIDS').asList().Add_Item(z2.asGrid())
    Tool.Get_Parameter('GRIDS').asList().Add_Item(t1.asGrid())
    Tool.Get_Parameter('GRIDS').asList().Add_Item(t2.asGrid())

    print('Executing tool: ' + Tool.Get_Name().c_str())
    if Tool.Execute() == False:
        print('failed')
        return False
    print('okay')

    Data = Tool.Get_Parameter('RESULT').asGrid()

    return Data


def gridvalues_to_points(obj):
    #_____________________________________
    # Create a new instance of tool 'Grid Values to Points'
    Tool = saga_api.SG_Get_Tool_Library_Manager().Create_Tool('shapes_grid', '3')
    if Tool == None:
        print('Failed to create tool: Grid Values to Points')
        return False

    Tool.Get_Parameters().Reset_Grid_System()

    Tool.Get_Parameter('GRIDS').asList().Add_Item(obj.asGrid())
    Tool.Set_Parameter('POLYGONS', 'Shapes input, optional')
    Tool.Set_Parameter('NODATA', True)
    Tool.Set_Parameter('TYPE', 'nodes')

    print('Executing tool: ' + Tool.Get_Name().c_str())
    if Tool.Execute() == False:
        print('failed')
        return False
    print('okay')

    Data = Tool.Get_Parameter(saga_api.CSG_String('SHAPES')).asShapes()

    return Data


def reproject_shape(obj,template):
    #_____________________________________
    # Create a new instance of tool 'Coordinate Transformation (Shapes)'
    Tool = saga_api.SG_Get_Tool_Library_Manager().Create_Tool('pj_proj4', '2')
    if Tool == None:
        print('Failed to create tool: Coordinate Transformation (Shapes)')
        return False

    Tool.Set_Parameter('CRS_PROJ4', template.Get_Projection().Get_Proj4().c_str())
    Tool.Set_Parameter('CRS_FILE', '')
    Tool.Set_Parameter('CRS_EPSG', '')
    Tool.Set_Parameter('CRS_EPSG_AUTH', 'EPSG')
    Tool.Set_Parameter('PRECISE', False)
    Tool.Set_Parameter('SOURCE', obj)
    Tool.Set_Parameter('TRANSFORM_Z', True)
    Tool.Set_Parameter('COPY', True)

    print('Executing tool: ' + Tool.Get_Name().c_str())
    if Tool.Execute() == False:
        print('failed')
        return False
    print('okay')

    #_____________________________________

    Data = Tool.Get_Parameter('TARGET').asShapes()

    return Data


def proj_2_latlong(obj,template):
    #_____________________________________
    # Create a new instance of tool 'Coordinate Transformation (Grid)'
    Tool = saga_api.SG_Get_Tool_Library_Manager().Create_Tool('pj_proj4', '4')
    if Tool == None:
        print('Failed to create tool: Coordinate Transformation (Grid)')
        return False

    Tool.Set_Parameter('CRS_PROJ4', '+proj=longlat +datum=WGS84 +no_defs ')
    Tool.Set_Parameter('CRS_FILE', '')
    Tool.Set_Parameter('CRS_EPSG', 4326)
    Tool.Set_Parameter('CRS_EPSG_AUTH', 'EPSG')
    Tool.Set_Parameter('PRECISE', False)
    Tool.Set_Parameter('SOURCE', obj.asGrid())
    Tool.Set_Parameter('RESAMPLING', 0)
    Tool.Set_Parameter('BYTEWISE', False)
    Tool.Set_Parameter('KEEP_TYPE', False)
    Tool.Set_Parameter('TARGET_AREA', False)
    Tool.Set_Parameter('TARGET_DEFINITION', 'user defined')
    Tool.Set_Parameter('TARGET_USER_SIZE', template.Get_Cellsize())
    Tool.Set_Parameter('TARGET_USER_XMIN', template.Get_XMin())
    Tool.Set_Parameter('TARGET_USER_XMAX', template.Get_XMax())
    Tool.Set_Parameter('TARGET_USER_YMIN', template.Get_YMin())
    Tool.Set_Parameter('TARGET_USER_YMAX', template.Get_YMax())
    Tool.Set_Parameter('TARGET_USER_COLS', template.Get_NX())
    Tool.Set_Parameter('TARGET_USER_ROWS', template.Get_NY())
    Tool.Set_Parameter('TARGET_USER_FITS', 'nodes')
    Tool.Set_Parameter('OUT_X_CREATE', False)
    Tool.Set_Parameter('OUT_Y_CREATE', False)

    print('Executing tool: ' + Tool.Get_Name().c_str())
    if Tool.Execute() == False:
        print('failed')
        return False
    print('okay')

    Data = Tool.Get_Parameter('GRID').asGrid()

    return Data


def clip_grid(obj,template,buffer):
    Tool = saga_api.SG_Get_Tool_Library_Manager().Create_Tool('grid_tools', '31')
    if Tool == None:
        print('Failed to create tool: Clip Grids')
        return False

    Tool.Get_Parameters().Reset_Grid_System()

    Tool.Get_Parameter('GRIDS').asList().Add_Item(obj.asGrid())
    Tool.Set_Parameter('EXTENT', 1)
    Tool.Set_Parameter('GRIDSYSTEM', template.Get_System())
    Tool.Set_Parameter('INTERIOR', False)
    Tool.Set_Parameter('BUFFER', buffer)

    print('Executing tool: ' + Tool.Get_Name().c_str())
    if Tool.Execute() == False:
        print('failed')
        return False
    print('okay')

    List = Tool.Get_Parameter('CLIPPED').asGridList().Get_Grid(0)

    return List


def multilevel_B_spline(shape, template):
    #_____________________________________
    # Create a new instance of tool 'Multilevel B-Spline'
    Tool = saga_api.SG_Get_Tool_Library_Manager().Create_Tool('grid_spline', '4')
    if Tool == None:
        print('Failed to create tool: Multilevel B-Spline')
        return False

    Tool.Set_Parameter('SHAPES', shape)
    Tool.Set_Parameter('FIELD', 3)
    Tool.Set_Parameter('TARGET_DEFINITION', 'user defined')
    Tool.Set_Parameter('TARGET_USER_SIZE', template.Get_Cellsize())
    Tool.Set_Parameter('TARGET_USER_XMIN', template.Get_XMin())
    Tool.Set_Parameter('TARGET_USER_XMAX', template.Get_XMax())
    Tool.Set_Parameter('TARGET_USER_YMIN', template.Get_YMin())
    Tool.Set_Parameter('TARGET_USER_YMAX', template.Get_YMax())
    Tool.Set_Parameter('TARGET_USER_COLS', template.Get_NX())
    Tool.Set_Parameter('TARGET_USER_ROWS', template.Get_NY())
    Tool.Set_Parameter('TARGET_USER_FITS', 'nodes')
    Tool.Set_Parameter('METHOD', 'no')
    Tool.Set_Parameter('EPSILON', 0.000100)
    Tool.Set_Parameter('LEVEL_MAX', 14)

    print('Executing tool: ' + Tool.Get_Name().c_str())
    if Tool.Execute() == False:
        print('failed')
        return False
    print('okay')

    Parm = Tool.Get_Parameters()
    Data  = Parm('TARGET_OUT_GRID').asGrid()

    return Data


def triangulation(shp,template):
    #_____________________________________
    # Create a new instance of tool 'Triangulation'
    Tool = saga_api.SG_Get_Tool_Library_Manager().Create_Tool('grid_gridding', '5')
    if Tool == None:
        print('Failed to create tool: Triangulation')
        return False

    Tool.Set_Parameter('POINTS', shp)
    Tool.Set_Parameter('FIELD', 4)
    Tool.Set_Parameter('TARGET_DEFINITION', 0)
    Tool.Set_Parameter('TARGET_USER_SIZE', template.Get_Cellsize())
    Tool.Set_Parameter('TARGET_USER_XMIN', template.Get_XMin())
    Tool.Set_Parameter('TARGET_USER_XMAX', template.Get_XMax())
    Tool.Set_Parameter('TARGET_USER_YMIN', template.Get_YMin())
    Tool.Set_Parameter('TARGET_USER_YMAX', template.Get_YMax())
    Tool.Set_Parameter('TARGET_USER_COLS', template.Get_NX())
    Tool.Set_Parameter('TARGET_USER_ROWS', template.Get_NY())
    Tool.Set_Parameter('FRAME', False)

    print('Executing tool: ' + Tool.Get_Name().c_str())
    if Tool.Execute() == False:
        print('failed')
        return False
    print('okay')
    Data = Tool.Get_Parameter('TARGET_OUT_GRID').asGrid()
    return Data


def srad(DEM):
    #_____________________________________
    # Create a new instance of tool 'Potential Incoming Solar Radiation'
    Tool = saga_api.SG_Get_Tool_Library_Manager().Create_Tool('ta_lighting', '2')
    if Tool == None:
        print('Failed to create tool: Potential Incoming Solar Radiation')
        return False

    Tool.Get_Parameters().Reset_Grid_System()

    Tool.Set_Parameter('GRD_DEM', DEM.asGrid())
    Tool.Set_Parameter('GRD_SVF', 'Grid input, optional')
    Tool.Set_Parameter('GRD_VAPOUR', 'Grid input, optional')
    Tool.Set_Parameter('GRD_VAPOUR_DEFAULT', 10.000000)
    Tool.Set_Parameter('GRD_LINKE', 'Grid input, optional')
    Tool.Set_Parameter('GRD_LINKE_DEFAULT', 3.000000)
    Tool.Set_Parameter('GRD_TOTAL', saga_api.SG_Get_Create_Pointer()) # optional output, remove this line, if you don't want to create it
    Tool.Set_Parameter('GRD_RATIO', saga_api.SG_Get_Create_Pointer()) # optional output, remove this line, if you don't want to create it
    Tool.Set_Parameter('GRD_FLAT', saga_api.SG_Get_Create_Pointer()) # optional output, remove this line, if you don't want to create it
    Tool.Set_Parameter('GRD_DURATION', saga_api.SG_Get_Create_Pointer()) # optional output, remove this line, if you don't want to create it
    Tool.Set_Parameter('GRD_SUNRISE', saga_api.SG_Get_Create_Pointer()) # optional output, remove this line, if you don't want to create it
    Tool.Set_Parameter('GRD_SUNSET', saga_api.SG_Get_Create_Pointer()) # optional output, remove this line, if you don't want to create it
    Tool.Set_Parameter('SOLARCONST', 1367.000000)
    Tool.Set_Parameter('LOCALSVF', True)
    Tool.Set_Parameter('UNITS',0)
    Tool.Set_Parameter('SHADOW', 1)
    Tool.Set_Parameter('LOCATION', 1)
    Tool.Set_Parameter('PERIOD', 0)
    Tool.Set_Parameter('DAY', year + '-' + month + '-' + day)
    Tool.Set_Parameter('DAY_STOP', year + '-' + month + '-' + day)
    Tool.Set_Parameter('DAYS_STEP', 1)
    Tool.Set_Parameter('HOUR_RANGE.MIN', float(hour))
    Tool.Set_Parameter('HOUR_RANGE.MAX', float(hour)+1)
    Tool.Set_Parameter('MOMENT', float(hour))
    Tool.Set_Parameter('HOUR_STEP', 1)
    Tool.Set_Parameter('METHOD', 3)
    Tool.Set_Parameter('ATMOSPHERE', 12000.000000)
    Tool.Set_Parameter('PRESSURE', 1013.000000)
    Tool.Set_Parameter('WATER', 1.680000)
    Tool.Set_Parameter('DUST', 100.000000)
    Tool.Set_Parameter('LUMPED', 80.000000)

    print('Executing tool: ' + Tool.Get_Name().c_str())
    if Tool.Execute() == False:
        print('failed')
        return False
    print('okay')

    #_____________________________________
    # Save results to file:

    Data1 = Tool.Get_Parameter('GRD_TOTAL').asDataObject()

    Data2 = Tool.Get_Parameter('GRD_FLAT').asDataObject()

    return Data1, Data2


def grid_calculator(obj1,obj2,equ):
    #_____________________________________
    # Create a new instance of tool 'Grid Calculator'
    Tool = saga_api.SG_Get_Tool_Library_Manager().Create_Tool('grid_calculus', '1')
    if Tool == None:
        print('Failed to create tool: Grid Calculator')
        return False

    Tool.Get_Parameters().Reset_Grid_System()

    Tool.Set_Parameter('RESAMPLING', 'B-Spline Interpolation')
    Tool.Set_Parameter('FORMULA', equ)
    Tool.Set_Parameter('NAME', 'Calculation')
    Tool.Set_Parameter('FNAME', False)
    Tool.Set_Parameter('USE_NODATA', False)
    Tool.Set_Parameter('TYPE', 7)
    Tool.Get_Parameter('GRIDS').asList().Add_Item(obj1.asGrid())
    Tool.Get_Parameter('GRIDS').asList().Add_Item(obj2.asGrid())

    print('Executing tool: ' + Tool.Get_Name().c_str())
    if Tool.Execute() == False:
        print('failed')
        return False
    print('okay')

    Data = Tool.Get_Parameter('RESULT').asGrid()

    return Data


def calc_LST(rsds,T_air,T_sky,albedo):
    #_____________________________________
    # Create a new instance of tool 'Land Surface Temperature'
    Tool = saga_api.SG_Get_Tool_Library_Manager().Create_Tool('climate_tools', '28')
    if Tool == None:
        print('Failed to create tool: Land Surface Temperature')
        return False

    Tool.Get_Parameters().Reset_Grid_System()

    Tool.Set_Parameter('IRRADIANCE', rsds.asGrid())
    Tool.Set_Parameter('ALBEDO', albedo.asGrid())
    Tool.Set_Parameter('EMISSIVITY', 'Grid input, optional')
    Tool.Set_Parameter('EMISSIVITY_DEFAULT', 0.75000)
    Tool.Set_Parameter('CONVECTION', 'Grid input, optional')
    Tool.Set_Parameter('CONVECTION_DEFAULT', 15.000000)
    Tool.Set_Parameter('T_AIR', T_air.asGrid())
    Tool.Set_Parameter('T_SKY', T_sky.asGrid())
    Tool.Set_Parameter('T_INITIAL', T_air.asGrid())
    Tool.Set_Parameter('UNIT', 0)
    Tool.Set_Parameter('ITERATIONS', 100)

    print('Executing tool: ' + Tool.Get_Name().c_str())
    if Tool.Execute() == False:
        print('failed')
        return False
    print('okay')

    Data = Tool.Get_Parameter('LST').asGrid()

    return Data


