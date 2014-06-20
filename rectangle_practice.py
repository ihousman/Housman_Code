from pylab import arange, plot, sin, ginput, show
##t = arange(10)
##plot(t, sin(t))
##print "Please click"
##x = ginput(3)
##print "clicked",x
##show()

#!/usr/bin/env python
# -*- noplot -*-
"""
This provides examples of uses of interactive functions, such as ginput,
waitforbttonpress and manual clabel placement.

This script must be run interactively using a backend that has a
graphical user interface (for example, using GTKAgg backend, but not
PS backend).

See also ginput_demo.py
"""
#import time
import matplotlib
import numpy
#import matplotlib.cm as cm
#import matplotlib.mlab as mlab
import matplotlib.pyplot as plt

def tellme(s):
    print s
    plt.title(s,fontsize=16)
    plt.draw()

##################################################
# Define a triangle by clicking three points
##################################################
#plt.clf()


def get_points():
  plt.axis([0.,1.,0.,1.])
  plt.setp(plt.gca(),autoscale_on=False)
  happy = False
  while not happy:
    tellme('Hit the Enter key when finished slecting points')
    pts = numpy.asarray(plt.ginput(500, timeout = -1))
    ph = plt.plot(pts[:,0], pts[:,1], 'ro')
    tellme('Hit the Enter key to accept these points\nMouse button to reject')
   
    happy = plt.waitforbuttonpress()
    if not happy:
      for p in ph: p.remove()
    else:
      return pts
pts = get_points()
print pts
##happy = False
##while not happy:
##    pts = []
##    while len(pts) < 3:
##        tellme('Select 3 corners with mouse')
##        pts = np.asarray( plt.ginput(3,timeout=-1) )
##        
##        if len(pts) < 3:
##            tellme('Too few points, starting over')
##            time.sleep(1) # Wait a second
##
##    ph = plt.fill( pts[:,0], pts[:,1], 'r', lw=2 )
##
##    tellme('Happy? Key click for yes, mouse click for no')
##
##    happy = plt.waitforbuttonpress()
##
##    # Get rid of fill
##    if not happy:
##        for p in ph: p.remove()

