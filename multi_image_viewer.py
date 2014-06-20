from r_numpy_lib import *
from Tkinter import *
try:
    import matplotlib.pyplot as plt
except:
    install('matplotlib')
    try:
        import matplotlib.pyplot as plt
    except:
        print 'Installation of matplotlib was unsuccessful'
        print 'Please search for matplotlib-1.1.1rc.win32-py'+python_version_dec+'.exe and manually install'
        raw_input('Press enter to exit')
        sys.exit()

########################################################
def display_chips(chip_list, dt = 'Int16', band_no = 1, column_max = 8, std_stretch = 3, color = plt.cm.RdBu_r, fig_size = (20, 10)):

    fig = None
    fig = plt.figure(figsize = fig_size)
    
    if type(chip_list) != list:
        array = brick(chip_list, dt = dt)
        length = len(array)
        stacki = True
    else:
        length = len(chip_list)
        stacki = False
        array = []
        for chip in chip_list:
            array.append(raster(chip, dt = dt, band_no = band_no))
        array = numpy.array(array)

    rows = int(math.ceil(length/ column_max )) 
    columns = int(math.ceil(length/rows)) 

    row_column_list = []
    for row in range(0,rows + 1):
        for column in range(columns):
            row_column_list.append([row, column])
    
    shape = (rows + 1, columns)
    i = 0
    for band in array:
    
        plt.subplot2grid(shape = shape, loc = row_column_list[i])

        mean = numpy.mean(band)
        std = numpy.std(band)
        stretch_min = mean - (std * std_stretch)
        stretch_max = mean + (std * std_stretch)
        plt.imshow(band,cmap = color, vmin = stretch_min, vmax = stretch_max)

        plt.subplots_adjust( hspace = 0.1,wspace = 0, top = 0.95, bottom = 0.01, left = 0.05, right = 0.99)
        plt.text(-.2,-.2, str(i + 1))
        plt.axis('off')
        
        i += 1
  
    plt.show()
   
    array = None

    
Dir = 'O:/02_Inputs/MODIS/Atlanta/Inputs/Thermal_Stack_Inputs/'
#images = map(lambda i : Dir + i, filter(lambda i: i.find('_1_t.img') > -1 and i.find('.aux.xml') == -1 , os.listdir(Dir)))
images = Dir + 'Atlanta_MODIS_day.img'
#display_chips(images)
import matplotlib.pyplot as plt
import numpy as np

# Simple data to display in various forms
x = np.linspace(0, 2*np.pi, 400)
y = np.sin(x**2)

plt.close('all')

# Just a figure and one subplot
f, ax = plt.subplots()
ax.plot(x, y)
ax.set_title('Simple plot')

# Two subplots, the axes array is 1-d
f, axarr = plt.subplots(2, sharex=True)
axarr[0].plot(x, y)
axarr[0].set_title('Sharing X axis')
axarr[1].scatter(x, y)

# Two subplots, unpack the axes array immediately
f, (ax1, ax2) = plt.subplots(1, 2, sharey=True)
ax1.plot(x, y)
ax1.set_title('Sharing Y axis')
ax2.scatter(x, y)

# Three subplots sharing both x/y axes
f, (ax1, ax2, ax3) = plt.subplots(3, sharex=True, sharey=True)
ax1.plot(x, y)
ax1.set_title('Sharing both axes')
ax2.scatter(x, y)
ax3.scatter(x, 2*y**2-1,color='r')
# Fine-tune figure; make subplots close to each other and hide x ticks for
# all but bottom plot.
f.subplots_adjust(hspace=0)
plt.setp([a.get_xticklabels() for a in f.axes[:-1]], visible=False)

# Four axes, returned as a 2-d array
f, axarr = plt.subplots(2, 2)
axarr[0,0].plot(x, y)
axarr[0,0].set_title('Axis [0,0]')
axarr[0,1].scatter(x, y)
axarr[0,1].set_title('Axis [0,1]')
axarr[1,0].plot(x, y**2)
axarr[1,0].set_title('Axis [1,0]')
axarr[1,1].scatter(x, y**2)
axarr[1,1].set_title('Axis [1,1]')
# Fine-tune figure; hide x ticks for top plots and y ticks for right plots
plt.setp([a.get_xticklabels() for a in axarr[0,:]], visible=False)
plt.setp([a.get_yticklabels() for a in axarr[:,1]], visible=False)

# Four polar axes
plt.subplots(2, 2, subplot_kw=dict(polar=True))

plt.show()
