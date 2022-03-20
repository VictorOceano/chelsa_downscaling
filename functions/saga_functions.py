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
#along with chelsa_highres.  If not, see <https://www.gnu.org/licenses/>.


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


#!/usr/bin/env python

#This file is part of chelsa_isimip3b_ba_1km.
#
#chelsa_isimip3b_ba_1km is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.

#chelsa_isimip3b_ba_1km is distributed in the hope that it will be useful,
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

# ********************************************************
# Define functions needed for the calculations
# ********************************************************
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

    if Tool.Execute() == False:
        print 'failed'
        return False

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
    Parm('TRANSFORM').Set_Value(False)
    Parm('RESAMPLING').Set_Value('Nearest Neighbour')

    if Tool.Execute() == False:
        print 'failed'
        return False

    #_____________________________________

    output = Tool.Get_Parameter(saga_api.CSG_String('GRIDS')).asGridList()
    return output


def polynomial_trends(File1,File2):
    #_____________________________________
    # Create a new instance of tool 'Polynomial Trend from Grids'
    Tool = saga_api.SG_Get_Tool_Library_Manager().Create_Tool('statistics_regression', '9')
    if Tool == None:
        print('Failed to create tool: Polynomial Trend from Grids')
        return False

    Tool.Get_Parameters().Reset_Grid_System()

    Tool.Get_Parameter('Y_GRIDS').asList().Add_Item(File1.asGridList().Get_Grid(0))
    Tool.Get_Parameter('Y_GRIDS').asList().Add_Item(File1.asGridList().Get_Grid(1))
    Tool.Get_Parameter('Y_GRIDS').asList().Add_Item(File1.asGridList().Get_Grid(2))
    Tool.Get_Parameter('Y_GRIDS').asList().Add_Item(File1.asGridList().Get_Grid(3))
    Tool.Get_Parameter('Y_GRIDS').asList().Add_Item(File1.asGridList().Get_Grid(4))
    Tool.Get_Parameter('Y_GRIDS').asList().Add_Item(File1.asGridList().Get_Grid(5))
    Tool.Get_Parameter('Y_GRIDS').asList().Add_Item(File1.asGridList().Get_Grid(6))
    Tool.Get_Parameter('Y_GRIDS').asList().Add_Item(File1.asGridList().Get_Grid(7))
    Tool.Get_Parameter('Y_GRIDS').asList().Add_Item(File1.asGridList().Get_Grid(8))
    Tool.Get_Parameter('Y_GRIDS').asList().Add_Item(File1.asGridList().Get_Grid(9))
    Tool.Get_Parameter('Y_GRIDS').asList().Add_Item(File1.asGridList().Get_Grid(10))

    Tool.Set_Parameter('R2', saga_api.SG_Get_Create_Pointer()) # optional output, remove this line, if you don't want to create it
    Tool.Set_Parameter('ORDER', 1)
    Tool.Get_Parameter('X_GRIDS').asList().Add_Item(File2.asGridList().Get_Grid(0))
    Tool.Get_Parameter('X_GRIDS').asList().Add_Item(File2.asGridList().Get_Grid(1))
    Tool.Get_Parameter('X_GRIDS').asList().Add_Item(File2.asGridList().Get_Grid(2))
    Tool.Get_Parameter('X_GRIDS').asList().Add_Item(File2.asGridList().Get_Grid(3))
    Tool.Get_Parameter('X_GRIDS').asList().Add_Item(File2.asGridList().Get_Grid(4))
    Tool.Get_Parameter('X_GRIDS').asList().Add_Item(File2.asGridList().Get_Grid(5))
    Tool.Get_Parameter('X_GRIDS').asList().Add_Item(File2.asGridList().Get_Grid(6))
    Tool.Get_Parameter('X_GRIDS').asList().Add_Item(File2.asGridList().Get_Grid(7))
    Tool.Get_Parameter('X_GRIDS').asList().Add_Item(File2.asGridList().Get_Grid(8))
    Tool.Get_Parameter('X_GRIDS').asList().Add_Item(File2.asGridList().Get_Grid(9))
    Tool.Get_Parameter('X_GRIDS').asList().Add_Item(File2.asGridList().Get_Grid(10))

    print('Executing tool: ' + Tool.Get_Name().c_str())
    if Tool.Execute() == False:
        print('failed')
        return False
    print('okay')

    #_____________________________________
    # Save results to file:

    List = Tool.Get_Parameter(saga_api.CSG_String('COEFF')).asGridList().Get_Grid(1)
    #_____________________________________

    return List


def extreme_lapserates(extreme,param,dict,times,param2):
    #_____________________________________
    # Create a new instance of tool 'Temperature Lapse Rates'
    Tool = saga_api.SG_Get_Tool_Library_Manager().Create_Tool('climate_tools', '26')
    if Tool == None:
        print('Failed to create tool: Temperature Lapse Rates')
        return False

    Tool.Get_Parameters().Reset_Grid_System()

    Tool.Get_Parameter('TEMP').asList().Add_Item(dict['lapse00:00'])
    Tool.Get_Parameter('TEMP').asList().Add_Item(dict['lapse01:00'])
    Tool.Get_Parameter('TEMP').asList().Add_Item(dict['lapse02:00'])
    Tool.Get_Parameter('TEMP').asList().Add_Item(dict['lapse03:00'])
    Tool.Get_Parameter('TEMP').asList().Add_Item(dict['lapse04:00'])
    Tool.Get_Parameter('TEMP').asList().Add_Item(dict['lapse05:00'])
    Tool.Get_Parameter('TEMP').asList().Add_Item(dict['lapse06:00'])
    Tool.Get_Parameter('TEMP').asList().Add_Item(dict['lapse07:00'])
    Tool.Get_Parameter('TEMP').asList().Add_Item(dict['lapse08:00'])
    Tool.Get_Parameter('TEMP').asList().Add_Item(dict['lapse09:00'])
    Tool.Get_Parameter('TEMP').asList().Add_Item(dict['lapse10:00'])
    Tool.Get_Parameter('TEMP').asList().Add_Item(dict['lapse11:00'])
    Tool.Get_Parameter('TEMP').asList().Add_Item(dict['lapse12:00'])
    Tool.Get_Parameter('TEMP').asList().Add_Item(dict['lapse13:00'])
    Tool.Get_Parameter('TEMP').asList().Add_Item(dict['lapse14:00'])
    Tool.Get_Parameter('TEMP').asList().Add_Item(dict['lapse15:00'])
    Tool.Get_Parameter('TEMP').asList().Add_Item(dict['lapse16:00'])
    Tool.Get_Parameter('TEMP').asList().Add_Item(dict['lapse17:00'])
    Tool.Get_Parameter('TEMP').asList().Add_Item(dict['lapse18:00'])
    Tool.Get_Parameter('TEMP').asList().Add_Item(dict['lapse19:00'])
    Tool.Get_Parameter('TEMP').asList().Add_Item(dict['lapse20:00'])
    Tool.Get_Parameter('TEMP').asList().Add_Item(dict['lapse21:00'])
    Tool.Get_Parameter('TEMP').asList().Add_Item(dict['lapse22:00'])
    Tool.Get_Parameter('TEMP').asList().Add_Item(dict['lapse23:00'])

    #for ngrid in range(0,extreme.Get_Grid_Count()-1):

    Tool.Get_Parameter('TGROUND').asList().Add_Item(extreme.asGridList().Get_Grid(0))
    Tool.Get_Parameter('TGROUND').asList().Add_Item(extreme.asGridList().Get_Grid(1))
    Tool.Get_Parameter('TGROUND').asList().Add_Item(extreme.asGridList().Get_Grid(2))
    Tool.Get_Parameter('TGROUND').asList().Add_Item(extreme.asGridList().Get_Grid(3))
    Tool.Get_Parameter('TGROUND').asList().Add_Item(extreme.asGridList().Get_Grid(4))
    Tool.Get_Parameter('TGROUND').asList().Add_Item(extreme.asGridList().Get_Grid(5))
    Tool.Get_Parameter('TGROUND').asList().Add_Item(extreme.asGridList().Get_Grid(6))
    Tool.Get_Parameter('TGROUND').asList().Add_Item(extreme.asGridList().Get_Grid(7))
    Tool.Get_Parameter('TGROUND').asList().Add_Item(extreme.asGridList().Get_Grid(8))
    Tool.Get_Parameter('TGROUND').asList().Add_Item(extreme.asGridList().Get_Grid(9))
    Tool.Get_Parameter('TGROUND').asList().Add_Item(extreme.asGridList().Get_Grid(10))
    Tool.Get_Parameter('TGROUND').asList().Add_Item(extreme.asGridList().Get_Grid(11))
    Tool.Get_Parameter('TGROUND').asList().Add_Item(extreme.asGridList().Get_Grid(12))
    Tool.Get_Parameter('TGROUND').asList().Add_Item(extreme.asGridList().Get_Grid(13))
    Tool.Get_Parameter('TGROUND').asList().Add_Item(extreme.asGridList().Get_Grid(14))
    Tool.Get_Parameter('TGROUND').asList().Add_Item(extreme.asGridList().Get_Grid(15))
    Tool.Get_Parameter('TGROUND').asList().Add_Item(extreme.asGridList().Get_Grid(16))
    Tool.Get_Parameter('TGROUND').asList().Add_Item(extreme.asGridList().Get_Grid(17))
    Tool.Get_Parameter('TGROUND').asList().Add_Item(extreme.asGridList().Get_Grid(18))
    Tool.Get_Parameter('TGROUND').asList().Add_Item(extreme.asGridList().Get_Grid(19))
    Tool.Get_Parameter('TGROUND').asList().Add_Item(extreme.asGridList().Get_Grid(20))
    Tool.Get_Parameter('TGROUND').asList().Add_Item(extreme.asGridList().Get_Grid(21))
    Tool.Get_Parameter('TGROUND').asList().Add_Item(extreme.asGridList().Get_Grid(22))
    Tool.Get_Parameter('TGROUND').asList().Add_Item(extreme.asGridList().Get_Grid(23))

    Tool.Set_Parameter('EXTREME', param) # 'maximum' or 'minimum'

    print('Executing tool: ' + Tool.Get_Name().c_str())
    if Tool.Execute() == False:
        print('failed')
        return False
    print('okay')

    if param2 == 0:
        Data = Tool.Get_Parameter('LAPSE').asDataObject()
    if param2 == 1:
        Data = Tool.Get_Parameter('TEXTREME').asDataObject()
    if param2 == 2:
        Data = Tool.Get_Parameter('TIME').asDataObject()

    return Data


