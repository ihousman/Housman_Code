import os, sys
from r_numpy_lib import *
import numpy
#import numpy as np
from numpy import numarray
try:
    from numpy.numarray import nd_image
except:
    print 'Cannot use nd_image functions'
##from mpl_toolkits.basemap import Basemap, cm
##from netCDF4 import Dataset as NetCDFFile
###############################################################################
#Set Python version
python_possibilities = {'C:\\Python26\\ArcGIS10.0': [26, 10], 'C:\\Python26': [26, 9.3],'C:\\Python25' : [25, 9.3]}
for possibility in python_possibilities:
    if os.path.exists(possibility):
        arc_version = python_possibilities[possibility][1]
        python_version =   python_possibilities[possibility][0]
        python_dir = possibility
        break
print 'Arc version:',arc_version
print 'Python version:', python_version
print 'Python dir:', python_dir
#arc_version =9.3
#python_version = 26
python_version_dec = str(float(python_version)/10)
python_version = str(python_version)
admin = False
gdal_dir = 'C:/Program Files/FWTools2.4.7/bin/'


if os.path.exists(python_dir)==False:
    print 'Python version:', python_version, 'Arc version:', arc_version,'does not exist'
    raw_input('Press enter to exit')
    sys.exit()
###############################################################################
cwd = os.getcwd()
parts = cwd.split('\\')
cwd = ''
for part in parts:
    cwd += part + '/'
###############################################################################

##################################################################
try:
    import matplotlib.pyplot as plt
except:
    #install('matplotlib')
    try:
        import matplotlib.pyplot as plt
    except:
        print 'Installation of matplotlib was unsuccessful'
        print 'Please search for matplotlib-1.1.1rc.win32-py'+python_version_dec+'.exe and manually install'
        #raw_input('Press enter to exit')
        #sys.exit()
##################################################################
def map_maker(input_list, output_map, title = '', labels = True, nodata = 0, colorbar = True, size = (20, 8), axis = 'off', color = plt.cm.RdBu_r, Min = 20, Max = 80, band_no = 1, rows = 1):
    
    #try:
    fig = None
    fig = plt.figure(figsize = size)
    
    columns = int(math.ceil(len(input_list)/ int(rows)))
    rows = str(rows)

    i = str(rows) + str(columns) + '1'
    i = int(i)
    #print i
    for Input in input_list:
        print i
        info = raster_info(Input)
        array = raster(Input, dt = info['dt'], band_no = band_no)
        #array[array <= 0] = None
        array = numpy.ma.masked_where(array == nodata, array)
        plt.subplot(i)
        plt.imshow(array, cmap = color, vmin = Min, vmax = Max)
        plt.axis(axis)
        
        plt.subplots_adjust(wspace = 0, hspace = 0, top = 0.99, bottom = 0.01, left = 0.05, right = 0.99)
        #plt.contour(array, [50, 70])
        i += 1
    
    if colorbar == True:
        plt.colorbar()
    if title != '':
        plt.title(title)
        
    print 'yay'    
    #plt.show()
    fig.savefig(output_map, format = output_map[-3:], dpi = fig.dpi)

    
    fig = None

    array = None
def table_to_raster(table, output, header = True, delimiter = '\t'):
    open_table = open(table, 'r')
    lines = open_table.readlines()
    print lines
    print open_table.read()
    open_table.close()
    cellText = ''
    for line in lines:
        cellText += line
    bbox = dict(boxstyle='round', facecolor= 'wheat', alpha=0.5)
    fig, ax = plt.subplots(1,1)
    fig.text(0.05, 0.05, cellText, transform = ax.transAxes, verticalalignment = 'top')
    plt.show()
############################################################################   
def sort(in_list, order = range(1000), num_break = '_', num_place = 0):
    out_list = []
    for num in order:
        for entry in in_list:
            if str(num) == entry.split(num_break)[num_place]:
                out_list.append(entry)
    return out_list
