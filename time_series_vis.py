from pylab import *
from matplotlib.widgets import Slider, Button, RadioButtons, SpanSelector
#from mpl_toolkits.basemap import Basemap
#import matplotlib.patches as patches
from r_numpy_lib import *
from scipy import ndimage, stats
from matplotlib_lib import *
#ax = subplot(111)
#subplots_adjust(left=0.25, bottom=0.25)
#t = arange(0.0, 1.0, 0.001)

ignore_value = 0
#s = a0*sin(2*pi*f0*t)

#display_chips(image)
def tellme(s):
    print s
    plt.title(s,fontsize=16)
    plt.draw()

def dims_to_list(dims):
    out_list = []
    for i1 in range(int(dims[0])):
        for i2 in range(int(dims[1])):
            out_list.append([i1, i2])
    return out_list
def dim_finder(in_list):
    shape = int(math.ceil(math.sqrt(len(in_list))))
    return [shape, shape]

class interactive_chips:
    def __init__(self, default_stretch = 2.0, template_image = '', title = ''):
        self.title = title
        self.template_image = template_image
        self.kernel0 = 0
        self.sd0 = default_stretch
        self.fig = plt.figure()
        self.plot_list = []
        self.pt_list = []
        self.an_list = []
        self.ptn = 0
        self.xy_list = []
        self.bp_id = ''
        self.kp_id = ''
        self.color = 'hot'
        self.shp = ''
    def Display_chips(self, array_stack, info = '', img_name = ''):

        if info != '':
            self.info = info
            self.spat_coords = info['coords']
            self.res = info['res']
        else:
            self.spat_coords = ''
            self.res = ''

        if img_name != '':
            self.img_name = img_name
        else:
            self.img_name = ''
            
        self.array_stack = array_stack
        array_stack = None
        if numpy.ndim(self.array_stack) == 2:
            self.array_stack = [self.array_stack]
        
        
        plt.suptitle(self.title)
        self.dims = int(math.ceil(sqrt(len(self.array_stack))))
        self.coords = []
        for i1 in range(int(self.dims)):
            for i2 in range(int(self.dims)):
                self.coords.append([i1, i2])
        #print 'coords', self.coords
        
        i = 0
        self.i_list = []
        self.i2_list = []
        self.std_list = []
        self.mean_list = []
        
        #self.xy_list = []
        #self.pt_no = 1
        for array in self.array_stack:
            
            #print array
            name2 = "self.l22" + str(i) 
            exec(name2 + " = plt.subplot2grid(shape = (int(self.dims),int(self.dims)), loc = self.coords[i])")
            #plt.subplot2grid(shape = (int(self.dims),int(self.dims)), loc = self.coords[i])
            mean = float(numpy.mean(array[array!= ignore_value]))
            std = float(numpy.std(array[array!= ignore_value]))
            self.std_list.append(std)
            self.mean_list.append(mean)
            Min = float(mean) - float((std * self.sd0))
            Max = float(mean) + float((std * self.sd0))
            name = "self.l" + str(i)
            plt.show
            exec(name + " =imshow(array, cmap = get_cmap(self.color), picker = True)")
            exec(name + '.set_clim((Min, Max))')
            plt.text(-0.2, -0.2, i + 1)
            plt.axis('off')
            plt.subplots_adjust( hspace = 0.1,wspace = 0.005, top = 0.95, bottom = 0.01, left = 0.05, right = 0.99)
            self.i_list.append(name)
            self.i2_list.append(name2)
            #connect('button_press_event', self.submit_pts)
            #connect('key_press_event', self.plot_xys)
            i += 1

        axcolor = 'red'
        axsd = axes([0.24, 0.01, 0.3, 0.02], axisbg=axcolor)
        axkernel  = axes([0.24, 0.032, 0.3, 0.02], axisbg=axcolor)

        self.ssd = Slider(axsd, 'SD', 0.1, 5.0, valinit=self.sd0)
        self.skernel = Slider(axkernel, 'Kernel', 0, 10, valinit=self.kernel0)
        self.ssd.on_changed(self.update_sd)
        self.skernel.on_changed(self.update_kernel)
        self.ssd.poly

        self.rax = axes([0.01, 0.01, 0.15, 0.10], axisbg=axcolor)
        self.colors = RadioButtons(self.rax, ('autumn', 'bone', 'hot', 'RdYIBu_r'), active=2)
        self.colors.on_clicked(self.colorfunc)

        #self.fax = axes([0.65, 0.025, 0.75, 0.08], axisbg=axcolor)
        #self.functs = RadioButtons(fax, ('nd_image.gaussian_filter1d', 'lin.regress'), active=0)
        #functs_dict = {'nd_image.gaussian_filter1d':['sigma = .2', 'axis = 1', 'order = 3']}


        
        
        self.exax =  axes([0.93, 0.015, 0.04, 0.029], axisbg=axcolor)
        self.ex = Button(self.exax, 'Exit')
        self.ex.on_clicked(self.exit_func)

        self.saveax = axes([0.93, 0.045, 0.05, 0.029], axisbg=axcolor)
        self.save = Button(self.saveax, 'Save')
        self.save.on_clicked(self.save_func)

        self.savexysax = axes([0.85, 0.015, 0.07, 0.029], axisbg=axcolor)
        self.savexys = Button(self.savexysax, 'Save Pts')
        self.savexys.on_clicked(self.save_xys)

        self.selectshpax = axes([0.85, 0.045, 0.07, 0.029], axisbg=axcolor)
        self.selectshp = Button(self.selectshpax, 'Load Shp')
        self.selectshp.on_clicked(self.select_shp)

        
        self.pixelclrax = axes([0.60, 0.047, 0.12, 0.029], axisbg=axcolor)
        self.pixelclr = Button(self.pixelclrax, 'Clr/Strt Pts')
        self.pixelclr.on_clicked(self.select_pts)


        self.pixelonax = axes([0.60, 0.015, 0.07, 0.029], axisbg=axcolor)
        self.pixelon = Button(self.pixelonax, 'On Pts')
        self.pixelon.on_clicked(self.connect)
        
        self.pixeloffax = axes([0.67, 0.015, 0.07, 0.029], axisbg=axcolor)
        self.pixeloff = Button(self.pixeloffax, 'Off Pts')
        self.pixeloff.on_clicked(self.disconnect)

        self.pixeldrawptsax = axes([0.75, 0.015, 0.07, 0.029], axisbg=axcolor)
        self.pixeldrawpts = Button(self.pixeldrawptsax, 'Plot Pts')
        self.pixeldrawpts.on_clicked(self.plot_xys)
        