def get_mean_dicto(dict,times):
    #_____________________________________
    # Create a new instance of tool 'Statistics for Grids'
    Tool = saga_api.SG_Get_Tool_Library_Manager().Create_Tool('statistics_grid', '4')
    if Tool == None:
        print('Failed to create tool: Statistics for Grids')
        return False

    Tool.Get_Parameters().Reset_Grid_System()

    for timestamp in times:
        Tool.Get_Parameter('GRIDS').asList().Add_Item(dict['lapse'+timestamp])

    Tool.Set_Parameter('RESAMPLING', 'B-Spline Interpolation')
    Tool.Set_Parameter('MEAN', saga_api.SG_Get_Create_Pointer()) # optional output, remove this line, if you don't want to create it

    print('Executing tool: ' + Tool.Get_Name().c_str())
    if Tool.Execute() == False:
        print('failed')
        return False
    print('okay')

    Parm = Tool.Get_Parameters()
    Data = Parm('MEAN').asGrid()

    return Data


def get_mean(obj):
    #_____________________________________
    # Create a new instance of tool 'Statistics for Grids'
    Tool = saga_api.SG_Get_Tool_Library_Manager().Create_Tool('statistics_grid', '4')
    if Tool == None:
        print('Failed to create tool: Statistics for Grids')
        return False

    Tool.Get_Parameters().Reset_Grid_System()

    Tool.Get_Parameter('GRIDS').asList().Add_Item(obj.asGridList().Get_Grid(0))
    Tool.Get_Parameter('GRIDS').asList().Add_Item(obj.asGridList().Get_Grid(1))
    Tool.Get_Parameter('GRIDS').asList().Add_Item(obj.asGridList().Get_Grid(2))
    Tool.Get_Parameter('GRIDS').asList().Add_Item(obj.asGridList().Get_Grid(3))
    Tool.Get_Parameter('GRIDS').asList().Add_Item(obj.asGridList().Get_Grid(4))
    Tool.Get_Parameter('GRIDS').asList().Add_Item(obj.asGridList().Get_Grid(5))
    Tool.Get_Parameter('GRIDS').asList().Add_Item(obj.asGridList().Get_Grid(6))
    Tool.Get_Parameter('GRIDS').asList().Add_Item(obj.asGridList().Get_Grid(7))
    Tool.Get_Parameter('GRIDS').asList().Add_Item(obj.asGridList().Get_Grid(8))
    Tool.Get_Parameter('GRIDS').asList().Add_Item(obj.asGridList().Get_Grid(9))
    Tool.Get_Parameter('GRIDS').asList().Add_Item(obj.asGridList().Get_Grid(10))
    Tool.Get_Parameter('GRIDS').asList().Add_Item(obj.asGridList().Get_Grid(11))
    Tool.Get_Parameter('GRIDS').asList().Add_Item(obj.asGridList().Get_Grid(12))
    Tool.Get_Parameter('GRIDS').asList().Add_Item(obj.asGridList().Get_Grid(13))
    Tool.Get_Parameter('GRIDS').asList().Add_Item(obj.asGridList().Get_Grid(14))
    Tool.Get_Parameter('GRIDS').asList().Add_Item(obj.asGridList().Get_Grid(15))
    Tool.Get_Parameter('GRIDS').asList().Add_Item(obj.asGridList().Get_Grid(16))
    Tool.Get_Parameter('GRIDS').asList().Add_Item(obj.asGridList().Get_Grid(17))
    Tool.Get_Parameter('GRIDS').asList().Add_Item(obj.asGridList().Get_Grid(18))
    Tool.Get_Parameter('GRIDS').asList().Add_Item(obj.asGridList().Get_Grid(19))
    Tool.Get_Parameter('GRIDS').asList().Add_Item(obj.asGridList().Get_Grid(20))
    Tool.Get_Parameter('GRIDS').asList().Add_Item(obj.asGridList().Get_Grid(21))
    Tool.Get_Parameter('GRIDS').asList().Add_Item(obj.asGridList().Get_Grid(22))
    Tool.Get_Parameter('GRIDS').asList().Add_Item(obj.asGridList().Get_Grid(23))

    Tool.Set_Parameter('RESAMPLING', 'B-Spline Interpolation')
    Tool.Set_Parameter('MEAN', saga_api.SG_Get_Create_Pointer()) # optional output, remove this line, if you don't want to create it

    print('Executing tool: ' + Tool.Get_Name().c_str())
    if Tool.Execute() == False:
        print('failed')
        return False
    print('okay')

    Parm = Tool.Get_Parameters()
    Data = Parm('MEAN').asGrid()

    return Data


