from r_numpy_lib import *
from access_db_lib import *

def state_mbr_extractor(shp, out_dir, state_field_name = 'STATE', buff_deg = 0.3):
    state_list = dbf_to_list(shp, state_field_name)
    out_list = []
    state_mbr_dict  = ''
    out_table = 'State\tXmin\tYmin\tXmax\tYmax\n'
    for state in state_list:
        sql = state_field_name  + ' = ' + state
        output = out_dir + os.path.basename(os.path.splitext(shp)[0]) + '_' + state + '.shp'
        out_list.append(output)
        if os.path.exists(output) == False:
            select_by_attribute(shp, output, sql)
    i = 0
    for out in out_list:
        state_mbr_dict += ',\n' + '"' + state_list[i] + '"' + ' : '
        t_list = []
        out_table += state_list[i] + '\t'
        info = shape_info(out, False)
        coords = info['coords']
        for coord in coords[:2]:
            ct = coord - buff_deg
            
            t_list.append(ct)
            out_table += str(ct) + '\t'
            
        for coord in coords[2:]:
            ct = coord + buff_deg
            
            t_list.append(ct)
            out_table += str(ct) + '\t'
        
        
        state_mbr_dict += str(t_list) 
        out_table = out_table[:-1] + '\n'
        

        i += 1
    state_mbr_dict = 'state_mbr_dict = {' + state_mbr_dict[2:] + '}'

    mbr_dict = out_dir + 'state_mbr_dict.py'
    mbr_o = open(mbr_dict, 'w')
    mbr_o.writelines(state_mbr_dict)
    mbr_o.close()
    
    ot_f = out_dir + 'State_MBR_List.txt'
    ot_fo = open(ot_f, 'w')
    ot_fo.writelines(out_table)
    ot_fo.close()

Dir = 'E:/Riparian_Mapping_Program/Master_Inputs/NAIP/States_Polygon/'
shp = Dir + 'State_Diss_NAD83.shp'
out_dir = 'O:/03_Process/fiddle4/'
state_mbr_extractor(shp, out_dir)