############################################################################    
    
##base_dir = 'O:/02_Inputs/MODIS/Baltimore/Outputs/'
##out_folder = 'O:/02_Inputs/MODIS/Baltimore/maps/'
##if os.path.exists(out_folder) == False:
##    os.makedirs(out_folder)
##
##Dirs = os.listdir(base_dir)
##Dirs = sort(Dirs)
##for Dir in Dirs[:1]:
##    run_dir = base_dir + Dir + '/'
##    #images = os.listdir(run_dir)
##    image = run_dir + Dir + '_cubist_output.img'
##    plot = image + '_training_vs_modeled_plot.png'
##    table = image + '_parameters_report.txt'
##    #print os.path.exists(plot), os.path.exists(image)
##    if os.path.exists(image) == True and os.path.exists(plot) == True:
##        
##        out_map = out_folder + Dir + '_map.png'
##        if os.path.exists(out_map) == False:
##            print 'Making', out_map
            #map_maker([image, plot], out_map, title = Dir)
    #table_to_raster(table, table + '_plot.png')
            
##image = Dir + '19_balt_sample__AST__summer__day__VCT_summer_cubist_output.img'
##plot = Dir + '19_balt_sample__AST__summer__day__VCT_summer_cubist_output.img_training_vs_modeled_plot.png'
##image_list = [image, plot]
##output_map = 'test_map.png'
##
##map_maker(image_list, output_map)
#plt.figure(figsize = (20,8))
#plt.subplot(111)
def proj_coord_to_array_location(shapefile, raster):
    info = raster_info(raster)
    xys = xy_coords(shapefile, False)
    
    coords = info['coords']
    res = info['res']
    xmin = coords[0]
    ymin = coords[1]
    
    height = info['height']
    width = info['width']
    out_listx = []
    out_listy = []
    for xy in xys:
        
        xdif = math.ceil((xy[0] - xmin)) / res
        ydif = height - (math.ceil((xy[1] - ymin))/ res)
        out_listx.append(xdif)
        out_listy.append(ydif)
    return out_listx, out_listy



######################################################################################

def get_color_list():
    #maps = sorted(m for m in plt.cm.datad if not m.endswith("_r"))
    maps = sorted(plt.cm.datad)
    return maps
def display_colors():
    a = numpy.linspace(0, 1, 256).reshape(1,-1)
    a = numpy.vstack((a,a))

    # Get a list of the colormaps in matplotlib.  Ignore the ones that end with
    # '_r' because these are simply reversed versions of ones that don't end
    # with '_r'
    maps = sorted(m for m in plt.cm.datad if not m.endswith("_r"))
    
    nmaps = len(maps) + 1

    fig = plt.figure(figsize=(5,10))
    fig.subplots_adjust(top=0.99, bottom=0.01, left=0.2, right=0.99)
    for i,m in enumerate(maps):
        ax = plt.subplot(nmaps, 1, i+1)
        plt.axis("off")
        plt.imshow(a, aspect='auto', cmap=plt.get_cmap(m), origin='lower')
        pos = list(ax.get_position().bounds)
        fig.text(pos[0] - 0.01, pos[1], m, fontsize=10, horizontalalignment='right')

    plt.show()