def get_sum(obj):
    #_____________________________________
    # Create a new instance of tool 'Statistics for Grids'
    Tool = saga_api.SG_Get_Tool_Library_Manager().Create_Tool('statistics_grid', '4')
    if Tool == None:
        print('Failed to create tool: Statistics for Grids')
        return False

    Tool.Get_Parameters().Reset_Grid_System()

    Tool.Get_Parameter('GRIDS').asList().Add_Item(obj.asGridList().Get_Grid(0))
    Tool.Get_Parameter('GRIDS').asList().Add_Item(obj.asGridList().Get_Grid(1))
    Tool.Get_Parameter('GRIDS').asList().Add_Item(obj.asGridList().Get_Grid(2))
    Tool.Get_Parameter('GRIDS').asList().Add_Item(obj.asGridList().Get_Grid(3))
    Tool.Get_Parameter('GRIDS').asList().Add_Item(obj.asGridList().Get_Grid(4))
    Tool.Get_Parameter('GRIDS').asList().Add_Item(obj.asGridList().Get_Grid(5))
    Tool.Get_Parameter('GRIDS').asList().Add_Item(obj.asGridList().Get_Grid(6))
    Tool.Get_Parameter('GRIDS').asList().Add_Item(obj.asGridList().Get_Grid(7))
    Tool.Get_Parameter('GRIDS').asList().Add_Item(obj.asGridList().Get_Grid(8))
    Tool.Get_Parameter('GRIDS').asList().Add_Item(obj.asGridList().Get_Grid(9))
    Tool.Get_Parameter('GRIDS').asList().Add_Item(obj.asGridList().Get_Grid(10))
    Tool.Get_Parameter('GRIDS').asList().Add_Item(obj.asGridList().Get_Grid(11))
    Tool.Get_Parameter('GRIDS').asList().Add_Item(obj.asGridList().Get_Grid(12))
    Tool.Get_Parameter('GRIDS').asList().Add_Item(obj.asGridList().Get_Grid(13))
    Tool.Get_Parameter('GRIDS').asList().Add_Item(obj.asGridList().Get_Grid(14))
    Tool.Get_Parameter('GRIDS').asList().Add_Item(obj.asGridList().Get_Grid(15))
    Tool.Get_Parameter('GRIDS').asList().Add_Item(obj.asGridList().Get_Grid(16))
    Tool.Get_Parameter('GRIDS').asList().Add_Item(obj.asGridList().Get_Grid(17))
    Tool.Get_Parameter('GRIDS').asList().Add_Item(obj.asGridList().Get_Grid(18))
    Tool.Get_Parameter('GRIDS').asList().Add_Item(obj.asGridList().Get_Grid(19))
    Tool.Get_Parameter('GRIDS').asList().Add_Item(obj.asGridList().Get_Grid(20))
    Tool.Get_Parameter('GRIDS').asList().Add_Item(obj.asGridList().Get_Grid(21))
    Tool.Get_Parameter('GRIDS').asList().Add_Item(obj.asGridList().Get_Grid(22))
    Tool.Get_Parameter('GRIDS').asList().Add_Item(obj.asGridList().Get_Grid(23))

    Tool.Set_Parameter('RESAMPLING', 'B-Spline Interpolation')
    Tool.Set_Parameter('SUM', saga_api.SG_Get_Create_Pointer()) # optional output, remove this line, if you don't want to create it

    print('Executing tool: ' + Tool.Get_Name().c_str())
    if Tool.Execute() == False:
        print('failed')
        return False
    print('okay')

    Parm = Tool.Get_Parameters()
    Data = Parm('SUM').asGrid()

    return Data


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

    if Tool.Execute() == False:
        print('failed')
        return False

    List = Tool.Get_Parameter(saga_api.CSG_String('OUTPUT')).asGridList().Get_Grid(0)

    return List


def change_latlong360(obj,direction):
    #_____________________________________
    # Create a new instance of tool 'Change Longitudinal Range for Grids'
    Tool = saga_api.SG_Get_Tool_Library_Manager().Create_Tool('pj_proj4', '13')
    if Tool == None:
        print('Failed to create tool: Change Longitudinal Range for Grids')
        return False

    Tool.Get_Parameters().Reset_Grid_System()

    Tool.Get_Parameter('INPUT').asList().Add_Item(obj.asGrid())
    Tool.Set_Parameter('DIRECTION', direction)
    Tool.Set_Parameter('PATCH', True)

    print('Executing tool: ' + Tool.Get_Name().c_str())
    if Tool.Execute() == False:
        print('failed')
        return False
    print('okay')

    List = Tool.Get_Parameter(saga_api.CSG_String('OUTPUT')).asGridList().Get_Grid(0)

    return List


def set_2_latlong(obj):
    #_____________________________________
    # Create a new instance of tool 'Set Coordinate Reference System'
    Tool = saga_api.SG_Get_Tool_Library_Manager().Create_Tool('pj_proj4', '0')
    if Tool == None:
        print('Failed to create tool: Set Coordinate Reference System')
        return False

    Tool.Set_Parameter('CRS_METHOS', 0)
    Tool.Set_Parameter('CRS_PROJ4', '+proj=longlat +datum=WGS84 +no_defs ')
    Tool.Set_Parameter('CRS_FILE', '')
    Tool.Set_Parameter('CRS_EPSG', 4326)
    Tool.Set_Parameter('CRS_EPSG_AUTH', 'EPSG')
    Tool.Set_Parameter('PRECISE', False)
    Tool.Get_Parameter('GRIDS').asList().Add_Item(obj.asGrid())

    print('Executing tool: ' + Tool.Get_Name().c_str())
    if Tool.Execute() == False:
        print('failed')
        return False
    print('okay')

    return True


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


def pj_proj4_3(obj):
    #_____________________________________
    Tool = saga_api.SG_Get_Tool_Library_Manager().Get_Tool('pj_proj4', '3')
    if Tool == None:
        print('Failed to create tool: Coordinate Transformation (Grid List)')
        return False

    Tool.Reset()

    Tool.Set_Parameter('CRS_METHOD', 'Proj4 Parameters')
    Tool.Set_Parameter('CRS_PROJ4', '+proj=merc +lon_0=0 +k=1 +x_0=0 +datum=WGS84 +units=m +no_defs ')
    Tool.Set_Parameter('CRS_FILE', '')
    Tool.Set_Parameter('CRS_EPSG', 4326)
    Tool.Set_Parameter('CRS_EPSG_AUTH', 'EPSG')
    Tool.Set_Parameter('PRECISE', False)
    Tool.Get_Parameter('SOURCE').asList().Add_Item(obj.asGrid())
    Tool.Set_Parameter('RESAMPLING', 'B-Spline Interpolation')
    Tool.Set_Parameter('BYTEWISE', False)
    Tool.Set_Parameter('KEEP_TYPE', False)
    Tool.Set_Parameter('TARGET_AREA', False)
    Tool.Set_Parameter('TARGET_DEFINITION', 'user defined')
    Tool.Set_Parameter('TARGET_USER_SIZE', 3000.000)
    Tool.Set_Parameter('TARGET_USER_FITS', 'nodes')
    Tool.Set_Parameter('TARGET_TEMPLATE', 'Grid input, optional')
    Tool.Set_Parameter('OUT_X_CREATE', False)
    Tool.Set_Parameter('OUT_Y_CREATE', False)

    if Tool.Execute() == False:
        print('failed to execute tool: ' + Tool.Get_Name().c_str())
        return False

    ds = Tool.Get_Parameter('GRIDS').asGridList().Get_Grid(0)

    return ds



def reproject_shape(obj):
    #_____________________________________
    # Create a new instance of tool 'Coordinate Transformation (Shapes)'
    Tool = saga_api.SG_Get_Tool_Library_Manager().Create_Tool('pj_proj4', '2')
    if Tool == None:
        print('Failed to create tool: Coordinate Transformation (Shapes)')
        return False

    Tool.Set_Parameter('CRS_PROJ4', '+proj=merc +lon_0=0 +k=1 +x_0=0 +datum=WGS84 +units=m +no_defs ')
    Tool.Set_Parameter('CRS_FILE', '')
    Tool.Set_Parameter('CRS_EPSG', 4326)
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


