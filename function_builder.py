import os, sys, shutil
from Tkinter import *
import numpy
import scipy
from scipy import stats, ndimage, signal
from r_numpy_lib import *
from ScrolledText import ScrolledText
#image = numpy.arange(500).reshape((5, 10, 10))
def three_to_two(in_array):
    dimst = numpy.shape(in_array)
    return numpy.transpose(in_array).flatten().reshape((dimst[1] * dimst[2], dimst[0]))

def two_to_three(in_array, original_array):
    dimst = numpy.shape(original_array)
    print dimst
    print len(in_array[0])
    print len(in_array)
    dimsn = (dimst[2], dimst[1], len(in_array[0]))
    return numpy.transpose(in_array.flatten().reshape(dimsn))

def one_to_three(in_array, original_array, zd):
    dimst = numpy.shape(original_array)
    print dimst
    #print len(in_array[0])
    print len(in_array)
    dimsn = (dimst[2], dimst[1], zd)
    return numpy.transpose(in_array.reshape(dimsn))

#from matplotlib_widget_practice import *
def ext(type_list = [numpy.ndarray]):
    gs = globals()
    this = sys.modules[__name__]
    for g in gs:
        t = type(gs[g])
        
        if t in type_list:
            
            print 'Erasing',g
            exec('del g')
    sys.exit()
##            g = eval(g)
##            print g
##            del g
##            g = None
##            print g
##            
def undo():
    global funentry
    fun_list = eval(str(funentry.get()))
    try:
        funentry.destroy()
    except:
        x = 'oops'
        
    new_entry = str(fun_list[:-1])
    funentry = Entry(root, width = len(new_entry))
    funentry.grid(row = 2, column = 1, columnspan = 2,sticky = W)
    funentry.insert(0, new_entry)
    submit_function()
def make_fun():
    global funentry
    try:
        funentry.destroy()
    except:
        x = 'oops'
    funentry = Entry(root, width = 60)
    funentry.grid(row = 2, column = 1, columnspan = 2,sticky = W)
    
def build_function(x = 1):
    
    fun_list = None
    global fun_list
    et = funentry.get()
    try:
        fun_list = eval(str(funentry.get()))
    except:
        fun_list = []
    fun =  funs.get()
    ft = Funs[fun]

    
    fun_list.append(ft) 

    global funentry
    funentry.destroy()
    funentry = Entry(root, width = len(str(fun_list)))
    funentry.grid(row = 2, column = 1, columnspan = 2,sticky = W)
    funentry.insert(0, str(fun_list))
    submit_function()
def run():
    global interactive, update_button, command_hist, stext
    funs = fun_out.get()
    #try:
    
    x = eval(funs)
    stext.insert(END, funs + '\n\n')
    command_hist.append(funs)
##    except:
##        work_with = array_stack
##        print 'Transposing image for function', funs
##        
##        it = three_to_two(work_with)
##        funs = funs.replace('image', 'it')
##        try:
##            x = eval(funs)
##            x = two_to_three(x, array_stack)
##        except:
##            last = 0
##            index = 0
##            ot = []
##            print 'last try'
##            funs = funs.replace('it', 'line')
##            funs = funs
##            for line in it:
##                ot.append(stats.linregress(line, numpy.arange(len(line))))
##                last = status_bar(index, len(it), last = last)
##                index += 1
##            
##            x = two_to_three(numpy.array(ot), work_with)
##        global image
        
        
    #print image
    #print x

    update_button = Button(root, text = 'Update', command = run_update)
    update_button.grid(row = 8, column = 2, sticky = E)
    #Run = Button(root, text = 'Run', command = run)
    #Run.grid(row = 7, column = 2, sticky = E)
    from time_series_vis import interactive_chips
    interactive = interactive_chips( template_image = i, title = funs)
    interactive.Display_chips(x, info = info, img_name = img_name)
    #global interactive
    print interactive
def run_update():
    global stext, command_hist
    funs = fun_out.get()
    x = eval(funs)
    print image
    print x
    #from matplotlib_widget_practice import interactive_chips
    stext.insert(END, funs + '\n\n')
    command_hist.append(funs)
    interactive.update_chips(x, funs)# = interactive_chips(x, template_image = i, title = funs)
    
def build_base(fun):
    fun_list = fun[0] + '(image'
    if str(fun[1]) != 'None':
        
        f = fun[1]
        for arg in f:
            fun_list += ', ' + arg
        #fun_list += ')'
    fun_list += ')'
    return fun_list

def add_to_base(fun_list, fun):
    fun_list = fun[0] + '(' + fun_list

    if str(fun[1]) != 'None':
        f = fun[1]
        for arg in f:
            fun_list += ', ' + arg
    fun_list += ')'
    return fun_list