####################################################
### Now contour according to distance from triangle
### corners - just an example
####################################################
##
### Define a nice function of distance from individual pts
##def f(x,y,pts):
##    z = np.zeros_like(x)
##    for p in pts:
##        z = z + 1/(np.sqrt((x-p[0])**2+(y-p[1])**2))
##    return 1/z
##
##X,Y = np.meshgrid( np.linspace(-1,1,51), np.linspace(-1,1,51) )
##Z = f(X,Y,pts)
##
##CS = plt.contour( X, Y, Z, 20 )
##
##tellme( 'Use mouse to select contour label locations, middle button to finish' )
##CL = plt.clabel( CS, manual=True )
##
####################################################
### Now do a zoom
####################################################
##tellme( 'Now do a nested zoom, click to begin' )
##plt.waitforbuttonpress()
##
##happy = False
##while not happy:
##    tellme( 'Select two corners of zoom, middle mouse button to finish' )
##    pts = np.asarray( plt.ginput(2,timeout=-1) )
##
##    happy = len(pts) < 2
##    if happy: break
##
##    pts = np.sort(pts,axis=0)
##    plt.axis( pts.T.ravel() )
##
##tellme('All Done!')
plt.show()
##from matplotlib.pyplot import figure, show
##from matplotlib.lines import Line2D
##from matplotlib.patches import Patch, Rectangle
##from matplotlib.text import Text
##from matplotlib.image import AxesImage
##import numpy as npy
##from numpy.random import rand
##
##if 1: # simple picking, lines, rectangles and text
##    fig = figure()
##    ax1 = fig.add_subplot(211)
##    ax1.set_title('click on points, rectangles or text', picker=True)
##    ax1.set_ylabel('ylabel', picker=True, bbox=dict(facecolor='red'))
##    line, = ax1.plot(rand(100), 'o', picker=5)  # 5 points tolerance
##
##    # pick the rectangle
##    ax2 = fig.add_subplot(212)
##
##    bars = ax2.bar(range(10), rand(10), picker=True)
##    for label in ax2.get_xticklabels():  # make the xtick labels pickable
##        label.set_picker(True)
##
##
##    def onpick1(event):
##        if isinstance(event.artist, Line2D):
##            thisline = event.artist
##            xdata = thisline.get_xdata()
##            ydata = thisline.get_ydata()
##            ind = event.ind
##            print 'onpick1 line:', zip(npy.take(xdata, ind), npy.take(ydata, ind))
##        elif isinstance(event.artist, Rectangle):
##            patch = event.artist
##            print 'onpick1 patch:', patch.get_path()
##        elif isinstance(event.artist, Text):
##            text = event.artist
##            print 'onpick1 text:', text.get_text()
##
##
##
##    fig.canvas.mpl_connect('pick_event', onpick1)
##
##if 1: # picking with a custom hit test function
##    # you can define custom pickers by setting picker to a callable
##    # function.  The function has the signature
##    #
##    #  hit, props = func(artist, mouseevent)
##    #
##    # to determine the hit test.  if the mouse event is over the artist,
##    # return hit=True and props is a dictionary of
##    # properties you want added to the PickEvent attributes
##
##    def line_picker(line, mouseevent):
##        """
##        find the points within a certain distance from the mouseclick in
##        data coords and attach some extra attributes, pickx and picky
##        which are the data points that were picked
##        """
##        if mouseevent.xdata is None: return False, dict()
##        xdata = line.get_xdata()
##        ydata = line.get_ydata()
##        maxd = 0.05
##        d = npy.sqrt((xdata-mouseevent.xdata)**2. + (ydata-mouseevent.ydata)**2.)
##
##        ind = npy.nonzero(npy.less_equal(d, maxd))
##        if len(ind):
##            pickx = npy.take(xdata, ind)
##            picky = npy.take(ydata, ind)
##            props = dict(ind=ind, pickx=pickx, picky=picky)
##            return True, props
##        else:
##            return False, dict()
##
##    def onpick2(event):
##        print 'onpick2 line:', event.pickx, event.picky
##
##    fig = figure()
##    ax1 = fig.add_subplot(111)
##    ax1.set_title('custom picker for line data')
##    line, = ax1.plot(rand(100), rand(100), 'o', picker=line_picker)
##    fig.canvas.mpl_connect('pick_event', onpick2)
##
##
##if 1: # picking on a scatter plot (matplotlib.collections.RegularPolyCollection)
##
##    x, y, c, s = rand(4, 100)
##    def onpick3(event):
##        ind = event.ind
##        print 'onpick3 scatter:', ind, npy.take(x, ind), npy.take(y, ind)
##
##    fig = figure()
##    ax1 = fig.add_subplot(111)
##    col = ax1.scatter(x, y, 100*s, c, picker=True)
##    #fig.savefig('pscoll.eps')
##    fig.canvas.mpl_connect('pick_event', onpick3)
##
##if 1: # picking images (matplotlib.image.AxesImage)
##    fig = figure()
##    ax1 = fig.add_subplot(111)
##    im1 = ax1.imshow(rand(10,5), extent=(1,2,1,2), picker=True)
##    im2 = ax1.imshow(rand(5,10), extent=(3,4,1,2), picker=True)
##    im3 = ax1.imshow(rand(20,25), extent=(1,2,3,4), picker=True)
##    im4 = ax1.imshow(rand(30,12), extent=(3,4,3,4), picker=True)
##    ax1.axis([0,5,0,5])
##
##    def onpick4(event):
##        artist = event.artist
##        if isinstance(artist, AxesImage):
##            im = artist
##            A = im.get_array()
##            print 'onpick4 image', A.shape
##
##    fig.canvas.mpl_connect('pick_event', onpick4)
##
##
##show()
##
##from matplotlib.widgets import  RectangleSelector
##from pylab import *
###from matplotlib.patches import Rectangle
##import matplotlib
##import matplotlib.pyplot as plt
##from numpy import *