def multilevel_B_spline(shape, template,lev):
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
    Tool.Set_Parameter('LEVEL_MAX', lev)

    print('Executing tool: ' + Tool.Get_Name().c_str())
    if Tool.Execute() == False:
        print('failed')
        return False
    print('okay')

    Parm = Tool.Get_Parameters()
    Data  = Parm('TARGET_OUT_GRID').asGrid()

    return Data


def polar_coords(uwind,vwind):
    #_____________________________________
    # Create a new instance of tool 'Gradient Vector from Cartesian to Polar Coordinates'
    Tool = saga_api.SG_Get_Tool_Library_Manager().Create_Tool('grid_calculus', '15')
    if Tool == None:
        print('Failed to create tool: Gradient Vector from Cartesian to Polar Coordinates')
        return False

    Tool.Get_Parameters().Reset_Grid_System()

    Tool.Set_Parameter('DX', uwind.asGrid())
    Tool.Set_Parameter('DY', vwind.asGrid())
    Tool.Set_Parameter('UNITS', 'radians')
    Tool.Set_Parameter('SYSTEM', 'geographical')
    Tool.Set_Parameter('SYSTEM_ZERO', 0.000000)
    Tool.Set_Parameter('SYSTEM_ORIENT', 'clockwise')

    print('Executing tool: ' + Tool.Get_Name().c_str())
    if Tool.Execute() == False:
        print('failed')
        return False
    print('okay')

    Data = Tool.Get_Parameter('DIR').asGrid()

    return Data


def windeffect(dir,dem):
    #_____________________________________
    # Create a new instance of tool 'Wind Effect (Windward / Leeward Index)'
    Tool = saga_api.SG_Get_Tool_Library_Manager().Create_Tool('ta_morphometry', '15')
    if Tool == None:
        print('Failed to create tool: Wind Effect (Windward / Leeward Index)')
        return False

    Tool.Get_Parameters().Reset_Grid_System()

    Tool.Set_Parameter('DEM', dem.asGrid())
    Tool.Set_Parameter('DIR', dir.asGrid())
    Tool.Set_Parameter('LEN_SCALE', 1.000000)
    Tool.Set_Parameter('AFH', saga_api.SG_Get_Create_Pointer()) # optional output, remove this line, if you don't want to create it
    Tool.Set_Parameter('MAXDIST', 300.000000)
    Tool.Set_Parameter('OLDVER', False)
    Tool.Set_Parameter('ACCEL', 1.500000)
    Tool.Set_Parameter('PYRAMIDS', False)

    print('Executing tool: ' + Tool.Get_Name().c_str())
    if Tool.Execute() == False:
        print('failed')
        return False
    print('okay')

    Data = Tool.Get_Parameter('EFFECT').asGrid()

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


def calc_geopotential(obj):
    #_____________________________________
    # Create a new instance of tool 'Grid Calculator'
    Tool = saga_api.SG_Get_Tool_Library_Manager().Create_Tool('grid_calculus', '1')
    if Tool == None:
        print('Failed to create tool: Grid Calculator')
        return False

    Tool.Get_Parameters().Reset_Grid_System()

    Tool.Set_Parameter('RESAMPLING', 'B-Spline Interpolation')
    Tool.Set_Parameter('FORMULA', 'a*9.80665')
    Tool.Set_Parameter('NAME', 'geopotential')
    Tool.Set_Parameter('FNAME', False)
    Tool.Set_Parameter('USE_NODATA', False)
    Tool.Set_Parameter('TYPE', 7)
    Tool.Get_Parameter('GRIDS').asList().Add_Item(obj.asGrid())

    print('Executing tool: ' + Tool.Get_Name().c_str())
    if Tool.Execute() == False:
        print('failed')
        return False
    print('okay')

    Data = Tool.Get_Parameter('RESULT').asGrid()

    return Data


def closegaps(obj):
    #_____________________________________
    # Create a new instance of tool 'Close Gaps'
    Tool = saga_api.SG_Get_Tool_Library_Manager().Create_Tool('grid_tools', '7')
    if Tool == None:
        print('Failed to create tool: Close Gaps')
        return False

    Tool.Get_Parameters().Reset_Grid_System()

    Tool.Set_Parameter('INPUT', obj.asGrid())
    Tool.Set_Parameter('THRESHOLD', 0.100000)

    print('Executing tool: ' + Tool.Get_Name().c_str())
    if Tool.Execute() == False:
        print('failed')
        return False
    print('okay')


def change_data_storage(File):
    #_____________________________________
    # Create a new instance of tool 'Change Data Storage'
    Tool = saga_api.SG_Get_Tool_Library_Manager().Create_Tool('grid_tools', '11')
    if Tool == None:
        print('Failed to create tool: Change Data Storage')
        return False

    Tool.Get_Parameters().Reset_Grid_System()

    Tool.Set_Parameter('INPUT', File.asGrid())
    Tool.Set_Parameter('OUTPUT', saga_api.SG_Get_Create_Pointer()) # optional output, remove this line, if you don't want to create it
    Tool.Set_Parameter('TYPE', 7)
    Tool.Set_Parameter('OFFSET', 0.000000)
    Tool.Set_Parameter('SCALE', 1.000000)

    print('Executing tool: ' + Tool.Get_Name().c_str())
    if Tool.Execute() == False:
        print('failed')
        return False
    print('okay')

    Data = Tool.Get_Parameter('OUTPUT').asGrid()

    return Data


def change_data_storage2(File,type):
    #_____________________________________
    # Create a new instance of tool 'Change Data Storage'
    Tool = saga_api.SG_Get_Tool_Library_Manager().Create_Tool('grid_tools', '11')
    if Tool == None:
        print('Failed to create tool: Change Data Storage')
        return False

    Tool.Get_Parameters().Reset_Grid_System()

    Tool.Set_Parameter('INPUT', File.asGrid())
    Tool.Set_Parameter('OUTPUT', saga_api.SG_Get_Create_Pointer()) # optional output, remove this line, if you don't want to create it
    Tool.Set_Parameter('TYPE', type)
    Tool.Set_Parameter('OFFSET', 0.000000)
    Tool.Set_Parameter('SCALE', 1.000000)

    print('Executing tool: ' + Tool.Get_Name().c_str())
    if Tool.Execute() == False:
        print('failed')
        return False
    print('okay')

    Data = Tool.Get_Parameter('OUTPUT').asGrid()

    return Data


def grid_masking(grid, mask):
    #_____________________________________
    # Create a new instance of tool 'Tool Grid Masking'
    Tool = saga_api.SG_Get_Tool_Library_Manager().Create_Tool('grid_tools', '24')
    if Tool == None:
        print('Failed to create tool: Tool Grid Masking')
        return False

    Tool.Get_Parameters().Reset_Grid_System()

    Tool.Set_Parameter('GRID', grid.asGrid())
    Tool.Set_Parameter('MASK', mask.asGrid())

    print('Executing tool: ' + Tool.Get_Name().c_str())
    if Tool.Execute() == False:
        print('failed')
        return False
    print('okay')