#get_color_list()
#display_colors()
#Displays a list of images or bands within a stack using matplotlib
def display_chips(chip_list, dt = '', xoffset = 0, yoffset = 0, width = '', height = '',band_no = 1, band_list = [], column_max = 5, ignore_value = 0, std_stretch = 2, hist_or_image = 'image',color = plt.get_cmap('RdYlBu_r'), fig_size = (20, 20)):
    if hist_or_image == 'scatter':
        band_list = [1,2,3] 
    if type(color) == 'str':
        color = plt.get_cmap(color)
    fig = None
    fig = plt.figure(figsize = fig_size)

    if type(chip_list) != list:
        #plt.title(os.path.basename(chip_list))
        if dt == '':
            dt = raster_info(chip_list)['dt']
        array = brick(chip_list, dt = dt, xoffset = xoffset, yoffset = yoffset, width = width, height = height, band_list = band_list)
        length = len(array)
        stacki = True
    else:
        #plt.title(os.path.basename(chip_list[0]))      
        if dt == '':
            dt = raster_info(chip_list[0])['dt']
        length = len(chip_list)
        stacki = False
        array = []
        for chip in chip_list:
            array.append(raster(chip, dt = dt, band_no = band_no, xoffset = xoffset, yoffset = yoffset, width = width, height = height))
        array = numpy.array(array)

    rows = int(math.ceil(length/ column_max ))
    if rows == 0:
        rows = 1
    columns = int(math.ceil(length/rows)) 

    row_column_list = []
    for row in range(0,rows + 1):
        for column in range(columns):
            row_column_list.append([row, column])
    if hist_or_image == 'scatter':
        from mpl_toolkits.mplot3d import Axes3D
        ax = fig.add_subplot(111, projection='3d')
        ax.scatter(array[0][0::100], array[1][0::100], array[2][0::100])
        ax.set_xlabel('X Label')
        ax.set_ylabel('Y Label')
        ax.set_zlabel('Z Label')
    else:
        shape = (rows + 1, columns)
        i = 0
        if band_list == []:
            band_list = range(1, len(array) + 1)
        for band in array:
            
            plt.subplot2grid(shape = shape, loc = row_column_list[i])
            if ignore_value != '':
                bt = band[band != int(ignore_value)]
            else:
                bt = band
            mean = numpy.mean(bt)
            std = numpy.std(bt)
            bt = None
            stretch_min = mean - (std * std_stretch)
            stretch_max = mean + (std * std_stretch)

            if hist_or_image == 'image':
                t = plt.imshow(band,cmap = color,vmin = stretch_min, vmax = stretch_max)
                plt.axis('off')
                plt.text(-.2,-.2, str(band_list[i]))
            elif hist_or_image == 'hist':
                
                bns = int(math.ceil(numpy.log10(len(numpy.unique(band))) * 20))
                if bns == 0:
                    bns = len(numpy.unique(band))
                band = band.flatten()
                
                if ignore_value != '':
                    band = band[band != int(ignore_value)]
          
                n, bis, patches = plt.hist(band, bins =bns)
                plt.subplots_adjust( hspace = 0.1,wspace = 0.005, top = 0.95, bottom = 0.01, left = 0.05, right = 0.99)
                
                xs = [stretch_min, stretch_max]
                ys = n
                
                ydummies = [max(ys)] * len(xs)
                xdummies_min = [min(xs)] * len(ys)
                xdummies_max = [max(xs)] * len(ys)
                plt.plot(xs, ydummies)
                plt.plot(xdummies_min, ys)
                plt.plot(xdummies_max, ys)

                plt.text(min(xs),max(ys), str(band_list[i]))

           
            i += 1
    array = None
    
##    try:
##        metadata = os.path.splitext(chip_list)[0] + '_metadata.txt'
##        mo = open(metadata, 'r')
##        lines = mo.readlines()
##        li = 1
##        for line in lines:
##            plt.text(li, li, line)#, transform = ax.transAxes)
##            li += 1
##    except:
##        metadata = None
    return fig
    #plt.show()
    
    fig = None

#image = 'O:/02_Inputs/Aster/Bend/Inputs/Landsat_Thermal/Landsat_LPGS_B60_Stack.img'
#display_chips(image, ignore_value = 0, std_stretch = 2, hist_or_image = 'image', band_list = [2,5])

