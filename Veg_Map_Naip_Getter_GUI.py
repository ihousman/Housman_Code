from Veg_Map_Naip_Getter import *
from Tkinter import *
################################################################################################
#Functions that individual buttons call

#Select input shapefile function
def select_i_shp(provided_input = ''):
    #Tries to set the initial dir to the current input directory or output directory
    idir = os.path.dirname(i.get())
    if len(idir) == 0:
        idir = os.path.dirname(o.get())
    if len(idir) == 0:
        idir = cwd
    if provided_input == '':
        shp = str(askopenfilename(title = 'Select Study Area Shapefile', initialdir = idir,filetypes=[("Shapefile","*.shp")]))
    else:
        shp = provided_input
    if shp != '':
        global i
        i.destroy()
        i = Entry(root, width = len(shp))
        i.grid(row = 0, column = 2, columnspan = 2, sticky = W)
        i.insert(0, shp)

#Select output image name
def select_o_image():
    idir = os.path.dirname(o.get())
    if len(idir) == 0:
        idir = os.path.dirname(i.get())
    if len(idir) == 0:
        idir = cwd
    image =  str(asksaveasfilename(title = 'Select output image name',initialdir = idir, filetypes=[("IMAGINE","*.img"),("tif","*.tif")]))
    if image != '':
        if os.path.splitext(image)[1] == '':
            image += '.img'
    global o
    o.destroy()
    o = Entry(root, width = len(image))
    o.insert(0, image)
    o.grid(row = 1, column = 2, columnspan = 2, sticky = W)


#Select an image server dir
def select_is_dir():
    idir = os.path.dirname(is_dir.get())
    if idir == '':
        idir = cwd
    dirname = askdirectory(initialdir = idir, title = 'Select Image Directory')
    global is_dir
    is_dir.destroy()
    is_dir = Entry(root, width = len(dirname))
    is_dir.insert(0, dirname)
    is_dir.grid(row = 2, column = 2, columnspan = 2, sticky = W)

#If imagery in directory does not have a standard NAIP naming convention,
#use this function to set it up for image selection and select the image it intersects
def setup_pseudo_is():
    global p, quads
    shp = i.get()
    is_dirname = is_dir.get()
    if is_dirname[-1] != '/':
        is_dirname += '/'
    if shp == '':
        warning = showwarning('No Study Area Defined', 'Please select study area shapefile')
    else:
        p = pseudo_image_server(is_dirname)
        quads = p.get_images(shp)
    print
    print 'There are', len(quads), 'images to download'

#If the directory is a standard NAIP directory but no part of the nationwide select,
#this will select the images that are intersected
def custom_naip_download():
    global quads
    shp = i.get()
    is_dirname = is_dir.get()
    if is_dirname[-1] != '/':
        is_dirname += '/'
    if shp == '':
        warning = showwarning('No Study Area Defined', 'Please select study area shapefile')
    else:
        quads = quad_downloader(shp, temp_dir, state_list = [], mosaic_only = False, download_images = False, dir_list = [is_dirname])[0]
    print
    print 'There are', len(quads), 'images to download'

#This will allow for standard US select to be downloaded (not always the most up-to-date)
def standard_naip_download():
    global quads
    shp = i.get()
    if shp == '':
        warning = showwarning('No Study Area Defined', 'Please select study area shapefile')
    else:
        quads = quad_downloader(shp, temp_dir, state_list = [], mosaic_only = False, download_images = False)[0]
    print
    print 'There are', len(quads), 'images to download'
def degrade_only():
    try:
        shp = i.get()
        res = s.get()
        print res
        l = large_mosaic(quads, study_area = shp)
        l.degrade_images(res = res)
    except:
        warning = showwarning('No images found', 'Please run any setup option first')

def degrade_and_mosaic():
    try:
        shp = i.get()
        res = s.get()
        rs_val = rs.get()
        dt_val = dt.get()
        iof_val = iof.get()
        chunk_or_not = eval(v.get())
        run_or_not = eval(r.get())
        if dt_val == 'Same_As_Input':
            dt_val = ''
        
            
        print res
        l = large_mosaic(quads, study_area = shp)
        l.degrade_images(res = res)
        
        out = o.get()
        if out != '':
            
            l.mosaic_list(output = out, resampling_method = rs_val, integer_or_float = iof_val, datatype = dt_val, chunk = chunk_or_not, run = run_or_not)
        else:
            warning = showwarning('No Output Defined', 'Please define an output name')
    except:
        warning = showwarning('No images found', 'Please run any setup option first')

def mosaic_only():
    try:
        shp = i.get()
        res = s.get()
        rs_val = rs.get()
        dt_val = dt.get()
        iof_val = iof.get()
        chunk_or_not = eval(v.get())
        run_or_not = eval(r.get())
        if dt_val == 'Same_As_Input':
            dt_val = ''
        
            
        print res
        l = large_mosaic(quads, study_area = shp)
##        #l.degrade_images(res = res)
##        
        out = o.get()
        if out != '':
            
            l.mosaic_list(output = out, resampling_method = rs_val, integer_or_float = iof_val, datatype = dt_val, chunk = chunk_or_not, run = run_or_not)
        else:
            warning = showwarning('No Output Defined', 'Please define an output name')
    except:
        warning = showwarning('No images found', 'Please run any setup option first')
    
################################################################################################
#fun_help()
popup = 't_root'
root = Tk()
root.title('Veg Map Naip Getter')
root.geometry("+0+0")
try:
    root.iconbitmap(default =  cwd + 'download.ico')
except:
    print 'No icon found'
