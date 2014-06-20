from r_numpy_lib import *
from Tkinter import *
from tkFileDialog import askopenfilename
from tkFileDialog import asksaveasfilename
from tkMessageBox import showwarning
root = Tk()
frame = Frame(root)
frame.pack()
entry = ''
projection = ''
#callbacks

def getinput():
    global Input
    global input_message
    Input =  str(askopenfilename(title = 'Select shapefile to reproject',filetypes=[("Shapefile","*.shp")]))
    try:
        input_message.forget()
    except:
        print
    input_message = Message(frame, text = "Selected shapefile is: " + Input, width = len(Input))
    input_message.pack(side = 'bottom')
def printit():
    print w.cget("text")
    
def getoutput():
    global Output
    global output_message
    Output =  str(asksaveasfilename(title = 'Choose reprojected filename',filetypes=[("Shapefile","*.shp")]))
    try:
        output_message.forget()
    except:
        print
    output_message = Message(frame, text = "Selected reprojected shapefile is: " + Output)
    output_message.pack(side = 'bottom')

def crs():
    projection = ''
    global CRS
    try:
        zone.forget()
        datum.forget()
        w.forget()
    except:
        print
    try:
        CRS.forget()
    except:
        print
    CRS = Entry(frame, width=80)
    CRS.pack(side='top')
    CRS.insert(0,'Enter CRS')
    CRS.configure(state="normal")

def run():
    shapefile = Input
    output = Output
    try:
        crs = CRS.cget("text")
    except:
        crs = ''
        
    if projection == '' and crs == '':
        warning = showwarning('Encountered Error!', 'Please enter CRS or choose a projection and retry running')
    print projection, crs


    
def printit():
    print w.cget("text")

##    zone.update()
def utm():
    global zone
    global datum
    global w
    try:
        zone.forget()
        datum.forget()
        w.forget()
    except:
        print
    try:
        CRS.forget()
    except:
        print 
    global projection
    projection = 'UTM'
    variable = StringVar(root)
    variable.set('Zone')
    zone = OptionMenu(root, variable, 'Zone', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20')
    zone.pack(side = 'top')
        

    variable = StringVar(root)
    variable.set('Datum')
    datum = OptionMenu(root, variable, 'Datum','NAD83', 'WGS84')
    datum.pack(side = 'top')
 
def albers():
    global projection
    projection = 'albers'
    try:
        zone.forget()
        datum.forget()
        w.forget()
    except:
        print
    try:
        CRS.forget()
    except:
        print 

v = IntVar()

b = Button(frame, text = "Input", width = 10, command = getinput)
b.pack()
b2 = Button(frame, text = "Output", width = 10, command = getoutput)
b2.pack()
rb = Radiobutton(frame, text="Enter CRS", variable = v, value = 1,command=crs)
rb.pack(anchor=W)
rb = Radiobutton(frame, text="UTM", variable = v, value = 2,command=utm)
rb.pack(anchor=W)

rb = Radiobutton(frame, text="Albers Conical Equal Area USGS", variable = v, value = 3, command=albers)
rb.pack(anchor=W)

b3 = Button(frame, text = "Run", width = 5, command = run)
b3.pack()
root.mainloop()