##        
        show()
    def disconnect(self, fill = ''):
        if self.kp_id != '':
            print 'Disconnecting key_press_event'
            disconnect(self.kp_id)
        if self.bp_id != '':
            print 'Disconnecting button_press_event'
            disconnect(self.bp_id)

    def connect(self, fill = ''):
        self.disconnect()
        print 'Connecting button_press_event'
        self.bp_id = connect('button_press_event', self.submit_pts)
        #print 'Connecting key_press_event'
        #self.kp_id = connect('key_press_event', self.plot_xys)
    def clear(self):
        self.xy_list = []
    def save_plots(self, x):
        idir = ''
        if self.img_name != '':
            idir = os.path.dirname(self.img_name)
        elif self.shp != '':
            idir = os.path.dirname(self.shp)
       
        output_name =  str(asksaveasfilename(title = 'Select output image name', initialdir = idir, filetypes=[("CSV","*.csv"),("TAB","*.txt")]))
        if os.path.splitext(output_name)[1] == '':
            output_name += '.csv'
        sep_dict = {'.csv' : ',', '.txt': '\t'}
        sep = sep_dict[os.path.splitext(output_name)[1]]
        fid = 0
        out_lines = 'FID' + sep + 'x' + sep + 'y' + sep + sep+ 'Values\n'
        for coords, ys in self.out_plot_list:
            out_lines += str(fid) + sep + str(coords[0]) + sep + str(coords[1]) 
            for y in ys:
                out_lines+= sep + str(y)
            out_lines+= '\n'
            fid += 1
        print 'Writing:', os.path.basename(output_name)
        oo = open(output_name, 'w')
        oo.writelines(out_lines)
        oo.close()
        print 'Finished writing:', os.path.basename(output_name)
    def plot_xys(self, fills = '', title = ''):
        lp1 = dict(linewidth=1, color='blue', linestyle='-')
        lp2 = dict(linewidth=1, color='red', linestyle='o')
        fig = plt.figure()
        plt.suptitle(title)
        dims = dim_finder(self.xy_list)
        coord_list = dims_to_list(dims)
        i = 0
        
        #gs = matplotlib.gridspec.GridSpec(len(dims), len(dims))
        self.plot_list = []
        self.out_plot_list = []
        pi = 0
        for xy in self.xy_list:
            if None not in xy:
                #try:
                nt = 'self.plotl' + str(pi)
                nt2 = 'self.plotm' + str(pi)
                
                ys = self.array_stack[:, int(xy[1]), int(xy[0])]
                xs = range(len(ys))
                
                plt.show
                #call = 'plt.subplot(gs' + str(coord_list[i]) + ')'
                #eval(call)
                #plt.subplot(gs[i])
                exec(nt2 + " = plt.subplot2grid(shape = (dims[0],dims[1]), loc = coord_list[i])")
                #plt.text(-0.02, -0.02, i + 1)
                #plt.subplots_adjust( hspace = 0.1,wspace = 0.05, top = 0.95, bottom = 0.01, left = 0.05, right = 0.99)
                exec(nt + " = plt.plot(xs, ys, linestyle = '-', color = 'r', marker = 'o')")
                #exec("axs = "+nt+".axes()")
               
                exec(nt2 + ".text(min(xs), max(ys), i + 1)")
                #exec(nt2 + " = plt.plot(xs, ys, 'o', color = 'red')")
                real_xys = array_coord_to_proj_coord(xy, self.spat_coords, self.res)
                
                #self.plot_list.append([real_xys, list(nt)])
                self.out_plot_list.append([real_xys, list(ys)])
                #plt.show
                pi += 1
                #except:
                    #print 'Could not plot', xy
                
        
                i += 1
        
        self.saveplotsax = axes([0.85, 0.02, 0.12, 0.029], axisbg='red')
        self.saveplots = Button(self.saveplotsax, 'Save Plots')
        self.saveplots.on_clicked(self.save_plots)
        plt.show()
    def submit_pts(self, event, xyt = []):
        if xyt != []:
            xy = xyt
            x = xy[0]
            y = xy[1]
        else:
            x = event.xdata
            y = event.ydata
            xy = [x,y]
      
        if None not in xy and x >= 1 and y >= 1:
            self.xy_list.append(xy)
            
            try:
                self.ax.plot(event.xdata, event.ydata, 'ro')
                #plt.annotate(str(self.pt_no), xy = (x,y), textcoords = 'offset points')
                #plt.annotate(str(self.pt_no), xy = (x,y), xytext = (x, y))
                self.ax.imshow(self.a)
                plt.annotate('hello', xy = (x,y))
            except:
                #try:
                #plt.plot(event.xdata, event.ydata, 'ro')
                it = 0
                for i in self.i2_list:
                    ptn = 'self.pt_' + str(self.pt_no) + '_' + str(it)
                    ann = 'self.an_' + str(self.pt_no) + '_' + str(it)
                   
                    exec(ptn + ' = ' + i + ".plot(x, y, 'ro')")
                    exec(ann + ' = ' + i + ".annotate(str(self.pt_no), xy = (x,y))")
                    #self.update_chips(self.array_stack)
                    #exec(i + ".imshow(self.array_stack[it])")
                    plt.subplots_adjust( hspace = 0.1,wspace = 0.005, top = 0.95, bottom = 0.01, left = 0.05, right = 0.99)
                    self.pt_list.append(ptn)
                    self.an_list.append(ann)
                    it += 1
                #except:
                    #print 'Cannot plot pt', xy
            self.pt_no += 1
            
            #print 'Pt coords are:', self.xy_list
            draw()
            
    def select_pts(self, array_stack = '', band = 0, pt_no = 1):
        
        self.pt_no = pt_no
        
        self.xy_list = []
        self.plot_list = []
        
        if array_stack != '':
            try:
                list(array_stack)
                self.array_stack = array_stack
                self.ax = subplot(111)
                self.a = numpy.sum(numpy.diff(self.array_stack, axis = 0), axis = 0)#self.array_stack[band]
                self.ax.imshow(self.a)
                plt.title('Press enter to submit points')
                self.exax =  axes([0.93, 0.025, 0.04, 0.029], axisbg='red')
                self.ex = Button(self.exax, 'Exit')
                self.ex.on_clicked(self.exit_func)
               
                connect('button_press_event', self.submit_pts)
                connect('key_press_event', self.plot_xys)
                plt.show()
        
                array_stack = None
            except:
                print 'oops'
                
                self.connect()
                
            if len(self.pt_list) > 0:
                for pt in self.pt_list:
                    ptt = pt + '[0]'
                    exec(ptt + '.remove()')
                    exec('del ' + ptt)
                    exec('del ' + pt)
                rt = range(len(self.an_list))
                no = len(self.an_list)/len(self.i2_list)
                rt2 = range(len(self.i2_list)) * no
                
                for i in rt:
                    
                    an = self.an_list[i]
                    axt = self.i2_list[rt2[i]]
                    exec(axt + '.texts.remove(' + an + ')')
