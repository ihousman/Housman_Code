import os, sys, shutil

def flat_to_envi_hdr(input_dir, output_dir, zone = ''):
    hdrs = filter(lambda i: os.path.splitext(i)[1] == '.hdr', os.listdir(input_dir))
    if zone == '':
        zone = str(raw_input('Please enter zone: '))
    zone = str(zone)
    for hdr in hdrs:
        print hdr
        hdri = input_dir + hdr
        hdro = open(hdri, 'r')
        hdrl = hdro.readlines()
        hdro.close()
        for line in hdrl:
            print line
            if line.find('BANDS: ') > -1:
                bands= line.split('BANDS: ')[1][:-1]
            if line.find('ROWS:') > -1:
                lines = line.split('ROWS: ')[1][:-1]
            if line.find('COLS:') > -1:
                samples = line.split('COLS: ')[1][:-1]
                #print samples
            if line.find('UL_X_COORDINATE:') > -1:
                ulx = line.split('UL_X_COORDINATE: ')[1][:-1]
            if line.find('UL_Y_COORDINATE:') > -1:
                uly = line.split('UL_Y_COORDINATE: ')[1][:-1]
        out_lines = 'ENVI\ndescription = {File imported into ENVI.}\n'\
                    'samples = '+samples+'\nlines = '+lines+'\nbands = '+bands+'\nheader offset = 0\nfile type = ENVI Standard\ndata type = 2\n'\
                    'interleave = bsq\nsensor type = Unknown\nbyte order = 0\n'\
                    'map info = {UTM, 1.500, 1.500,'+ulx+','+uly+',30.0000,30.0000,'+zone+', North, WGS-84, units=M}\n'\
                    'wavelength units = Unknown'
        out_hdr = output_dir + hdr
        oho = open(out_hdr, 'w')
        oho.writelines(out_lines)
        oho.close()
##########################################################
def flat_to_envi_hdr_prep(input_dir, output_dir):
    if input_dir[-1] != '/':
        input_dir += '/'
    
    if os.path.exists(output_dir) == False:
        os.makedirs(output_dir)

    hdrs = filter(lambda i: os.path.splitext(i)[1] == '.hdr', os.listdir(input_dir))
    for hdr in hdrs:
        Input = input_dir + hdr
        Output = output_dir + hdr
        if os.path.exists(Output) == False:
            print 'Moving', hdr
            shutil.move(Input, Output)
###############################################################
def fix_headers(from_dir, zone = ''):
    old_hdr_dir = from_dir + 'bsq_hdrs/'
    flat_to_envi_hdr_prep(from_dir, old_hdr_dir) 
    flat_to_envi_hdr(old_hdr_dir, from_dir, zone)