def submit_function():
    global fun_out
    #et = funentry.get()
    try:
        fun_list = eval(str(funentry.get()))
        fun_t = fun_list
        fun_list = ''#build_base(fun_t)
        flo = ''
        fi = 0
        for fun in fun_t:
            if fun_list == '':
                fun_list = build_base(fun)
            elif fun not in ['+', '-', '/', '*']:
                fun_list = add_to_base(fun_list, fun)

            else:
                fun_list += fun
                
                flo += fun_list
                fun_list = ''
            fi += 1
        #fun_list += ')' * len(fun_t)
        if flo != '':
            flo += fun_list
            fun_list = flo
    except:
        fun_list = 'image           '
    
    lfun_out = Label(root, text = 'Function')
    lfun_out.grid(row = 5, column = 1, sticky = W, padx = 3)
    try:
        fun_out.destroy()
    except:
        x = ''
    fun_out = Entry(root, width = len(str(fun_list)))
    fun_out.insert(0, str(fun_list))
    fun_out.grid(row = 6, column = 1, columnspan = 2,sticky = W)

    Run = Button(root, text = 'Run', command = run)
    Run.grid(row = 7, column = 2, sticky = E)
root = Tk()
root.title('Time-series Analysis Tool (tSAT)')
root.geometry("+0+0")
#root.configure(background = 'white')

Funs = {'Fit- Fast Fourier Transform' : ['numpy.fft.fft', ['axis = 0']], 'Fit- Hermitian Fast Fourier Transform' : ['numpy.fft.hfft', ['axis = 0']],'Fit- Inverse Fast Fourier Transform' : ['numpy.fft.ifft', ['axis = 0']],
        'Fit- Zscore':['stats.zscore',['axis = 0']],
        'Summarize- Variation':['stats.variation',['axis = 0']], 'Summarize- Signal to Noise':['stats.signaltonoise',['axis = 0']],'Summarize- Skewness':['stats.skew',['axis = 0']], 'Summarize- Kurtosis':['stats.kurtosis',['axis = 0']],
        'Fit- Laplace':['ndimage.laplace',None],'Fit- Gaussian Laplace':['ndimage.gaussian_laplace',['sigma = 1']],'Fit- Gaussian Gradient Magnitude':['ndimage.gaussian_gradient_magnitude',['sigma = 1']],
        'Filter- Gaussian Filter 1d':['ndimage.gaussian_filter1d',['sigma = .2', 'axis = 0', 'order = 3']],'Fit- Correlate 1d':['ndimage.correlate1d',['weights = [1] * len(image)', 'axis = 0']],
        'Summarize- Sum' : ['numpy.sum', ['axis = 0']], 'Summarize- Mean' : ['numpy.mean', ['axis = 0']],'Fit- Difference' : ['numpy.diff', ['axis = 0']], 'Summarize- Decimate' : ['signal.decimate', ['axis = 0', 'q = len(image)']],
        'Filter- Convolve Filter 1d':['ndimage.convolve1d',['weights = [1] * len(image)', 'axis = 0']], 'Filter- Spline Filter 1d' : ['ndimage.spline_filter1d', ['order = 3', 'axis = 0']],
        'Summarize- Stack Minimum' : ['numpy.amin', ['axis = 0']],'Summarize- Stack Maximum' : ['numpy.amax', ['axis = 0']], 'Sumamrize- Value Range' : ['numpy.ptp', ['axis = 0']], 'Sumarize- Standard Deviation' :['numpy.std', ['axis = 0']],
        'A- Input Image' : ['', None], 'Filter- Gaussian Filter' : ['ndimage.filters.gaussian_filter', ['sigma = 1', 'order = 0']], 'Filter- Uniform Filter' : ['ndimage.filters.uniform_filter1d', ['size = 3', 'axis = 0']],
        'Filter- Minimum Filter' : ['ndimage.minimum_filter1d', ['size = 3', 'axis = 0']], 'Filter- Maximum Filter' : ['ndimage.maximum_filter1d', ['size = 3', 'axis = 0']],
        'Filter- Generic Filter': ['ndimage.generic_filter1d', ['function = mean', 'filter_size = 3', 'axis = 0']]}#, 'Summarize- Linear Regression' :['stats.linregress', None]}
        
#ndimage.filters.uniform_filter : ['size = 3']
F = list(Funs)
F.sort()


#b = Button(root, text = 'Select Input Image', height = 1, width = len('Select Input Image'), command = select_i_image)
#b.grid(row = 0, column = 1, sticky = E, padx = 3)
#i = Entry(root, width = 60)
#i.grid(row = -1, column = 2, columnspan = 2,sticky = W)

def read_image():
    global image, array_stack, i, info
    i = i_name.get()
    if os.path.exists(i) == True:
        info = raster_info(i)
        image = brick(i, 'Float32')
    else:
        warning = showwarning('Image does not exist', i + ' does not exist!!\nPlease select existing image')