##                for an in self.an_list:
##                    
##                    #x = eval(an)
##                    #x.remove()
##                    #del x
##                    #print x
##                    ann = an + '[0]'
##                    #exec(ann + '.remove()')
##                    #exec('del ' + ann)
##                    exec('del ' + an)
            self.pt_list = []
            self.an_list = []  
                #for i2 in self.i2_list:
                #self.l20.canvas.mpl_connect('button_press_event', self.submit_pts)
                #self.l20.connect('button_press_event', self.submit_pts)
                #plt.figure()
##                ct = self.coords[-1]
##                #ct = [0, ct[1] + 1]
##                print ct
##                self.ax = plt.subplot2grid(shape = (int(self.dims), int(self.dims)), loc = ct)
##                self.a = self.array_stack[-1]
##                self.ax.imshow(self.a)        
        #axis([0, len(self.a[1,:])-0.5 , 0, len(self.a[:,1])-0.5])
        #plt.subplots_adjust( hspace = 0.1,wspace = 0.00, top = 0.95, bottom = 0.01, left = 0.05, right = 0.99)
        
        
        #connect('key_press_event', plot_pts)
##    def get_points(self, x):
##        print self, x
##        #plt.axis([0.,1.,0.,1.])
##        #plt.setp(plt.gca(),autoscale_on=False)
##        happy = False
##        while not happy:
##            tellme('Hit the Enter key when finished slecting points')
##            pts = numpy.asarray(plt.ginput(500, timeout = -1))
##            #for i in self.i_list:
##                #exec(i + ".plot(pts[:,0], pts[:,1], 'ro')")
##            ph = plt.plot(pts[:,0], pts[:,1], 'ro')
##            print pts
##            tellme('Hit the Enter key to accept these points\nMouse button to reject')
##            happy = plt.waitforbuttonpress()
##            if not happy:
##                for p in ph: p.remove()
##            else:
##                print pts
##                return pts
##        
    def update_sd(self,  sd):

        
  
        