##def scatter():
##    import numpy as np
##    from mpl_toolkits.mplot3d import Axes3D
####    def randrange(n, vmin, vmax):
####        return (vmax-vmin)*np.random.rand(n) + vmin
####
##    fig = plt.figure()
##    ax = fig.add_subplot(111, projection='3d')
####    n = 100
####    for c, m, zl, zh in [('r', 'o', -50, -25), ('b', '^', -30, -5)]:
####        print c, m, zl, zh
####        xs = randrange(n, 23, 32)
####        ys = randrange(n, 0, 100)
####        zs = randrange(n, zl, zh)
####        ax.scatter(xs, ys, zs, c=c, marker=m)
##    x = range(50)
##    ax.scatter(x,x,x)
##    ax.set_xlabel('X Label')
##    ax.set_ylabel('Y Label')
##    ax.set_zlabel('Z Label')
##
##    plt.show()
#scatter()
##
##class LineBuilder:
##    def __init__(self, line):
##        self.line = line
##        self.xs = list(line.get_xdata())
##        self.ys = list(line.get_ydata())
##        self.cid = line.figure.canvas.mpl_connect('button_press_event', self)
##
##    def __call__(self, event):
##        print 'click', event
##        if event.inaxes!=self.line.axes: return
##        self.xs.append(event.xdata)
##        self.ys.append(event.ydata)
##        self.line.set_data(self.xs, self.ys)
##        self.line.figure.canvas.draw()
##
####fig = plt.figure()
####ax = fig.add_subplot(111)
####ax.set_title('click to build line segments')
####line, = ax.plot([0], [0])  # empty line
####linebuilder = LineBuilder(line)
####
####plt.show()
##
##
##class DraggableRectangle:
##    def __init__(self, rect):
##        self.rect = rect
##        self.press = None
##
##    def connect(self):
##        'connect to all the events we need'
##        self.cidpress = self.rect.figure.canvas.mpl_connect(
##            'button_press_event', self.on_press)
##        self.cidrelease = self.rect.figure.canvas.mpl_connect(
##            'button_release_event', self.on_release)
##        self.cidmotion = self.rect.figure.canvas.mpl_connect(
##            'motion_notify_event', self.on_motion)
##
##    def on_press(self, event):
##        'on button press we will see if the mouse is over us and store some data'
##        if event.inaxes != self.rect.axes: return
##
##        contains, attrd = self.rect.contains(event)
##        if not contains: return
##        print 'event contains', self.rect.xy
##        x0, y0 = self.rect.xy
##        self.press = x0, y0, event.xdata, event.ydata
##
##    def on_motion(self, event):
##        'on motion we will move the rect if the mouse is over us'
##        if self.press is None: return
##        if event.inaxes != self.rect.axes: return
##        x0, y0, xpress, ypress = self.press
##        dx = event.xdata - xpress
##        dy = event.ydata - ypress
##        #print 'x0=%f, xpress=%f, event.xdata=%f, dx=%f, x0+dx=%f'%(x0, xpress, event.xdata, dx, x0+dx)
##        self.rect.set_x(x0+dx)
##        self.rect.set_y(y0+dy)
##
##        self.rect.figure.canvas.draw()
##
##
##    def on_release(self, event):
##        'on release we reset the press data'
##        self.press = None
##        self.rect.figure.canvas.draw()
##
##    def disconnect(self):
##        'disconnect all the stored connection ids'
##        self.rect.figure.canvas.mpl_disconnect(self.cidpress)
##        self.rect.figure.canvas.mpl_disconnect(self.cidrelease)
##        self.rect.figure.canvas.mpl_disconnect(self.cidmotion)
##
####fig = plt.figure()
####ax = fig.add_subplot(111)
####rects = ax.bar(range(10), 20*np.random.rand(10))
####drs = []
####for rect in rects:
####    dr = DraggableRectangle(rect)
####    dr.connect()
####    drs.append(dr)
####
####plt.show()
##
##
##
####fig = plt.figure()
####ax = fig.add_subplot(111)
####ax.set_title('click on points')
####
####line, = ax.plot(np.random.rand(100), 'o', picker=5)  # 5 points tolerance
####
####def onpick(event):
####    thisline = event.artist
####    xdata = thisline.get_xdata()
####    ydata = thisline.get_ydata()
####    ind = event.ind
####    print 'onpick points:', zip(xdata[ind], ydata[ind])
##
####fig.canvas.mpl_connect('pick_event', onpick)
####
####plt.show()
##
##from matplotlib import pyplot
##import sys
##
##def _get_limits( ax ):
##    """ Return X and Y limits for the passed axis as [[xlow,xhigh],[ylow,yhigh]]
##    """
##    return [list(ax.get_xlim()), list(ax.get_ylim())]
##
##def _set_limits( ax, lims ):
##    """ Set X and Y limits for the passed axis
##    """
##    ax.set_xlim(*(lims[0]))
##    ax.set_ylim(*(lims[1]))
##    return
##
##def pre_zoom( fig ):
##    """ Initialize history used by the re_zoom() event handler.
##        Call this after plots are configured and before pyplot.show().
##    """
##    global oxy
##    oxy = [_get_limits(ax) for ax in fig.axes]
##    # :TODO: Intercept the toolbar Home, Back and Forward buttons.
##    return
##
##def re_zoom(event):
##    """ Pyplot event handler to zoom all plots together, but permit them to
##        scroll independently.  Created to support eyeball correlation.
##        Use with 'motion_notify_event' and 'button_release_event'.
##    """
##    global oxy
##    for ax in event.canvas.figure.axes:
##        navmode = ax.get_navigate_mode()
##        if navmode is not None:
##            break
##    scrolling = (event.button == 1) and (navmode == "PAN")
##    if scrolling:                   # Update history (independent of event type)
##        oxy = [_get_limits(ax) for ax in event.canvas.figure.axes]
##        return
##    if event.name != 'button_release_event':    # Nothing to do!
##        return
##    # We have a non-scroll 'button_release_event': Were we zooming?
##    zooming = (navmode == "ZOOM") or ((event.button == 3) and (navmode == "PAN"))
##    if not zooming:                 # Nothing to do!
##        oxy = [_get_limits(ax) for ax in event.canvas.figure.axes]  # To be safe
##        return
##    # We were zooming, but did anything change?  Check for zoom activity.
##    changed = None
##    zoom = [[0.0,0.0],[0.0,0.0]]    # Zoom from each end of axis (2 values per axis)
##    for i, ax in enumerate(event.canvas.figure.axes): # Get the axes
##        # Find the plot that changed
##        nxy = _get_limits(ax)
##        if (oxy[i] != nxy):         # This plot has changed
##            changed = i
##            # Calculate zoom factors
##            for j in [0,1]:         # Iterate over x and y for each axis
##                # Indexing: nxy[x/y axis][lo/hi limit]
##                #           oxy[plot #][x/y axis][lo/hi limit]
##                width = oxy[i][j][1] - oxy[i][j][0]
##                # Determine new axis scale factors in a way that correctly
##                # handles simultaneous zoom + scroll: Zoom from each end.
##                zoom[j] = [(nxy[j][0] - oxy[i][j][0]) / width,  # lo-end zoom
##                           (oxy[i][j][1] - nxy[j][1]) / width]  # hi-end zoom
##            break                   # No need to look at other axes
##    if changed is not None:
##        for i, ax in enumerate(event.canvas.figure.axes): # change the scale
##            if i == changed:
##                continue
##            for j in [0,1]:
##                width = oxy[i][j][1] - oxy[i][j][0]
##                nxy[j] = [oxy[i][j][0] + (width*zoom[j][0]),
##                          oxy[i][j][1] - (width*zoom[j][1])]
##            _set_limits(ax, nxy)
##        event.canvas.draw()         # re-draw the canvas (if required)
##        pre_zoom(event.canvas.figure)   # Update history
##    return
### End re_zoom()
##
##def main(argv):
##    """ Test/demo code for re_zoom() event handler.
##    """
##    import numpy
##    x = numpy.linspace(0,100,1000)      # Create test data
##    y = numpy.sin(x)*(1+x)
##
##    fig = pyplot.figure()               # Create plot
##    ax1 = pyplot.subplot(211)
##    ax1.plot(x,y)
##    ax2 = pyplot.subplot(212)
##    ax2.plot(x,y)
##
##    pre_zoom( fig )                     # Prepare plot event handler
##    pyplot.connect('motion_notify_event', re_zoom)  # for right-click pan/zoom
##    pyplot.connect('button_release_event',re_zoom)  # for rectangle-select zoom
##
##    pyplot.show()                       # Show plot and interact with user
### End main()
##
##if __name__ == "__main__":
##    # Script is being executed from the command line (not imported)
##    main(sys.argv)