def cloud_overlap(cloudcover,geopotential,cloudbase,dem,windeffect,levels):
    #_____________________________________
    # Create a new instance of tool 'Cloud Overlap'
    Tool = saga_api.SG_Get_Tool_Library_Manager().Create_Tool('climate_tools', '25')
    if Tool == None:
        print('Failed to create tool: Cloud Overlap')
        return False

    Tool.Get_Parameters().Reset_Grid_System()

    for level in levels:
        Tool.Get_Parameter('COVERS').asList().Add_Item(cloudcover.Get_Grid(level))
    for level in levels:
        Tool.Get_Parameter('HEIGHTS').asList().Add_Item(geopotential.Get_Grid(level))

    Tool.Set_Parameter('GROUND', dem.asGrid())
    Tool.Set_Parameter('WIND', windeffect.asGrid())
    Tool.Set_Parameter('CBASE', cloudbase.asGrid())
    Tool.Set_Parameter('BLOCKS', saga_api.SG_Get_Create_Pointer()) # optional output, remove this line, if you don't want to create it
    Tool.Set_Parameter('INTERVAL', 250.000000)
    Tool.Set_Parameter('MINCOVER', -1.0000)

    print('Executing tool: ' + Tool.Get_Name().c_str())
    if Tool.Execute() == False:
        print('failed')
        return False
    print('okay')

    Data = Tool.Get_Parameter('COVER').asGrid()

    return Data


def patching(File1,File2):
    #_____________________________________
    # Create a new instance of tool 'Patching'
    Tool = saga_api.SG_Get_Tool_Library_Manager().Create_Tool('grid_tools', '5')
    if Tool == None:
        print('Failed to create tool: Patching')
        return False

    Tool.Get_Parameters().Reset_Grid_System()

    Tool.Set_Parameter('ORIGINAL', File1.asGrid())
    Tool.Set_Parameter('COMPLETED', saga_api.SG_Get_Create_Pointer()) # optional output, remove this line, if you don't want to create it
    Tool.Set_Parameter('ADDITIONAL', File2.asGrid())
    Tool.Set_Parameter('RESAMPLING', 0)

    print('Executing tool: ' + Tool.Get_Name().c_str())
    if Tool.Execute() == False:
        print('failed')
        return False
    print('okay')

    Data = Tool.Get_Parameter('COMPLETED').asGrid()

    return Data


def patchingBspline(File1,File2):
    #_____________________________________
    # Create a new instance of tool 'Patching'
    Tool = saga_api.SG_Get_Tool_Library_Manager().Create_Tool('grid_tools', '5')
    if Tool == None:
        print('Failed to create tool: Patching')
        return False

    Tool.Get_Parameters().Reset_Grid_System()

    Tool.Set_Parameter('ORIGINAL', File1.asGrid())
    Tool.Set_Parameter('ADDITIONAL', File2.asGrid())
    Tool.Set_Parameter('RESAMPLING', 2)

    print('Executing tool: ' + Tool.Get_Name().c_str())
    if Tool.Execute() == False:
        print('failed')
        return False
    print('okay')


def calculate_bias(obj1,obj2):
    #_____________________________________
    # Create a new instance of tool 'Grid Calculator'
    Tool = saga_api.SG_Get_Tool_Library_Manager().Create_Tool('grid_calculus', '1')
    if Tool == None:
        print('Failed to create tool: Grid Calculator')
        return False

    Tool.Get_Parameters().Reset_Grid_System()

    Tool.Set_Parameter('RESAMPLING', 'B-Spline Interpolation')
    Tool.Set_Parameter('FORMULA', '(a+1)/(b+1)')
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


def simple_bias(obj1,obj2):
    #_____________________________________
    # Create a new instance of tool 'Grid Calculator'
    Tool = saga_api.SG_Get_Tool_Library_Manager().Create_Tool('grid_calculus', '1')
    if Tool == None:
        print('Failed to create tool: Grid Calculator')
        return False

    Tool.Get_Parameters().Reset_Grid_System()

    Tool.Set_Parameter('RESAMPLING', 'B-Spline Interpolation')
    Tool.Set_Parameter('FORMULA', 'a/(b*0.001)')
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


def biascor(obj1,obj2):
    #_____________________________________
    # Create a new instance of tool 'Grid Calculator'
    Tool = saga_api.SG_Get_Tool_Library_Manager().Create_Tool('grid_calculus', '1')
    if Tool == None:
        print('Failed to create tool: Grid Calculator')
        return False

    Tool.Get_Parameters().Reset_Grid_System()

    Tool.Set_Parameter('RESAMPLING', 'B-Spline Interpolation')
    Tool.Set_Parameter('FORMULA', 'a*b')
    Tool.Set_Parameter('NAME', 'Calculation')
    Tool.Set_Parameter('FNAME', False)
    Tool.Set_Parameter('USE_NODATA', False)
    Tool.Set_Parameter('TYPE', 7)
    Tool.Get_Parameter('GRIDS').asList().Add_Item(obj1.asGrid())
    Tool.Get_Parameter('XGRIDS').asList().Add_Item(obj2.asGrid())

    print('Executing tool: ' + Tool.Get_Name().c_str())
    if Tool.Execute() == False:
        print('failed')
        return False
    print('okay')

    Data = Tool.Get_Parameter('RESULT').asGrid()

    return Data


def biascor2(obj1,obj2):
    #_____________________________________
    # Create a new instance of tool 'Grid Calculator'
    Tool = saga_api.SG_Get_Tool_Library_Manager().Create_Tool('grid_calculus', '1')
    if Tool == None:
        print('Failed to create tool: Grid Calculator')
        return False

    Tool.Get_Parameters().Reset_Grid_System()

    Tool.Set_Parameter('RESAMPLING', 'B-Spline Interpolation')
    Tool.Set_Parameter('FORMULA', 'a/b')
    Tool.Set_Parameter('NAME', 'Calculation')
    Tool.Set_Parameter('FNAME', False)
    Tool.Set_Parameter('USE_NODATA', False)
    Tool.Set_Parameter('TYPE', 7)
    Tool.Get_Parameter('GRIDS').asList().Add_Item(obj1.asGrid())
    Tool.Get_Parameter('XGRIDS').asList().Add_Item(obj2.asGrid())

    print('Executing tool: ' + Tool.Get_Name().c_str())
    if Tool.Execute() == False:
        print('failed')
        return False
    print('okay')

    Data = Tool.Get_Parameter('RESULT').asGrid()

    return Data


def capat1(obj1):
    #_____________________________________
    # Create a new instance of tool 'Grid Calculator'
    Tool = saga_api.SG_Get_Tool_Library_Manager().Create_Tool('grid_calculus', '1')
    if Tool == None:
        print('Failed to create tool: Grid Calculator')
        return False

    Tool.Get_Parameters().Reset_Grid_System()

    Tool.Set_Parameter('RESAMPLING', 'B-Spline Interpolation')
    Tool.Set_Parameter('FORMULA', 'ifelse(a<1,a*1,a-a+1)')
    Tool.Set_Parameter('NAME', 'tcc')
    Tool.Set_Parameter('FNAME', False)
    Tool.Set_Parameter('USE_NODATA', False)
    Tool.Set_Parameter('TYPE', 7)
    Tool.Get_Parameter('GRIDS').asList().Add_Item(obj1.asGrid())

    print('Executing tool: ' + Tool.Get_Name().c_str())
    if Tool.Execute() == False:
        print('failed')
        return False
    print('okay')

    #_____________________________________
    Data = Tool.Get_Parameter('RESULT').asGrid()

    return Data


def convert2uinteger(obj1):
    #_____________________________________
    # Create a new instance of tool 'Grid Calculator'
    Tool = saga_api.SG_Get_Tool_Library_Manager().Create_Tool('grid_calculus', '1')
    if Tool == None:
        print('Failed to create tool: Grid Calculator')
        return False

    Tool.Get_Parameters().Reset_Grid_System()

    Tool.Set_Parameter('RESAMPLING', 'B-Spline Interpolation')
    Tool.Set_Parameter('FORMULA', 'a*10000')
    Tool.Set_Parameter('NAME', 'tcc')
    Tool.Set_Parameter('FNAME', False)
    Tool.Set_Parameter('USE_NODATA', False)
    Tool.Set_Parameter('TYPE', 3)
    Tool.Get_Parameter('GRIDS').asList().Add_Item(obj1.asGrid())

    print('Executing tool: ' + Tool.Get_Name().c_str())
    if Tool.Execute() == False:
        print('failed')
        return False
    print('okay')

    #_____________________________________
    Data = Tool.Get_Parameter('RESULT').asGrid()

    return Data


