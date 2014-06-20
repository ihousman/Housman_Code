import os, sys, shutil
from access_db_lib import *
from r_numpy_lib import *
###############################################################################
cwd = os.getcwd()
parts = cwd.split('\\')
cwd = ''
for part in parts:
    cwd += part + '/'
############################################################################
root = 'O:/02_Inputs/'
city = 'Baltimore'
sensor = 'MODIS'
addon = '_set'
datum = 'NAD83'
calibration_field = 'PCT_IMPV'
combo_range = range(2,5)
zone_dict = {'Atlanta': 16, 'Baltimore' : 18}
res_dict = {'Aster': 90, 'MODIS' : 1000}
point_count_dict = {'Aster': 10000, 'MODIS' : 2000}
point_count = point_count_dict[sensor]
res = res_dict[sensor]
zone = zone_dict[city]
############################################################################
base_dir = root + sensor + '/' + city + '/'
inputs_dir = root + sensor + '/' + city + '/Inputs/'
outputs_dir = root + sensor + '/' + city + '/Set_Outputs/'
calibration_dir = inputs_dir + 'Calibration/'
l_spectral_dir = inputs_dir + 'Landsat_Spectral/'
l_thermal_dir = inputs_dir + 'Landsat_Thermal/'
nlcd_dir = inputs_dir + 'NLCD/'
terrain_dir = inputs_dir + 'Terrain/'
thermal_dir = inputs_dir + 'Thermal/'
thermal_temp_dir = inputs_dir + 'Thermal_Temp/'
mask_dir = inputs_dir + 'Mask/'
anc_master = root + 'Ancillary/Rasters/'
reporting_dir = base_dir + 'Reporting/'
if os.path.exists(reporting_dir) == False:
    os.makedirs(reporting_dir)
############################################################################
mask_layer = mask_dir + os.listdir(mask_dir)[0]
nlcd_lc = anc_master +'nlcd2006_landcover_2-14-11.img'
nlcd_impv = anc_master + 'nlcd2006_impervious_5-4-11.img'

nlcd_impv_clp = nlcd_dir + city + '_' + sensor + '_NLCD_impv.img'
nlcd_lc_clp = nlcd_dir + city + '_' + sensor + '_NLCD_lc.img'


pi_calibration = calibration_dir + 'balt_sample.shp'
nlcd_calibration = calibration_dir + 'nlcd_sample.shp'

out_summary =reporting_dir  + city + '_' +  sensor + '_summary'+addon+'.txt'
var_list_filename = reporting_dir  + city + '_' + sensor + '_variable_count_list'+addon+'.txt'
############################################################################
def bar_plotter(in_list,png_filename, names_column = 0, values_column = 1):
    name_list = 'c("'
    value_list = 'c('
    for line in in_list:
        name_list += str(line[names_column]) + '", "'
        value_list += str(line[values_column])+ ', '
    name_list = name_list[:-3] + ')'
    value_list = value_list[:-2] + ')'
    print name_list
    print value_list
    devoff = RO.r['dev.off']
    r.png(png_filename)
    r('barplot(' + value_list + ', names.arg = ' + name_list + ', cex.names = 5)')

##    r('nlcd_list = ' + r_nlcd)
##    r('pi_list = ' + r_pi)
##    r('r2 = cor(nlcd_list,pi_list)')
##    r('linear = lm(nlcd_list~pi_list)')
##    r('xlab = paste("PI_Based_Out_Values\n", "R2= ", as.character(round(r2, 5)), sep = "")')
##    if modeled_nlcd_raster.find('pi_nlcd') > -1:
##        ylab = 'PI_Loc_NLCD_Based_Out_Values'
##    else:
##        ylab = 'NLCD_Based_Out_Values'
##    r('ylab = "'+ylab+'"')
##    r('plot(pi_list, nlcd_list, main = "' + os.path.splitext(os.path.basename(modeled_pi_raster))[0] + '", xlab = xlab, ylab = ylab)')
##    r('abline(linear)')

    devoff()