def select_image():
    global i_name, img_name, idir
    idir = ''
    it = os.path.dirname(i_name.get())
    io = i_name.get()
    #print it
    if it != '' and os.path.isdir(it):
        idir = it
        
    image = str(askopenfilename(title = 'Select Stack Raster', initialdir = idir,filetypes=[("IMAGINE","*.img"),("tif","*.tif"), ("All Files", "*")]))
    img_name = image
    if image == '':
        image = io
   
    try:
        i_name.destroy()
    except:
        x = 'oops'
    i_name = Entry(root, width = len(image) + 3)
    i_name.grid(row = 0, column = 1, sticky = W)
    i_name.insert(0,image)

    try:
        ri.destroy()
    except:
        x = 'oops'
    ri = Button(root, text = 'Update Image', command = read_image)
    ri.grid(row = 0, column = 2)
    read_image()
    
select_i_image = Button(root, text = 'Select Image', command = select_image)
select_i_image.grid(row = 0, column = 0, sticky = E)
iit = '                   '
i_name = Entry(root, width = len(iit))
i_name.grid(row = 0, column = 1, sticky = W)
i_name.insert(0,iit)
lfuns = Label(root, text = 'Functions')
lfuns.grid(row = 1, column = 0, sticky = W)
funs = StringVar(root)
fmenu = OptionMenu(root, funs, *F, command = build_function)
fmenu.pack_configure
fmenu.grid(row = 2, column = 0, sticky = W)

##build = Button(root, text = "Build Function", command = build_function)
##build.grid(row = 2, column = 0, sticky = W)
##

submit = Button(root, text = "Submit Function", command = submit_function)
submit.grid(row = 3, column = 0, sticky = W)
clear = Button(root, text = "Clear Functions", command = make_fun)
clear.grid(row = 3, column = 1, sticky = E)
Undo = Button(root, text = "Undo", command = undo)
Undo.grid(row = 3, column = 2, sticky = E)
Exit = Button(root, text = "Exit", command = ext)
Exit.grid(row = 4, column = 2, sticky = E)
lfunentry = Label(root, text = 'Function Entry')
lfunentry.grid(row = 1, column = 1, sticky = E, padx = 3)
make_fun()

def add_command(op):
    fun_list = None
    global fun_list
    et = funentry.get()
    try:
        fun_list = eval(str(funentry.get()))
    except:
        fun_list = []
    fun_list.append(op) 

    global funentry
    funentry.destroy()
    funentry = Entry(root, width = len(str(fun_list)))
    funentry.grid(row = 2, column = 1, columnspan = 2,sticky = W)
    funentry.insert(0, str(fun_list))
    submit_function()

plusb = Button(root, text = '+', command = lambda: add_command('+'))
plusb.grid(row = 2, column = 3)
plusb = Button(root, text = '-', command = lambda: add_command('-'))
plusb.grid(row = 2, column = 4)
plusb = Button(root, text = '*', command = lambda: add_command('*'))
plusb.grid(row = 2, column = 5)
plusb = Button(root, text = '/', command = lambda: add_command('/'))
plusb.grid(row = 2, column = 6)
    
##history = Entry(root, width = 30)
##history.grid(row = 1, column = 7)
##history.insert(0, 't\nt\nt')

command_hist = ['image']
stextl = Label(root, text = 'Function History')
stextl.grid(row = 0, column = 7)
stext = ScrolledText(root, bg = 'white', height = 7, width = 40)
stext.insert(END, 'image\n\n')
stext.grid(row = 1, column = 7, rowspan = 7)

def save_hist():
    output_name =  str(asksaveasfilename(title = 'Select output history name', initialdir = idir, filetypes=[("Text","*.txt")]))
    if os.path.splitext(output_name)[1] == '':
        output_name += '.txt'
    out_lines = 'Commands saved on: '+now()+'\n'
    for line in command_hist:
        out_lines += line + '\n'
    out_lines = out_lines[:-1]

    print 'Writing history to:', os.path.basename(output_name)
    oo = open(output_name, 'w')
    oo.writelines(out_lines)
    oo.close()
save_history = Button(root, text = 'Save History', command = save_hist)
save_history.grid(row = 8, column = 7, sticky = W)
#stext
#colors.set('RdYlBu_r')
#color_list = get_color_list()
#cmenu = OptionMenu(root, colors, *color_list)
#cmenu.grid(row = 2, column = 5, sticky = W)
#i = 'R:/NAFD/Landtrendr/tSAT/zambia_inputs/nbr_stack_select.img'
#i = 'C:/Users/ihousman/Documents/Zambia/Analysis/Imagery/L5169069_06920090604_j.jpg'
#image = brick(vis_i, dt = 'Float32')
#brick(i, dt = 'Float32')
#image = numpy.arange(1000).reshape((10,10,10))
#array_stack = image
#image = array_stack
#image = tSAT_gui.image

root.mainloop()
fun_list = None