# End of file ScrollTest.py
##Dir = 'O:/02_Inputs/Aster/Baltimore/Outputs/333_balt_sample__AST__sum__day__LPGS_s__win__LPGS_w__DEM/'
####shp = Dir + 'nlcd_sample.shp'
##image = Dir + '333_balt_sample__AST__sum__day__LPGS_s__win__LPGS_w__DEM_cubist_output_nf.nf'
##img = Dir + '333_balt_sample__AST__sum__day__LPGS_s__win__LPGS_w__DEM_cubist_output.img'
##
##training_pts = Dir + 'balt_sample.shp'
##plot_coordsx, plot_coordsy = proj_coord_to_array_location(training_pts, img)
##info = raster_info(img)
##array = raster(img)
##coords = info['coords']
##zone = info['zone']
##mins = coords[:2]
##maxes = coords[2:]
##mins_geog = utm_to_geog(zone, mins[0], mins[1])
##maxes_geog = utm_to_geog(zone, maxes[0], maxes[1])
##
##total_width =  info['width'] * info['res']
##total_height = info['height'] * info['res']
####print total_width
####print int(mins_geog[1])
####m = Basemap(projection = 'sinu', lon_0 = mins_geog[1], lat_0 = mins_geog[0], width =int(total_width), height = int(total_height), resolution ='l')#, llcrnrlat = mins_geog[0],llcrnrlon = mins_geog[1], urcrnrlat = maxes_geog[0], urcrnrlon = maxes_geog[1], resolution = 'l')
####m.drawstates()
####m.drawcountries()
####m.bluemarble()
#####m.pcolormesh(
####m.drawcoastlines(color = 'r')
####m.drawrivers(color = 'b')
####plt.pcolormesh(array)
####m.imshow(array)
##
##plt.figure(figsize = (20,8))
##plt.subplot(111)
##plt.imshow(array)
##plt.plot(plot_coordsx, plot_coordsy, 'r.')
##plt.show()
##
####nc = NetCDFFile(image)
####prcpvar = nc.variables['Band1']
####data = prcpvar[:]
####array = raster(img)
####print array
####print data
####
####latcorners = nc.variables['lat'][:]
####print latcorners
##
##array = None
##data = None
###print prcpvar
###print nc
##
####Map = Basemap(projection = 'aea', width = 100000, height = 100000, lon_0 = -76.67, lat_0 = 39.18)
#####Map.drawcoastlines()
#####Map.fillcontinents(color='coral')
#####Map.drawmapscale(-76.67, 39.18, -80, 40000, 10000)
#####Map.drawmapscale(
####Map.drawstates()
####Map.drawgreatcircle(-70, 40, -100, 40)
####Map.etopo()
#####Map.imshow('O:/02_Inputs/MODIS/Baltimore/Outputs/5_nlcd_sample__009__winter__day__217__summer__night/5_nlcd_sample__009__winter__day__217__summer__night_cubist_output.img')
####Map.readshapefile(os.path.splitext(shp)[0],name = 'Test')# os.path.basename(os.path.splitext(shp)[0]))
#####Map.bluemarble()
#####plt.imshow(Map)
####plt.title('Test Map')
####plt.show()