top = Menu(root)
root.config(menu = top)
################################################################################
#l = Label(root, text = 'Options:')
#l.grid(row = 0, column = 4, sticky = W, padx = 3)
s = Scale(root, from_= 0.5, to = 90, label = 'Output Image Res',orient = HORIZONTAL, resolution = 0.5)
s.set(10)
s.grid(row = 0,column = 3, columnspan = 3, rowspan = 2, sticky = E+N, padx = 0, pady = 2)


l = Label(root, text = 'Declare input as:')
l.grid(row = 2, column = 4, sticky = E, padx = 3)
i_o_f = ['Integer', 'Float']
iof = StringVar(root)
iof.set('Integer')
iofmenu = OptionMenu(root, iof, *i_o_f)
iofmenu.grid(row = 2, column = 5, columnspan = 2, sticky = W)

l = Label(root, text = 'Resampling method:')
l.grid(row = 3, column = 4, sticky = E, padx = 3)
r_s = ['NEAREST NEIGHBOR', 'CUBIC CONVOLUTION']
rs = StringVar(root)
rs.set('NEAREST NEIGHBOR')
rsmenu = OptionMenu(root, rs, *r_s)
rsmenu.grid(row = 3, column = 5, columnspan = 2, sticky = W)

l = Label(root, text = 'Output DataType:')
l.grid(row = 4, column = 4, sticky = E, padx = 3)
dt = StringVar(root)
dt.set('Same_As_Input')
dt_list = erdas_datatype_list.append('Same_As_Input')
datatype_list = list(erdas_datatype_list)
dtmenu = OptionMenu(root, dt, *datatype_list)
dtmenu.grid(row = 4, column = 5, columnspan = 2, sticky = W)


it = '//166.2.126.25/R4_VegMaps/Sawtooth/Imagery/Half_Meter/full_res/Sub_Region_A.shp'
b = Button(root, text = 'Select Study Area Shapefile', height = 1, width = len('Select Study Area Shapefile'), command = select_i_shp)
b.grid(row = 0, column = 1, sticky = E, padx = 3)
i = Entry(root, width = len(it))
i.insert(0, it)
i.grid(row = 0, column = 2, columnspan = 2,sticky = W)

b = Button(root, text = 'Select Output Image', height = 1, width = len('Select Output Image'), command = select_o_image)
b.grid(row = 1, column = 1, sticky = E, padx = 3)
o = Entry(root, width = 60)
o.grid(row = 1, column = 2, columnspan = 2, sticky = W)

b = Button(root, text = 'Image Server Dir', height = 1, width = len('Image Server Dir'), command = select_is_dir)
b.grid(row = 2, column = 1, sticky = E, padx = 3)
#default_is = '//166.2.126.22/Data/National/Imagery/Aerial_Photography/Resource_Photos/Resource_2006_half_meter_Fishlake/'
#default_is = '//166.2.126.71/Data_NAIP/National/Imagery/Aerial_Photography/2011_DOQQ/Utah_2011_NAIP_doqqs/Utah_Statewide_DOQQ_2011/'
default_is = '//166.2.126.30/Data/R4/Imagery/Aerial_Photography/Resource_Photos/Sawtooth_NF/'
is_dir = Entry(root, width = len(default_is))
is_dir.insert(0, default_is)
is_dir.grid(row = 2, column = 2, columnspan = 2, sticky = W)


l = Label(root, text = 'Step 1: Set up imagery list')
l.grid(row = 4, column = 2, sticky = W, padx = 3)
b = Button(root, text = 'Set up imagery folder', height = 1, width = len('Set up Imagery Folder'), command = setup_pseudo_is)
b.grid(row = 5, column = 2, sticky = W)
b = Button(root, text = 'Set up custom NAIP', height = 1, width = len('Set up Custom NAIP'), command = custom_naip_download)
b.grid(row = 6, column = 2, sticky = W)
b = Button(root, text = 'Set up standard NAIP', height = 1, width = len('Set up Standard NAIP'), command = standard_naip_download)
b.grid(row = 7, column = 2, sticky = W)

l = Label(root, text = 'Step 2: Degrade and/or mosaic imagery list')
l.grid(row = 4, column = 3, sticky = W, padx = 3)
b = Button(root, text = 'Degrade Only', height = 1, width = len('Degrade Only'), command = degrade_only)
b.grid(row = 5, column = 3, sticky = W)

b = Button(root, text = 'Degrade and Mosaic', height = 1, width = len('Degrade and Mosaic'), command = degrade_and_mosaic)
b.grid(row = 6, column = 3, sticky = W)


b = Button(root, text = 'Mosaic Only', height = 1, width = len('Mosaic Only'), command = mosaic_only)
b.grid(row = 7, column = 3, sticky = W)
       
modes = [('No Chunks', 'False'), ('Chunks', 'True')]
v = StringVar()
v.set('True')
row_start = 4
for text, mode in modes:
    row_start += 1
    b = Radiobutton(root, text = text, variable = v, value = mode)
    b.grid(row = row_start, column = 4, sticky = W)

modes = [('Do Not Run Model', 'False'), ('Run Model', 'True')]
r = StringVar()
r.set('True')
row_start = 4
for text, mode in modes:
    row_start += 1
    b = Radiobutton(root, text = text, variable = r, value = mode)
    b.grid(row = row_start, column = 5, sticky = W)
#b = Button(root
#b = Button(root, text = 'Run', height = 2, width = 10, command = run_command)
#b.grid(row = 8, column = 2, padx = 5, pady = 5)
b = Button(root, text = "Exit", height = 1, width = 10, command = sys.exit)
b.grid(row = 8, column = 5, sticky = S)



root.mainloop()