###########################################################################
def top_predictors():
    
    start_column = 11
    f_list = []
    fc_list = []
    s_list = []
    t_list = []
    all_list = []
    for line in summ_lines:
        line = line.split('\t')
        line[-1] = line[-1][:-1]
        
        f_list.append(line[start_column].split('.img_')[0])
        all_list.append(line[start_column].split('.img_')[0])
        fc_list.append(line[start_column].split('.img_'))
        
        if len(line) >= start_column + 1:
            s_list.append(line[start_column + 1].split('.img_')[0])
            all_list.append(line[start_column + 1].split('.img_')[0])

        if len(line) >= start_column + 3:
            t_list.append(line[start_column + 2].split('.img_')[0])
            all_list.append(line[start_column + 2].split('.img_')[0])
   
    fvars = list(set(f_list))
    fc_out_list = {}
    for var in fvars:
        count = 0
        for fc in fc_list:
            if var == fc[0]:
                count += int(fc[1])
        fc_out_list[var] = count
        
    print fc_out_list
    f_count = unique_count(f_list)
    s_count = unique_count(s_list)
    t_count = unique_count(t_list)
    print t_count
    all_count = unique_count(all_list)
    
    #print 'allcount', all_count, f_list
    var_open = open(var_list_filename, 'r')
    var_lines = var_open.readlines()
    var_open.close()
    var_dict = {}
    for line in var_lines:
        line = line.split('\t')
        line[-1] = line[-1][:-1]
        var_dict[os.path.splitext(line[0])[0]] = line[1]
        #print line
    #print var_dict
    
    #print f_list
    out_table = 'First_Count_Pred_Name\tFirst_Count\tFirst_Total\tFirst_Percent\tFirst_Cumulative_R2\tSecond_Count_Pred_Name\tSecond_Count\tSecond_Total\tSecond_Percent\tThird_Count_Pred_Name\tThird_Count\tThird_Total\tThird_Percent\tTop Three_Count_Pred_Name\tTop_Three_Count\tTop_Three_Total\tTop_Three_Percent\n'
    for line in range(len(f_count)):
        t_line = ''
        try:
            f_cum = str(fc_out_list[f_count[line][0]])
        except:
            f_cum = ''
        fname = f_count[line][0]
        fcount = f_count[line][1]
        f_var_count = int(var_dict[f_count[line][0]]) * 3
        fp = float(f_count[line][1])/float(f_var_count) * 100

        sname = s_count[line][0]
        scount =  str(s_count[line][1])
        s_var_count = int(var_dict[s_count[line][0]]) * 3
        sp = float(s_count[line][1])/float(s_var_count) * 100
        
        try:
            tname = t_count[line][0]
            tcount = t_count[line][1]
            t_var_count = int(var_dict[t_count[line][0]]) * 3
            tp = float(t_count[line][1])/float(t_var_count) * 100
        except:
            tname = ''
            tcount = ''
            t_var_count = 0
            tp = 0
        print 'tvar', t_var_count, tp
        all_var_count = int(var_dict[all_count[line][0]]) * 3
        allp = float(all_var_count)/float(all_count[line][1]) * 100
        
        t_line += fname + '\t' + str(fcount) + '\t' + str(f_var_count) + '\t' + str(fp) + '\t' + f_cum +'\t' + sname + '\t' + scount + '\t' + str(s_var_count)  + '\t' + str(sp) +   '\t' +tname + '\t' + str(tcount)+ '\t' + str(t_var_count)  + '\t' + str(tp)+   '\t' +all_count[line][0] + '\t' + str(all_count[line][1]) + '\t' + str(all_var_count) + '\t' + str(allp)+'\n'
        out_table += t_line

    out_open = open(reporting_dir + city + '_' + sensor +'_Top_Predictor_Table'+addon+'.txt', 'w')
    out_open.writelines(out_table)
    out_open.close()
    #bar_plotter(f_count, reporting_dir + '1_Pred_Count.png')