##        kernel = self.skernel.val
##        sd = self.ssd.val
##        
##        #l.set_data(array)
##        #l.set_filterrad(freq)
##        #l.set_filternorm(freq)
##        #,  vmin = mean - (std * freq))
##        #l.check_update(array)
##        #l = imshow(array, vmin = mean - (std * freq))
##        #axes([0, numpy.shape(array)[1], numpy.shape(array)[0], 0])
##        
        for i in self.i_list:
            std = self.std_list[int(i[6:])]
            mean = self.mean_list[int(i[6:])]
            Min = mean - (std * sd)
            Max = mean + (std * sd)
          
##            
##            exec(i + '.set_data(ndimage.gaussian_filter(array_stack['+i[1:]+'], kernel))')
            exec(i + '.set_clim((Min, Max))')
            draw()
    def update_kernel(self,  kernel):
        for i in self.i_list:
            exec(i + '.set_data(ndimage.gaussian_filter(self.array_stack['+i[6:]+'], kernel))')
            #exec(i + '.set_clim((Min, Max))')
            draw()
    def update_chips(self, new_stack, title = ''):
        self.array_stack = new_stack
        #plt.suptitle(None)
        #plt.suptitle(title)
        self.std_list = []
        self.mean_list = []
        if numpy.ndim(new_stack) == 2:
            new_stack =[new_stack]
        
        for i in self.i_list[:len(self.array_stack)]:
            array = new_stack[+int(i[6:])]
            mean = float(numpy.mean(array[array!= ignore_value]))
            std = float(numpy.std(array[array!= ignore_value]))
            self.std_list.append(std)
            self.mean_list.append(mean)
            Min = float(mean) - float((std * self.sd0))
            Max = float(mean) + float((std * self.sd0))
            exec(i + '.set_data(new_stack['+i[6:]+'])')
            exec(i + '.set_clim((Min, Max))')
            draw()
        if self.xy_list != []:
            self.plot_xys(title = title)
        #Display_chips(self)
    def colorfunc(self, label):
        #l.set_color(label)
        self.color = label
        for i in self.i_list:
            exec(i + '.set_cmap(get_cmap(self.color))')
            draw()
    def select_shp(self, x):
        idir = ''
        if self.shp != '':
            idir = os.path.dirname(self.shp)
        elif self.img_name != '':
            idir = os.path.dirname(self.img_name)
            
        self.shp = str(askopenfilename(title = 'Select Point Shapefile',initialdir = idir, filetypes=[("Shapefile","*.shp")]))
        xys = xy_coords(self.shp, False)
        print 'There are', len(xys), 'points to plot'
        if len(xys) > 16:
            print 'There are more than 16 points in shapefile'
            print 'Randomly selecting 16 points from the shapefile'
            import random
            smp = random.sample(range(len(xys)), 16)
            xys = numpy.array(xys)[smp]
        if self.xy_list == []:
            self.select_pts()

        if self.spat_coords != '' and self.res != '':
            for xy in xys:
                if inside(xy, self.spat_coords):
                    xyt = proj_coord_to_array_coord(xy, self.spat_coords, self.res)
                    self.submit_pts(event = '',xyt = xyt)
                else:
                    print 'Point', xy, 'falls outside of raster'

    def save_xys(self, x):
        idir = ''
        if self.shp != '':
            idir = os.path.dirname(self.shp)
        elif self.img_name != '':
            idir = os.path.dirname(self.img_name)

        output_name =  str(asksaveasfilename(title = 'Select output shapefile name', initialdir = idir, filetypes=[("Shapefile","*.shp"),("CSV","*.csv"), ("KML","*.kml")]))
        if os.path.splitext(output_name)[1] == '':
            output_name += '.shp'
        xyo = []
        for xy in self.xy_list:
            xyo.append(array_coord_to_proj_coord(xy, self.spat_coords, self.res))

        if os.path.splitext(output_name)[1] == '.shp':
            list_to_point_shapefile(xyo, self.img_name, output_name)

        elif os.path.splitext(output_name)[1] == '.csv':
            write_xy_csv(xyo, output_name)
        elif os.path.splitext(output_name)[1] == '.kml' :
            zone =  int(self.info['zone'])
            if zone in range(100):
                xy_list_to_kml(xyo, output_name, self.info['zone'])
            else:
                warning = showwarning('Cannot find zone', 'Please ensure the raster is in UTM to export KMLs')
    def save_func(self, x):
        idir = ''
        if self.img_name != '':
            idir = os.path.dirname(self.img_name)
        elif self.shp != '':
            idir = os.path.dirname(self.shp)
       
         
        print 'yay'
        #initialdir = idir
        output_name =  str(asksaveasfilename(title = 'Select output image name', initialdir = idir, filetypes=[("IMAGINE","*.img"),("tif","*.tif")]))
        if os.path.splitext(output_name)[1] == '':
            output_name += '.img'
        try:
            
            Format = format_dict[os.path.splitext(output_name)[1]]
        except:
            warning = showwarning('Unsupported Format', 'Supported formats are:\n ' + str(list(format_dict)))
        stack(self.array_stack, output_name, self.template_image, dt = 'Float32',df = Format, array_list = True)
        

    def exit_func(self, x):
        self.array_list = None
        self.array_stack = None
        self.array = None
        self.a = None
        sys.exit()
    

    #l.update(vmin = mean - (std * freq))
    #l.set_ydata(amp*sin(2*pi*freq*t))