def convert2uinteger10(obj1,name):
    #_____________________________________
    # Create a new instance of tool 'Grid Calculator'
    Tool = saga_api.SG_Get_Tool_Library_Manager().Create_Tool('grid_calculus', '1')
    if Tool == None:
        print('Failed to create tool: Grid Calculator')
        return False

    Tool.Get_Parameters().Reset_Grid_System()

    Tool.Set_Parameter('RESAMPLING', 'B-Spline Interpolation')
    Tool.Set_Parameter('FORMULA', 'a*10')
    Tool.Set_Parameter('NAME', name)
    Tool.Set_Parameter('FNAME', False)
    Tool.Set_Parameter('USE_NODATA', False)
    Tool.Set_Parameter('TYPE', 3)
    Tool.Get_Parameter('GRIDS').asList().Add_Item(obj1.asGrid())

    print('Executing tool: ' + Tool.Get_Name().c_str())
    if Tool.Execute() == False:
        print('failed')
        return False
    print('okay')

    #_____________________________________
    Data = Tool.Get_Parameter('RESULT').asGrid()

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

    if Tool.Execute() == False:
        print 'failed'
        return False

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
    Tool.Set_Parameter('FORMULA', 'd-b*(a-c)')
    Tool.Set_Parameter('NAME', 'Calculation')
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


def surface_radiation(stot, cloudcover, name):
    #_____________________________________
    # Create a new instance of tool 'Grid Calculator'
    Tool = saga_api.SG_Get_Tool_Library_Manager().Create_Tool('grid_calculus', '1')
    if Tool == None:
        print('Failed to create tool: Grid Calculator')
        return False

    Tool.Get_Parameters().Reset_Grid_System()

    Tool.Set_Parameter('RESAMPLING', 'B-Spline Interpolation')
    Tool.Set_Parameter('FORMULA', 'a*(1-0.75*b^3.4)')
    Tool.Set_Parameter('NAME', name)
    Tool.Set_Parameter('FNAME', False)
    Tool.Set_Parameter('USE_NODATA', False)
    Tool.Set_Parameter('TYPE', 7)
    Tool.Get_Parameter('GRIDS').asList().Add_Item(stot.asGrid())
    Tool.Get_Parameter('XGRIDS').asList().Add_Item(cloudcover.asGrid())

    print('Executing tool: ' + Tool.Get_Name().c_str())
    if Tool.Execute() == False:
        print('failed')
        return False
    print('okay')

    #_____________________________________
    # Save results to file:
    Data = Tool.Get_Parameter('RESULT').asGrid()

    return Data


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


def grid_calculator_simple(obj1,equ):
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

    print('Executing tool: ' + Tool.Get_Name().c_str())
    if Tool.Execute() == False:
        print('failed')
        return False
    print('okay')

    Data = Tool.Get_Parameter('RESULT').asGrid()

    return Data


def grid_calculatorX(obj1,xobj2,equ):
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
    Tool.Get_Parameter('XGRIDS').asList().Add_Item(xobj2.asGrid())

    print('Executing tool: ' + Tool.Get_Name().c_str())
    if Tool.Execute() == False:
        print('failed')
        return False
    print('okay')

    Data = Tool.Get_Parameter('RESULT').asGrid()

    return Data


def calc_dist2bound(dem,pblh):
    #_____________________________________
    # Create a new instance of tool 'Grid Calculator'
    Tool = saga_api.SG_Get_Tool_Library_Manager().Create_Tool('grid_calculus', '1')
    if Tool == None:
        print('Failed to create tool: Grid Calculator')
        return False

    Tool.Get_Parameters().Reset_Grid_System()

    Tool.Set_Parameter('RESAMPLING', 'B-Spline Interpolation')
    Tool.Set_Parameter('FORMULA', 'abs((a-b))')
    Tool.Set_Parameter('NAME', 'Calculation')
    Tool.Set_Parameter('FNAME', False)
    Tool.Set_Parameter('USE_NODATA', False)
    Tool.Set_Parameter('TYPE', 7)
    Tool.Get_Parameter('GRIDS').asList().Add_Item(dem.asGrid())
    Tool.Get_Parameter('XGRIDS').asList().Add_Item(pblh.asGrid())

    print('Executing tool: ' + Tool.Get_Name().c_str())
    if Tool.Execute() == False:
        print('failed')
        return False
    print('okay')

    Data = Tool.Get_Parameter('RESULT').asGrid()

    return Data


def resample_up(obj,template, type):
    #_____________________________________
    # Create a new instance of tool 'Resampling'
    Tool = saga_api.SG_Get_Tool_Library_Manager().Create_Tool('grid_tools', '0')
    if Tool == None:
        print('Failed to create tool: Resampling')
        return False

    Tool.Get_Parameters().Reset_Grid_System()

    Tool.Get_Parameter('INPUT').asList().Add_Item(obj.asGrid())
    Tool.Set_Parameter('KEEP_TYPE', False)
    Tool.Set_Parameter('SCALE_UP', type)
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


def invert_dist2bound(dist2bound,maxdist2bound):
    #_____________________________________
    # Create a new instance of tool 'Grid Calculator'
    Tool = saga_api.SG_Get_Tool_Library_Manager().Create_Tool('grid_calculus', '1')
    if Tool == None:
        print('Failed to create tool: Grid Calculator')
        return False

    Tool.Get_Parameters().Reset_Grid_System()

    Tool.Set_Parameter('RESAMPLING', 'B-Spline Interpolation')
    Tool.Set_Parameter('FORMULA', 'abs((b-a))')
    Tool.Set_Parameter('NAME', 'Calculation')
    Tool.Set_Parameter('FNAME', False)
    Tool.Set_Parameter('USE_NODATA', False)
    Tool.Set_Parameter('TYPE', 7)
    Tool.Get_Parameter('GRIDS').asList().Add_Item(dist2bound.asGrid())
    Tool.Get_Parameter('XGRIDS').asList().Add_Item(maxdist2bound.asGrid())

    print('Executing tool: ' + Tool.Get_Name().c_str())
    if Tool.Execute() == False:
        print('failed')
        return False
    print('okay')

    Data = Tool.Get_Parameter('RESULT').asGrid()

    return Data


def downscale_precip(windhigh,windlow,prec,name,type):
    #_____________________________________
    # Create a new instance of tool 'Grid Calculator'
    Tool = saga_api.SG_Get_Tool_Library_Manager().Create_Tool('grid_calculus', '1')
    if Tool == None:
        print('Failed to create tool: Grid Calculator')
        return False

    Tool.Get_Parameters().Reset_Grid_System()

    Tool.Set_Parameter('RESAMPLING', type)
    Tool.Set_Parameter('FORMULA', 'b*a/c')
    Tool.Set_Parameter('NAME', name)
    Tool.Set_Parameter('FNAME', False)
    Tool.Set_Parameter('USE_NODATA', False)
    Tool.Set_Parameter('TYPE', 7)
    Tool.Get_Parameter('GRIDS').asList().Add_Item(windhigh.asGrid())
    Tool.Get_Parameter('XGRIDS').asList().Add_Item(prec.asGrid())
    Tool.Get_Parameter('XGRIDS').asList().Add_Item(windlow.asGrid())

    print('Executing tool: ' + Tool.Get_Name().c_str())
    if Tool.Execute() == False:
        print('failed')
        return False
    print('okay')

    Data = Tool.Get_Parameter('RESULT').asGrid()

    return Data


