import os,sys,shutil, string, subprocess, urllib, getpass
default_packages = ['rgdal', 'raster', 'maptools', 'Cubist']
r_version = '2.15'
sixty_four =False
cwd = os.getcwd()
user = getpass.getuser()
parts = cwd.split('\\')
cwd = ''
for part in parts:
    cwd += part + '/'
program_files_dir_options = ['C:/Program Files (x86)/', 'C:/Program Files/']
if sixty_four == True:
    program_files_dir = program_files_dir_options[1]
else:
    for option in program_files_dir_options:
        if os.path.exists(option):
            program_files_dir = option
            break
print 'Program files dir:', program_files_dir
try:
    os.putenv('R_LIBS', 'C:/Users/'+user+'/Documents/R/win-library/2.15')
except:
    print 'Could not set R_LIBS environment variable'
    raw_input()
###############################################################################
def install_r_shell(package_name, cleanup = False, install_default_packages = True, default_packages = default_packages):
    install_packages = {'r12'    : ['http://cran.r-project.org/bin/windows/base/old/2.12.1/R-2.12.1-win.exe', 'R-2.12.1-win32.exe']}
                                    #http://cran.cnr.berkeley.edu/bin/windows/base/R-2.15.1-win.exe
                
    url = install_packages[package_name][0]
    exe = cwd + '/'+install_packages[package_name][1]
    if os.path.exists(exe) == False:
        print 'Downloading', os.path.basename(exe)
        File = urllib.urlretrieve(url, exe)
    print 'Installing', package_name
    try:
        call = subprocess.Popen(exe)
    except:
        print 'Running .msi', exe
        call = subprocess.Popen('msiexec /i ' + os.path.basename(exe))
    call.wait()
    if cleanup == True:
        try:
            os.remove(exe)
        except:
            print 'Could not remove:', os.path.basename(exe)

    r1 = R()
    for package in default_packages:
        r1.install(package)
    r1 = None
###############################################################################

