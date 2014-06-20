import os, sys, shutil



in_dir = 'O:/02_Inputs/MODIS/Bend/Set_Model_Test_Outputs_Boot_CV1/'
out_dir = 'Q:/01_Documentation/01_Planning/Project_Report/Graphics/'
extension = '_boot_summary.txt'
out_file = out_dir + 'MODIS_Comparison_Report_boot.txt'
############################################
os.listdir
in_dirs = os.listdir(in_dir)
out_lines = '\tSVM_MAE\tSVM_RMSE\tSVM_R2\tRF_MAE\tRF_RMSE\tRF_R2\tCubist_MAE\tCubist_RMSE\tCubist_R2\n'

for Dir in in_dirs:
    print Dir
    out_lines += Dir[2:] + '\t'
    Files = os.listdir(in_dir + Dir)
    fc = 0
    for File in Files:
        if File.find(extension) > -1:
            fc += 1
            of = open(in_dir + Dir + '/' + File)
            lines = of.readlines()[1:]
            of.close()
            for line in lines[3:]:
                line = line.split('\t')
                line[-1] = line[-1][:-1]
                out_lines += line[2] + '\t' + line[3] + '\t' + line[4] + '\t'
                #print line
            
            print 'yay'
            print
            print
            out_lines += '\n'
    if fc == 0:
        out_lines += '\n'
oo = open(out_file, 'w')
oo.writelines(out_lines)
oo.close()