def grid_statistics(obj1,obj2,param=False):
    #_____________________________________
    # Create a new instance of tool 'Statistics for Grids'
    Tool = saga_api.SG_Get_Tool_Library_Manager().Create_Tool('statistics_grid', '4')
    if Tool == None:
        print('Failed to create tool: Statistics for Grids')
        return False

    Tool.Get_Parameters().Reset_Grid_System()

    Tool.Get_Parameter('GRIDS').asList().Add_Item(obj1.asGrid())
    Tool.Get_Parameter('GRIDS').asList().Add_Item(obj2.asGrid())
    Tool.Set_Parameter('RESAMPLING', 'B-Spline Interpolation')
    Tool.Set_Parameter('MAX' if param else 'MIN', saga_api.SG_Get_Create_Pointer())
    Tool.Set_Parameter('PCTL_VAL', 50.000000)

    print('Executing tool: ' + Tool.Get_Name().c_str())
    if Tool.Execute() == False:
        print('failed')
        return False
    print('okay')

    Data = Tool.Get_Parameter('MAX' if param else 'MIN').asDataObject()

    return Data


def get_minmax(extreme,minmax):
    #_____________________________________
    # Create a new instance of tool 'Statistics for Grids'
    Tool = saga_api.SG_Get_Tool_Library_Manager().Create_Tool('statistics_grid', '4')
    if Tool == None:
        print('Failed to create tool: Statistics for Grids')
        return False

    Tool.Get_Parameters().Reset_Grid_System()

    Tool.Get_Parameter('GRIDS').asList().Add_Item(extreme.asGridList().Get_Grid(0))
    Tool.Get_Parameter('GRIDS').asList().Add_Item(extreme.asGridList().Get_Grid(1))
    Tool.Get_Parameter('GRIDS').asList().Add_Item(extreme.asGridList().Get_Grid(2))
    Tool.Get_Parameter('GRIDS').asList().Add_Item(extreme.asGridList().Get_Grid(3))
    Tool.Get_Parameter('GRIDS').asList().Add_Item(extreme.asGridList().Get_Grid(4))
    Tool.Get_Parameter('GRIDS').asList().Add_Item(extreme.asGridList().Get_Grid(5))
    Tool.Get_Parameter('GRIDS').asList().Add_Item(extreme.asGridList().Get_Grid(6))
    Tool.Get_Parameter('GRIDS').asList().Add_Item(extreme.asGridList().Get_Grid(7))
    Tool.Get_Parameter('GRIDS').asList().Add_Item(extreme.asGridList().Get_Grid(8))
    Tool.Get_Parameter('GRIDS').asList().Add_Item(extreme.asGridList().Get_Grid(9))
    Tool.Get_Parameter('GRIDS').asList().Add_Item(extreme.asGridList().Get_Grid(10))
    Tool.Get_Parameter('GRIDS').asList().Add_Item(extreme.asGridList().Get_Grid(11))
    Tool.Get_Parameter('GRIDS').asList().Add_Item(extreme.asGridList().Get_Grid(12))
    Tool.Get_Parameter('GRIDS').asList().Add_Item(extreme.asGridList().Get_Grid(13))
    Tool.Get_Parameter('GRIDS').asList().Add_Item(extreme.asGridList().Get_Grid(14))
    Tool.Get_Parameter('GRIDS').asList().Add_Item(extreme.asGridList().Get_Grid(15))
    Tool.Get_Parameter('GRIDS').asList().Add_Item(extreme.asGridList().Get_Grid(16))
    Tool.Get_Parameter('GRIDS').asList().Add_Item(extreme.asGridList().Get_Grid(17))
    Tool.Get_Parameter('GRIDS').asList().Add_Item(extreme.asGridList().Get_Grid(18))
    Tool.Get_Parameter('GRIDS').asList().Add_Item(extreme.asGridList().Get_Grid(19))
    Tool.Get_Parameter('GRIDS').asList().Add_Item(extreme.asGridList().Get_Grid(20))
    Tool.Get_Parameter('GRIDS').asList().Add_Item(extreme.asGridList().Get_Grid(21))
    Tool.Get_Parameter('GRIDS').asList().Add_Item(extreme.asGridList().Get_Grid(22))
    Tool.Get_Parameter('GRIDS').asList().Add_Item(extreme.asGridList().Get_Grid(23))

    Tool.Set_Parameter('RESAMPLING', 'B-Spline Interpolation')
    Tool.Set_Parameter('MIN', saga_api.SG_Get_Create_Pointer()) # optional output, remove this line, if you don't want to create it
    Tool.Set_Parameter('MAX', saga_api.SG_Get_Create_Pointer()) # optional output, remove this line, if you don't want to create it

    print('Executing tool: ' + Tool.Get_Name().c_str())
    if Tool.Execute() == False:
        print('failed')
        return False
    print('okay')

    #_____________________________________
    # Save results to file:
    if minmax == 0:
        Data = Tool.Get_Parameter('MIN').asDataObject()
    if minmax == 1:
        Data = Tool.Get_Parameter('MAX').asDataObject()

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


def Run_Clip_Grids(obj, xmin, xmax, ymin, ymax, buffer):
    #_____________________________________
    Tool = saga_api.SG_Get_Tool_Library_Manager().Get_Tool('grid_tools', '31')
    if Tool == None:
        print('Failed to create tool: Clip Grids')
        return False

    Tool.Get_Parameters().Reset_Grid_System()

    Tool.Get_Parameter('GRIDS').asList().Add_Item(obj.asGrid())
    Tool.Set_Parameter('EXTENT', 'user defined')
    Tool.Set_Parameter('XMIN', xmin)
    Tool.Set_Parameter('XMAX', xmax)
    Tool.Set_Parameter('YMIN', ymin)
    Tool.Set_Parameter('YMAX', ymax)
    #Tool.Set_Parameter('NX', 801)
    #Tool.Set_Parameter('NY', 801)
    Tool.Set_Parameter('BUFFER', buffer)

    if Tool.Execute() == False:
        print('failed to execute tool: ' + Tool.Get_Name().c_str())
        return False

    ds = Tool.Get_Parameter('CLIPPED').asGridList().Get_Grid(0)

    return ds


def Coordinate_Transformation_Shapes(obj):
    Tool = saga_api.SG_Get_Tool_Library_Manager().Get_Tool('pj_proj4', '1')
    if Tool == None:
        print('Failed to create tool: Coordinate Transformation (Shapes List)')
        return False

    Tool.Get_Parameters().Reset_Grid_System()

    Tool.Set_Parameter('CRS_METHOD', 'Proj4 Parameters')
    Tool.Set_Parameter('CRS_PROJ4', '+proj=merc +lon_0=0 +k=1 +x_0=0 +y_0=0 +datum=WGS84 +units=m +no_defs ')
    Tool.Set_Parameter('CRS_FILE', '')
    Tool.Set_Parameter('CRS_EPSG', 3857)
    Tool.Set_Parameter('CRS_EPSG_AUTH', 'EPSG')
    Tool.Set_Parameter('PRECISE', False)
    Tool.Get_Parameter('SOURCE').asList().Add_Item(obj)
    Tool.Set_Parameter('TRANSFORM_Z', True)
    Tool.Set_Parameter('COPY', True)

    if Tool.Execute() == False:
        print('failed to execute tool: ' + Tool.Get_Name().c_str())
        return False

    Data = Tool.Get_Parameter('TARGET').asList().Get_Grid(0)

    return Data