##def onselect(eclick, erelease):
##  'eclick and erelease are matplotlib events at press and release'
##  print ' startposition : (%f, %f)' % (eclick.xdata, eclick.ydata)
##  print ' endposition   : (%f, %f)' % (erelease.xdata, erelease.ydata)
##  print ' used button   : ', eclick.button
##  rect1 = matplotlib.patches.Rectangle((eclick.xdata, eclick.ydata), 100,100, fill = False)
##  try:
##    ax.remove(rect1)
##  except:
##    print 'oops'
##  ax.add_patch(rect1)
##  
##def toggle_selector(event):
##    print ' Key pressed.'
##    if event.key in ['Q', 'q'] and toggle_selector.RS.active:
##        print ' RectangleSelector deactivated.'
##        toggle_selector.RS.set_active(False)
##    if event.key in ['A', 'a'] and not toggle_selector.RS.active:
##        print ' RectangleSelector activated.'
##        toggle_selector.RS.set_active(True)
##    
##x = arange(100)
##y = sin(x)
##fig = plt.figure()
##ax = plt.subplot(111)
##ax.plot(x,y)
##plt.xlim([0, 400])
##plt.ylim([0,100])
##toggle_selector.RS = RectangleSelector(ax, onselect, drawtype='box')
##connect('key_press_event', toggle_selector)
##show()
####import matplotlib
####import matplotlib.pyplot as plt
####
####fig = plt.figure()
####ax = fig.add_subplot(111)
####rect0 = matplotlib.patches.Ellipse((-100, 50), 100, 100,color = 'blue')
####rect1 = matplotlib.patches.Rectangle((-200,-100), 400, 200, fill = False)
####rect2 = matplotlib.patches.Rectangle((0,150), 300, 20, color='red')
####rect3 = matplotlib.patches.Rectangle((-300,-50), 40, 200, color='#0099FF')
####circle1 = matplotlib.patches.Circle((-200,-250), radius=90, color='#EB70AA')
####ax.add_patch(rect0)
####ax.add_patch(rect1)
####ax.add_patch(rect2)
####ax.add_patch(rect3)
####ax.add_patch(circle1)
####plt.xlim([-400, 400])
####plt.ylim([-400, 400])
####plt.show()
####import matplotlib.pyplot as plt
####import numpy as np
####
####from matplotlib.widgets import RectangleSelector
####from matplotlib.transforms import Bbox
####
####def main():
####    # Generate some random data:
####    data = []
####    for track_id in xrange(100):
####        a, b = np.random.random(2)
####        x = 100 * a + np.random.random(100).cumsum()
####        y = np.cos(x) + b * np.random.random(100).cumsum()
####        data.append((track_id, x, y))
####
####    # Plot it, keeping track of the "track_id"
####    fig, ax = plt.subplots()
####    for track_id, x, y in data:
####        line, = ax.plot(x,y)
####        line.track_id = track_id
####
####    # Make the selector...
####    selector = RectangleSelector(ax, onselect, drawtype='box')
####    # We could set up a button or keyboard shortcut to activate this, instead...
####    selector.set_active(True)
####
####    plt.show()
####
####def onselect(eclick, erelease):
####    """Get the lines in an axis with vertices inside the region selected.
####    "eclick" and "erelease" are matplotlib button_click and button_release
####    events, respectively."""
####    # Make a matplotlib.transforms.Bbox from the selected region so that we
####    # can more easily deal with finding if points are inside it, etc...
####    left, bottom = min(eclick.x, erelease.x), min(eclick.y, erelease.y)
####    right, top = max(eclick.x, erelease.x), max(eclick.y, erelease.y)
####    region = Bbox.from_extents(left, bottom, right, top)
####
####    track_ids = []
####    ax = eclick.inaxes
####    for line in ax.lines:
####        bbox = line.get_window_extent(eclick.canvas)
####        # Start with a rough overlaps...
####        if region.overlaps(bbox):
####            # We need the xy data to be in display coords...
####            xy = ax.transData.transform(line.get_xydata())
####
####            # Then make sure that at least one vertex is really inside...
####            if any(region.contains(x,y) for x,y in xy):
####                # Highlight the selected line by making it bold
####                line.set_linewidth(3)
####                track_ids.append(line.track_id)
####
####    print track_ids
####    eclick.canvas.draw()
####
####if __name__ == '__main__':
####    main()
##
### build thumbnails of all images in a directory
##
##i = 'R:/NAFD/Landtrendr/tSAT/test_inputs/ud_stack_clip.tif'
##out = os.path.splitext(i)[0] + '_thumb.png'
###fig = image.thumbnail(i, out, scale = 0.1)
##