class R:
    def __init__(self, libraries = [''], r_dir = program_files_dir + 'R/R-'+r_version+'.1/bin/x64/', wd = cwd + 'temp/', save_image = True, restore_image = True):
        self.rdir = r_dir
        if os.path.exists(self.rdir) == False:
            install_r_shell('r12')
        self.rscript = 'Rscript.exe'
        
        self.wd = wd
        if os.path.exists(self.wd) == False:
            os.makedirs(self.wd)
        self.libs = ''
        for lib in libraries:
            self.libs += lib + ','
        self.libs = self.libs[:-1]

        for i in range(50):
            lock = self.wd + 'r_lock_' + str(i) + '.lock'
            if os.path.exists(lock) == False:
                self.lock_file = lock
        
                self.bat_filename = self.wd + 'r_caller_'+str(i)+'.bat'
                self.r_filename = self.wd + 'r_code_'+str(i)+'.r'
                self.r_output = self.wd + 'r_output'+str(i)+'.txt'
                break
        self.libraries = libraries
    ######################################################
    #Creates and deletes a .lock file to allow for simultaneous processing without any chance of calling on the same .bat/.r files
    def lock(self):
        open_lock = open(self.lock_file, 'w')
    def unlock(self):
        try:
            os.remove(self.lock_file)
        except:
            print 'Could not unlock file:', self.lock
    ###################################################### 
    def r(self, command, get_output = False, save_image = True, restore_image = True):
        self.lock()
        if get_output == False:
            self.command =  command + '\n'
            
        elif get_output == True:
            self.command = 'var_out = ' + command + '\n'
            self.command += 'write(var_out, file = "' + self.r_output + '", sep = "\t")\n'
        self.r_open = open(self.r_filename, 'w')
        self.r_open.writelines(self.command)
        self.r_open.close()
        
        
        self.bat_lines = None
        self.bat_lines = 'echo off\n'
        self.bat_lines += self.rdir[:2] + '\n'
        for part in range(len(self.rdir.split('/'))-1):
            self.bat_lines += 'cd..\n'
        self.bat_lines += 'cd ' + self.rdir + '\n'
        if self.libs != '':
            default_packages = '--default-packages=' + self.libs + ' '
        else:
            default_packages = ''
        if save_image == True:
            save_image = '--save'
        else:
            save_image = ''
        if restore_image == True:
            restore_image = '--restore'
        else:
            restore_image = ''
        self.bat_lines += self.rscript + ' '+save_image+' '+restore_image+' '+ default_packages +' ' + self.r_filename+ '\n'
        
        self.bat_open = open(self.bat_filename, 'w')
        self.bat_open.writelines(self.bat_lines)
        self.bat_open.close()
        Call = subprocess.Popen(self.bat_filename)
        Call.wait()
        self.unlock()
        if get_output == True:
            self.r_output_open = open(self.r_output)
            lines = self.r_output_open.readlines()
            self.r_output_open.close()
            lines_out = []
            for line in lines:
                for part in line.split('\t'):
                    if part[-1] == '\n':
                        part = part[:-1]
                    
                    try:
                        lines_out.append(float(part))
                    except:
                        lines_out.append(part)
            return lines_out
        
    def Rimport(self,script = ''):
        self.lock()
        self.r_filename2 = script
        self.bat_lines = None
        self.bat_lines = 'echo off\n'
        self.bat_lines += self.rdir[:2] + '\n'
        for part in range(len(self.rdir.split('/'))-1):
            self.bat_lines += 'cd..\n'
        self.bat_lines += 'cd ' + self.rdir + '\n'
        if self.libs != '':
            default_packages = '--default-packages=' + self.libs + ' '
        else:
            default_packages = ''
        self.bat_lines += self.rscript + ' --save --restore '+ default_packages + self.r_filename2+ '\n'
        
        self.bat_open = open(self.bat_filename, 'w')
        self.bat_open.writelines(self.bat_lines)
        self.bat_open.close()
        Call = subprocess.Popen(self.bat_filename)
        Call.wait()
        self.unlock()
    def Rfun(self, fun_lib = '', fun_call = '', save_image = True, restore_image = True):
        self.lock()
        shutil.copy(fun_lib, self.r_filename)
        open_file = open(self.r_filename, 'r')

        lines = open_file.readlines()
        open_file.close()
        if lines[-1][-1] != '\n':
            lines[-1] = lines[-1] + '\n'
        lines.append(fun_call)
        open_file = open(self.r_filename, 'w')
        open_file.writelines(lines)
        open_file.close()
          
        if save_image == True:
            save_image = '--save'
        else:
            save_image = ''
        if restore_image == True:
            restore_image = '--restore'
        else:
            restore_image = ''
        self.bat_lines = None
        self.bat_lines = 'echo off\n'
        self.bat_lines += self.rdir[:2] + '\n'
        for part in range(len(self.rdir.split('/'))-1):
            self.bat_lines += 'cd..\n'
        self.bat_lines += 'cd ' + self.rdir + '\n'
        if self.libs != '':
            default_packages = '--default-packages=' + self.libs + ' '
        else:
            default_packages = ''
        self.bat_lines += self.rscript + ' '+save_image+' '+restore_image+ ' '+ default_packages + self.r_filename+ '\n'
        
        self.bat_open = open(self.bat_filename, 'w')
        self.bat_open.writelines(self.bat_lines)
        self.bat_open.close()
        Call = subprocess.Popen(self.bat_filename)
        Call.wait()

        self.unlock()
    
    def install(self, package, cran = 'http://cran.stat.ucla.edu'):
        self.lock()
        self.command =   'r = getOption("repos")\n'
        self.command += 'r["CRAN"] = "'+cran+'"\n'
        self.command += 'options(repos = r)\n'
        self.command += 'install.packages("'+package+'")'
        
        self.r_open = open(self.r_filename, 'w')
        self.r_open.writelines(self.command)
        self.r_open.close()
        
        self.bat_lines = None
        self.bat_lines = 'echo off\n'
        self.bat_lines += self.rdir[:2] + '\n'
        for part in range(len(self.rdir.split('/'))-1):
            self.bat_lines += 'cd..\n'
        self.bat_lines += 'cd ' + self.rdir + '\n'
        
        self.bat_lines += self.rscript + ' '+ self.r_filename+ '\n'
        
        self.bat_open = open(self.bat_filename, 'w')
        self.bat_open.writelines(self.bat_lines)
        self.bat_open.close()
        Call = subprocess.Popen(self.bat_filename)
        Call.wait()
        self.unlock()

