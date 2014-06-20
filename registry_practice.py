from _winreg import *

"""print r"*** Reading from SOFTWARE\Microsoft\Windows\CurrentVersion\Run ***" """
aReg = ConnectRegistry(None,HKEY_LOCAL_MACHINE)

aKey = OpenKey(aReg, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall")
for i in range(1024):
    try:
        asubkey_name=EnumKey(aKey,i)
        asubkey=OpenKey(aKey,asubkey_name)
        val=QueryValueEx(asubkey, "DisplayName")
        print val
    except EnvironmentError:
        break
