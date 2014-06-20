from Tkinter import *
from r_numpy_lib import *
import os, shutil
##def square(x):
##  return x*x
##
##fun = 'square'
##print eval(fun + '(3)')
def exit():
  sys.exit()
script = 'r_numpy_lib.py'
copy = 'copy.py'

shutil.copy(script, copy)

open_s = open(copy, 'r')
lines = open_s.readlines()
open_s.close()

groups = []
group_lists = {'install': ['install', 'loader'],
               'convert': ['convert'],
               'raster': ['raster', 'ndi','composite', 'stack', 'intersection', 'clip', 'invert', 'recode', 'break', 'combine', 'mask', 'gdal', 'reproject', 'field', 'extract'],
               'shapefile': ['shapefile'],
               'stats': ['combo', 'sample', 'cubist'],
               'utils': ['utm', 'hist']
               }

  
fun_list = []
for line in lines:
  if line.find('def ') > -1 and line.find('guiable = True') > -1:
    fun = line.split('(')[0][4:]
    params = line.split('(')[1][:-3]
    
    temp = [fun, params]
    fun_list.append(temp)

for group in group_lists:
  temp = [group]
  for name in group_lists[group]:
    for fun in fun_list:
      if fun[0].find(name) > -1:
      
        temp.append(fun[0])
  groups.append(temp)


root = Tk()
root.geometry("+0+0")
root.title('RSAC Open Source Processing Toolbar')
top = Menu(root)
root.config(menu=top)
b = Button(root, text =  "Exit", height = 1, width = 50,command = sys.exit)
b.pack( side = LEFT, padx=5, pady=0)
for group in groups:
  
  group_name = group[0]
  post = Menu(top)

 
  for fun in group[1:]:
    post.add_command(label = fun, command = eval(fun), underline = 0)
  top.add_cascade(label = group_name, menu = post, underline = 0)


  
raw_input()