#####################################################################################
def sample_type_evaluator():
    start_column = 8
    i = 0
    minr2_list = []
    maxr2_list = []
    minre_list = []
    maxre_list = []
    minae_list = []
    maxae_list = []
    sample_list = ['PI', 'NLCD', 'PI_NLCD']
    big_list = 'Predictor_Combination\tMin_R2\tMaxR2\tMin_RE\tMax_RE\tMin_AE\tMax_AE\n'
    
    for line in summ_lines:
        if (i)%3 == 0:
            
            pi_line = summ_lines[i].split('\t')
            nlcd_line = summ_lines[i + 1].split('\t')
            pi_nlcd_line = summ_lines[i + 2].split('\t')

            pi_line[-1] = pi_line[-1][:-1]
            nlcd_line[-1] = nlcd_line[-1][:-1]
            pi_nlcd_line[-1] = pi_nlcd_line[-1][:-1]
        
            r2s = [pi_line[start_column + 2], nlcd_line[start_column + 2], pi_nlcd_line[start_column + 2]]
            res = [pi_line[start_column + 1], nlcd_line[start_column + 1], pi_nlcd_line[start_column + 1]]
            aes = [pi_line[start_column], nlcd_line[start_column], pi_nlcd_line[start_column]]
            
            max_r2s = max(r2s)
            min_r2s = min(r2s)
            
            max_res = max(res)
            min_res = min(res)
            
            max_aes = max(aes)
            min_aes = min(aes)
            
            for i2 in range(3):
                if r2s[i2] == max_r2s:
                    r2max_var = sample_list[i2]
                elif r2s[i2] == min_r2s:
                    r2min_var = sample_list[i2]
            #for i in range(3):
                if res[i2] == max_res:
                    remax_var = sample_list[i2]
                elif res[i2] == min_res:
                    remin_var = sample_list[i2]
            #for i in range(3):
                if aes[i2] == max_aes:
                    aemax_var = sample_list[i2]
                elif aes[i2] == min_aes:
                    aemin_var = sample_list[i2]
              
            
            minr2_list.append(r2min_var)
            maxr2_list.append(r2max_var)
            minre_list.append(remin_var)
            maxre_list.append(remax_var)
            minae_list.append(aemin_var)
            maxae_list.append(aemax_var)

            
            big_list += pi_line[0].split('sample_')[1] + '\t' + r2min_var + '\t' + r2max_var + '\t' + remin_var + '\t' + remax_var + '\t' +aemin_var + '\t' + aemax_var+ '\n'
        
        i += 1


    minr2_count = unique_count(minr2_list)
    maxr2_count = unique_count(maxr2_list)
    minre_count = unique_count(minre_list)
    maxre_count = unique_count(maxre_list)
    minae_count = unique_count(minae_list)
    maxae_count = unique_count(maxae_list)

    min_max_list = [minr2_count, minre_count, minae_count, maxr2_count, maxre_count, maxae_count]
    min_list = [minr2_count, minre_count, minae_count]
    max_list = [maxr2_count, maxre_count, maxae_count]
    small_lines = '\tR2_Min\tRelative_Error_Min\tAverage_Error_Min\tR2_Max\tRelative_Error_Max\tAverage_Error_Max\n'
    for sample in sample_list:
        small_lines += sample + '\t'
        for List in min_max_list:
        
            contains = False
            for piece in List:
                if piece[0] == sample:
                    tp = piece
                    contains = True
            if contains == False:
                tp = [sample, 0]
            print tp
            small_lines += str(tp[1]) + '\t'
        small_lines = small_lines[:-1] + '\n'
        
    small_open = open(reporting_dir + city + '_' + sensor +'_Sample_Method_Small_Summary'+addon+'.txt', 'w')
    small_open.writelines(small_lines)
    small_open.close()

    big_list_open = open(reporting_dir + city + '_' + sensor +'_Sample_Method_Large_Summary'+addon+'.txt', 'w')
    big_list_open.writelines(big_list)
    big_list_open.close()

    
summ_open = open(out_summary, 'r')
summ_lines = summ_open.readlines()
summ_open.close()
summ_lines = summ_lines[1:]


top_predictors()
sample_type_evaluator()

