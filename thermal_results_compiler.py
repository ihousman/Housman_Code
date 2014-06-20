import os, sys, shutil


Dir = 'O:/02_Inputs/Aster/'
cities = ['Baltimore', 'Atlanta', 'Bend']
doi = ['Set_Model_Test_Outputs_Boot_CV1', 'Set_Model_Test_Outputs_Boot_CV1', 'Set_Model_Test_Outputs_Boot_CV1']
final_report = Dir + 'final_report_cv4.txt'
allowed_folders = ['__win__night__sum__day','__AST__win__day__night__sum', '__VCT_summer__win__VCT_w__LPGS_s__LPGS_w', '__win__toa_w__toa_s__sum', '__AST__sum__day__night', '__VCT_summer__LPGS_s', '__toa_s__sum']
calibration_dict = {'balt_sample': 'PI', 'Atlanta_sample': 'PI','nlcd_sample': 'NLCD', 'pi_nlcd_sample': 'PI_Loc_NLCD_Values'}
pred_dict = {'AST__win__night__sum__day': 'ASTER 08','AST__sum__day__night': 'ASTER 08', 'AST__win__day__night__sum': 'ASTER 08', 'sum__VCT_summer__LPGS_s': 'Landsat TM Thermal', 'sum__VCT_summer__win__VCT_w__LPGS_s__LPGS_w': 'Landsat TM Thermal', 'toa_s__sum': 'Landsat TM Spectral', 'win__toa_w__toa_s__sum': 'Landsat TM Spectral'}
out_lines = 'City\tCalibration Method\tPredictors\tModel Method\tMAE\tRMSE\tR2\tRun Time\n'#SVM_MAE\tSVM_RMSE\tSVM_R2\tRF_MAE\tRF_RMSE\tRF_R2\tCubist_MAE\tCubist_RMSE\tCubist_R2\tMin_MAE\tMine_RMSE\tMax_R2\n'
i = 0
for city in cities:
    doi_dir = Dir + city + '/' + doi[i] + '/'

    folders = os.listdir(doi_dir)
    for folder in folders:
        allowed = False
        for af in allowed_folders:
            if folder.find(af) > -1 and folder.find('pi_nlcd_sample') == -1:
                allowed = True
        if allowed:
            ft = doi_dir + folder + '/'
            summary = filter(lambda i : i.find('_boot_summary.txt') > -1, os.listdir(ft))[0]
            #print city, folder, summary

            summary = ft + summary

            so = open(summary, 'r')
            sl = so.readlines()
            so.close()
            header = sl[0]
            header = header.split('\t')
            header[-1] = header[-1][:-1]
            #print header

            maet = {}
            rmset = {}
            r2t = {}
            olt = city + '\t' + calibration_dict[folder.split('__')[0][2:]] + '\t' + pred_dict[folder.split('sample__')[1]] + '\t'
            #out_lines += city + '\t' + folder.split('__')[0] + '\t' + folder.split('sample__')[1] + '\t' 
            for line in sl[1:4]:
                line = line.split('\t')
                line[-1] = line[-1][:-1]
                out_lines += olt + line[0][3:] + '\t' + line[2] + '\t' + line[3] + '\t' + line[4]+ '\t' + str(float(line[-1])/60.0) + '\n'
                
                
                #print line
                maet[float(line[2])] = line[0]
                rmset[float(line[3])] = line[0]
                r2t[float(line[4])] = line[0]
            #out_lines += maet[min(maet)] + '\t'+ rmset[min(rmset)] + '\t' + r2t[max(r2t)] 
                
            #out_lines += '\n'
            print city, folder, maet[min(maet)], maet
            print
            print
            print



    
    i += 1

oo = open(final_report, 'w')
oo.writelines(out_lines)
oo.close()
