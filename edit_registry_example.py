from _winreg import *
import tkMessageBox, tkFileDialog
from Tkinter import *
root = Tk()
root.withdraw()

try:
    key = OpenKey(HKEY_LOCAL_MACHINE, r'system\currentcontrolset\control\Session Manager\Environment',0,KEY_ALL_ACCESS)
except WindowsError, error:
    if (error.args[1].lower().find('access is denied') >= 0):
        tkMessageBox.showerror('Administrator','Must be administrator')
except Exception, error:
    print error
    tkMessageBox.showerror('Problem!','There was a problem with getting the registry key!')
else:
    Directory = tkFileDialog.askdirectory(parent = root, title = 'Please select a directory').replace('/','\\')
    try:
        Value = QueryValueEx(key,'PYTHONPATH')[0]
    except WindowsError:
        Value = Directory
    except Exception, error:
        print error
        tkMessageBox.showerror('Problem!','There was a problem with getting the PYTHONPATH value!')
    else:
        Value = Value + ';' + Directory
    SetValueEx(key,'PYTHONPATH',0,REG_SZ,Value)
    CloseKey(key)