##ax =  axes([0.8, 0.125, 0.1, 0.04])
##def onselect(eclick, erelease):
##  'eclick and erelease are matplotlib events at press and release'
##  print ' startposition : (%f, %f)' % (eclick.xdata, eclick.ydata)
##  print ' endposition   : (%f, %f)' % (erelease.xdata, erelease.ydata)
##  print ' used button   : ', eclick.button
##
##def toggle_selector(event):
##    print ' Key pressed.'
##    if event.key in ['Q', 'q'] and toggle_selector.RS.active:
##        print ' RectangleSelector deactivated.'
##        toggle_selector.RS.set_active(False)
##    if event.key in ['A', 'a'] and not toggle_selector.RS.active:
##        print ' RectangleSelector activated.'
##        toggle_selector.RS.set_active(True)
###span = RectangleSelector(ax, onselect, drawtype = 'line')
##toggle_selector.RS = RectangleSelector(ax, onselect, drawtype='line')
##connect('key_press_event', toggle_selector)
##resetax = axes([0.8, 0.025, 0.1, 0.04])
##button = Button(resetax, 'Reset', color=axcolor, hovercolor='0.975')
##def reset(event):
##    sfreq.reset()
##    samp.reset()
##    #l.remove()
##button.on_clicked(reset)

#saveax = axes([0.8, 0.025, 0.02, 0.04])
#button = Button(saveax,'Save', color = axcolor, hovercolor = '0.995')
#button.on_clicked(stack(array, 'test.img', image, array_list = True))
#image = 'R:/NAFD/Landtrendr/tSAT/test_inputs/Baltimore_MODIS_day.img'
#image = brick(image)
#interactive = interactive_chips(array_stack)
#img_in = 'R:/NAFD/Landtrendr/tSAT/test_inputs/ud_stack_clip.tif'
#image = brick(img_in, dt = 'Float32')
#info = raster_info(img_in)
#image = numpy.random.rand(5,10,10)
#i = interactive_chips(title = 'test')
#i.Display_chips(image, info = info, img_name = img_in)
#i.select_pts(image)
#print 'updating'
#i.update_chips(image * 2)
array = None

array_list = None
