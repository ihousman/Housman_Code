#Untars Landsat TM (or any) tarball
import os, sys
from tarfile import *
def untar(tarball, output_dir = '', bands = []):
    if output_dir == '':
        output_dir = os.path.dirname(tarball) + '/'
    out_list = []
    out_folder = os.path.basename(tarball).split('.')[0].split('[')[0]
    
    if os.path.exists(output_dir + out_folder) == False:
        
        
        tar = TarFile.open(tarball, 'r:gz')
        if bands == []:
            print 'Unzipping:', os.path.basename(tarball) 
            tar.extractall(path = output_dir)
        else:
            tar_names = tar.getnames()#[band]
            #print tar_names
            for band in bands:
                
                band = int(band)
                tar_name = tar_names[band]
                output_name = output_dir + tar_name
                out_list.append(output_name)
                if os.path.exists(output_name) == False:
                    print 'Unzipping:', output_dir + tar_name
                    tar.extract(tar_name, path = output_dir)
                
        tar.close()
    else:
        print 'Already unzipped:', os.path.basename(tarball)
    return out_list


folder = 'C:/Users/ihousman/Downloads/'
Input = folder + 'GDAL-1.9.1 (1).tar.gz'
untar(Input, folder)
