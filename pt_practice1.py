from pylab import *
import numpy


def hello(event):
    x = event.xdata
    y = event.ydata
    xy = [x,y]
    xy_list.append(xy)
    print xy_list
    print a[:,int(y),int(x)]
    #if xy != self.last:
       # print xy
    #print 'hello',event.xdata, event.ydata
    ax.plot(event.xdata, event.ydata, 'ro')
    draw()
def dims_to_list(dims):
    out_list = []
    for i1 in range(dims[0]):
        for i2 in range(dims[1]):
            out_list.append([i1, i2])
    return out_list
def dim_finder(in_list):
    shape = int(math.ceil(math.sqrt(len(in_list))))
    return [shape, shape]
##class xy_plots:
##    def __init__(self):
##         self.fig = plt.figure()
def plot_xys(fills):
    fig = plt.figure()
    dims = dim_finder(xy_list)
    coord_list = dims_to_list(dims)
    i = 0
    print len(xy_list)
    print dims
    print coord_list
    #gs = matplotlib.gridspec.GridSpec(len(dims), len(dims))
    
    for xy in xy_list:
        print xy
        ys = a[:, int(xy[1]), int(xy[0])]
        xs = range(len(ys))

        plt.show
        #call = 'plt.subplot(gs' + str(coord_list[i]) + ')'
        #eval(call)
        #plt.subplot(gs[i])
        plt.subplot2grid(shape = (dims[0],dims[1]), loc = coord_list[i])
        #plt.subplots_adjust( hspace = 0.1,wspace = 0.05, top = 0.95, bottom = 0.01, left = 0.05, right = 0.99)
        plot_now = plt.plot(xs, ys, 'ro')
        #plt.show
        

        i += 1
    plt.show()
############################################################################################################
xy_list = []

ax = subplot(111)

#runax = axes([0.87, 0.025, 0.05, 0.029], axisbg='red')
#run = Button(runax, 'Run')
#run.on_clicked(plot_pts)

#cursor = Cursor(ax)
plt.title('Press enter to submit points')
#cursor = SnaptoCursor(ax, t, s)
connect('button_press_event', hello)
connect('key_press_event', plot_xys)
#connect('button_press_event', c2.hello)
#ax.plot(t, s, 'o')
a = numpy.random.rand(5,10,10)
#a = numpy.arange(500).reshape((5,10,10))
print a[0]
ax.imshow(a[0])
axis([0,9.5,0,9.5])
show()
