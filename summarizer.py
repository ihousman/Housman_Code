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
datum = 'NAD83'
addon = '_set'
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
############################################################################
def sample_comparison(modeled_nlcd_raster, modeled_pi_raster, pts = pi_calibration, output_folder = base_dir + 'sample_comparison2/'):
    if os.path.exists(output_folder) == False:
        os.makedirs(output_folder)
    
    png_filename = output_folder + os.path.splitext(os.path.basename(modeled_nlcd_raster))[0] + '.png'
    if os.path.exists(png_filename) == False:
        print 'Making', os.path.basename(png_filename)
        nlcd_list = extract_value_to_list(pts, modeled_nlcd_raster)
        pi_list = extract_value_to_list(pts, modeled_pi_raster)
        if len(nlcd_list) == len(pi_list):
            r_nlcd = 'c('
            r_pi = 'c('
            for entry in nlcd_list:
                r_nlcd += str(entry) + ', '
            r_nlcd = r_nlcd[:-2] + ')'
            for entry in pi_list:
                r_pi += str(entry) + ', '
            r_pi = r_pi[:-2] + ')'
        devoff = RO.r['dev.off']
        r.png(png_filename)
  
        r('nlcd_list = ' + r_nlcd)
        r('pi_list = ' + r_pi)
        r('r2 = cor(nlcd_list,pi_list)')
        r('linear = lm(nlcd_list~pi_list)')
        r('xlab = paste("PI_Based_Out_Values\n", "R2= ", as.character(round(r2, 5)), sep = "")')
        if modeled_nlcd_raster.find('pi_nlcd') > -1:
            ylab = 'PI_Loc_NLCD_Based_Out_Values'
        else:
            ylab = 'NLCD_Based_Out_Values'
        r('ylab = "'+ylab+'"')
        r('plot(pi_list, nlcd_list, main = "' + os.path.splitext(os.path.basename(modeled_pi_raster))[0] + '", xlab = xlab, ylab = ylab)')
        r('abline(linear)')

        devoff()
        
        
############################################################################

outputs = os.listdir(outputs_dir)
outputs = sort(outputs, simple = False)
if sensor == 'MODIS':
    contains_list = ['A2006', 'toa', 'VCT', 'LPGS', 'DEM', 'diff', 'linregress']
else:
    contains_list = ['AST', 'toa', 'VCT', 'LPGS', 'DEM', 'diff', 'linregress']
#c_AST, c_toa, c_VCT, c_LPGS, c_DEM = False, False, False, False, False
i = 0
out_lines = ['Name\tc_'+sensor+'\tc_toa\tc_VCT\tc_LPGS\tc_DEM\tc_Diff\ttc_Stats\tAverage_Error\tRelative_Error\tR2\t1_Usage\t2_Usage\t3_Usage\t4_Usage\t5_Usage\n']
for Dir in outputs:
    print Dir
    temp_line = Dir + '\t'

    for c in contains_list:
        if Dir.find(c) > -1:
            
            temp_line += 'True\t'
        else:
            temp_line += 'False\t'
                
##    if Dir.find('AST') > -1:
##        contains_aster = 'True'
##    else:
##        contains_aster = 'False'
##    if Dir.find('toa') > -1:
        
##    print Dir
##    if i%3 == 0:
##        pi_dir = Dir
##        nlcd_dir = outputs[i + 1]
##        pi_nlcd_dir = outputs[i + 2]
##        nlcd_image = outputs_dir + nlcd_dir + '/' + nlcd_dir + '_cubist_output.img'
##        pi_nlcd_image = outputs_dir + pi_nlcd_dir + '/' + pi_nlcd_dir + '_cubist_output.img'
##        pi_image = outputs_dir + pi_dir + '/' + pi_dir + '_cubist_output.img'
##        #if os.path.exists(nlcd_image) and os.path.exists(pi_image):
##            #sample_comparison(nlcd_image, pi_image)
##        if os.path.exists(pi_image) and os.path.exists(pi_nlcd_image):
##            sample_comparison(pi_nlcd_image, pi_image)

    
    image = outputs_dir + Dir + '/' + Dir + '_cubist_output.img'
    param_report = image + '_parameters_report.txt'
    summary = image + '_model_summary.txt'


    open_param = open(param_report, 'r')
    params = open_param.readlines()
    open_param.close()

    open_summary = open(summary, 'r')
    summs = open_summary.readlines()
    open_summary.close()

    #param_header = 
##    for param in params[1:]:
##        
##        print param

    summ_find_list = ['Average  |error|', 'Relative |error|', 'Correlation coefficient']
    for summ in summs:
        for Find in summ_find_list:
            if summ.find(Find) > -1:
                found = summ.split(Find)[1]
                
                if found[-1] == '\n':
                    found = found[:-1]
                temp_line += str(float(found)) + '\t'
                #print Find, found
  
    usage_list = []
    #var_list = []
    for param in params[1:]:
        param = param.split('\t')
        param[-1] = param[-1][:-1]
        #print param
        #var_list.append(param[1])
        usage_list.append(param[1] + '_' +param[-1])
    
    usage_list = invert_list(sort(usage_list, simple = False, num_place = 1, num_break = '.img_'))
    #print usage_list    
    if len(usage_list) < 5:
        stop = len(usage_list)
    else:
        stop = 5
    for usage in usage_list[:stop]:
        temp_line += usage + '\t'
    temp_line = temp_line[:-1]  +'\n'
    out_lines.append(temp_line)
    i += 1

out_open = open(out_summary, 'w')
out_open.writelines(out_lines)
out_open.close()