def clip_with_polygon(grid, polygon):
    #_____________________________________
    Tool = saga_api.SG_Get_Tool_Library_Manager().Get_Tool('shapes_grid', '7')
    if Tool == None:
        print('Failed to create tool: Clip Grid with Polygon')
        return False

    Tool.Get_Parameters().Reset_Grid_System()

    Tool.Get_Parameter('INPUT').asList().Add_Item(grid)
    Tool.Set_Parameter('POLYGONS', polygon)
    Tool.Set_Parameter('EXTENT', 'polygons')

    if Tool.Execute() == False:
        print('failed to execute tool: ' + Tool.Get_Name().c_str())
        return False

    Data = Tool.Get_Parameter('OUTPUT').asGridList()

    return Data


def Run_Vectorising_Grid_Classes(obj):
    #_____________________________________
    Tool = saga_api.SG_Get_Tool_Library_Manager().Get_Tool('shapes_grid', '6')
    if Tool == None:
        print('Failed to create tool: Vectorising Grid Classes')
        return False

    Tool.Get_Parameters().Reset_Grid_System()

    Tool.Set_Parameter('GRID', obj)
    Tool.Set_Parameter('CLASS_ALL', 'all classes')
    Tool.Set_Parameter('CLASS_ID', 1.000000)
    Tool.Set_Parameter('SPLIT', 'one single (multi-)polygon object')
    Tool.Set_Parameter('ALLVERTICES', False)

    if Tool.Execute() == False:
        print('failed to execute tool: ' + Tool.Get_Name().c_str())
        return False

    Data = Tool.Get_Parameter('POLYGONS').asDataObject()

    return Data


def Air_Pressure(ps, orog, tas, tz, dem_high):
    #_____________________________________
    Tool = saga_api.SG_Get_Tool_Library_Manager().Get_Tool('climate_tools', '27')
    if Tool == None:
        print('Failed to create tool: Air Pressure Adjustment')
        return False

    Tool.Get_Parameters().Reset_Grid_System()

    Tool.Set_Parameter('P', ps)
    Tool.Set_Parameter('Z', orog)
    Tool.Set_Parameter('T', tas)
    Tool.Set_Parameter('L', tz)
    Tool.Set_Parameter('DEM', dem_high)

    if Tool.Execute() == False:
        print('failed to execute tool: ' + Tool.Get_Name().c_str())
        return False

    Data = Tool.Get_Parameter('P_ADJ').asDataObject()

    return Data


def clear_sky_solar_radiation(dem_merc, year, month, day, hour):
    #_____________________________________
    Tool = saga_api.SG_Get_Tool_Library_Manager().Get_Tool('ta_lighting', '2')
    if Tool == None:
        print('Failed to create tool: Potential Incoming Solar Radiation')
        return False

    Tool.Get_Parameters().Reset_Grid_System()

    Tool.Set_Parameter('GRD_DEM', dem_merc)
    Tool.Set_Parameter('GRD_TOTAL', saga_api.SG_Get_Create_Pointer()) # optional output, remove this line, if you don't want to create it
    Tool.Set_Parameter('SOLARCONST', 1367.000000)
    Tool.Set_Parameter('LOCALSVF', True)
    Tool.Set_Parameter('UNITS', 1)
    Tool.Set_Parameter('SHADOW', 1)
    Tool.Set_Parameter('LOCATION', 1)
    Tool.Set_Parameter('PERIOD', 0)
    Tool.Set_Parameter('DAY', str(year) + '-' + str("%02d" % month) + '-' + str("%02d" % day))
    Tool.Set_Parameter('MOMENT', hour)
    Tool.Set_Parameter('HOUR_RANGE.MIN', 0.000000)
    Tool.Set_Parameter('METHOD', 2)
    Tool.Set_Parameter('ATMOSPHERE', 12000.000000)
    Tool.Set_Parameter('PRESSURE', 1013.000000)
    Tool.Set_Parameter('WATER', 1.680000)
    Tool.Set_Parameter('DUST', 100.000000)
    Tool.Set_Parameter('LUMPED', 80.000000)

    if Tool.Execute() == False:
        print('failed to execute tool: ' + Tool.Get_Name().c_str())
        return False

    Data = Tool.Get_Parameter('GRD_TOTAL').asGrid()

    return Data


def Multi_Level_to_Surface_Interpolation(var, zg, dem_geo, levels):
    #_____________________________________
    Tool = saga_api.SG_Get_Tool_Library_Manager().Get_Tool('climate_tools', '0')
    if Tool == None:
        print('Failed to create tool: Multi Level to Surface Interpolation')
        return False

    Tool.Get_Parameters().Reset_Grid_System()

    for level in levels:
        Tool.Get_Parameter('VARIABLE').asList().Add_Item(var.Get_Grid(level))
    for level in levels:
        Tool.Get_Parameter('X_GRIDS').asList().Add_Item(zg.Get_Grid(level))

    Tool.Set_Parameter('X_SOURCE', 1)
    Tool.Set_Parameter('H_METHOD', 2)
    Tool.Set_Parameter('V_METHOD', 1)
    Tool.Set_Parameter('COEFFICIENTS', False)
    Tool.Set_Parameter('LINEAR_SORTED', 1)
    Tool.Set_Parameter('SPLINE_ALL', False)
    Tool.Set_Parameter('TREND_ORDER', 3)
    Tool.Set_Parameter('SURFACE', dem_geo)

    if Tool.Execute() == False:
        print('failed to execute tool: ' + Tool.Get_Name().c_str())
        return False

    Data = Tool.Get_Parameter('RESULT').asDataObject()

    return Data


def Grid_Normalization(grid):
    #_____________________________________
    Tool = saga_api.SG_Get_Tool_Library_Manager().Get_Tool('grid_calculus', '0')
    if Tool == None:
        print('Failed to create tool: Grid Normalization')
        return False

    Tool.Get_Parameters().Reset_Grid_System()

    Tool.Set_Parameter('INPUT', grid)
    Tool.Set_Parameter('RANGE.MIN', 0.000000)
    Tool.Set_Parameter('RANGE.MAX', 1.000000)

    if Tool.Execute() == False:
        print('failed to execute tool: ' + Tool.Get_Name().c_str())
        return False

    Data = Tool.Get_Parameter('OUTPUT').asDataObject()

    return Data



def grid_calculator3(obj1, obj2, xobj3, equ):
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
    Tool.Get_Parameter('XGRIDS').asList().Add_Item(xobj3.asGrid())

    print('Executing tool: ' + Tool.Get_Name().c_str())
    if Tool.Execute() == False:
        print('failed')
        return False
    print('okay')

    Data = Tool.Get_Parameter('RESULT').asGrid()

    return Data


def Gradient_Vector_from_Cartesian_to_Polar_Coordinates(u_sfc, v_sfc):
    #_____________________________________
    Tool = saga_api.SG_Get_Tool_Library_Manager().Get_Tool('grid_calculus', '15')
    if Tool == None:
        print('Failed to create tool: Gradient Vector from Cartesian to Polar Coordinates')
        return False

    Tool.Reset()

    Tool.Set_Parameter('DX', u_sfc)
    Tool.Set_Parameter('DY', v_sfc)
    Tool.Set_Parameter('UNITS', 'radians')
    Tool.Set_Parameter('SYSTEM', 'geographical')
    Tool.Set_Parameter('SYSTEM_ZERO', 0.000000)
    Tool.Set_Parameter('SYSTEM_ORIENT', 'clockwise')

    if Tool.Execute() == False:
        print('failed to execute tool: ' + Tool.Get_Name().c_str())
        return False

    #_____________________________________
    # Save results to file:

    dir = Tool.Get_Parameter('DIR').asDataObject()
    len = Tool.Get_Parameter('LEN').asDataObject()

    return dir, len

