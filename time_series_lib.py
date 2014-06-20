import os, sys, shutil, math
#sys.path.append('O:/03_Process/Tools/')
from r_numpy_lib import *

##import rpy2.robjects as RO
##import rpy2.robjects.numpy2ri
##r = RO.r
try:
    from scipy import stats
    from scipy import ndimage
    from scipy import signal
    from scipy import ndimage
except:
    install('scipy')
    from scipy import stats
###########################################################################################
#The time_stack object allows for basic and advanced data cube processing
#Upon initiation, the object has basic information computed for it
#All image processes are conducted with array chunks of a specified size
#The size_limit_kb sets the chunk size (of the input)
#If multiple processes are conducted on a single object, this may need to be decreased
class time_stack:
    def __init__(self, input_image, size_limit_kb = 20000):
        #Finds out how many bands there are, along with other basic information
        print 'Initializing', input_image,'as time stack object'
        self.size_limit_kb = size_limit_kb
        self.input_image = input_image
        self.info = raster_info(self.input_image)
        
        #Sets basic variables used for subsequent functions
        self.proj4, self.datum, self.projection, self.transform, self.dt, self.bands, self.res = self.info['proj4'], self.info['datum'],self.info['projection'], self.info['transform'], self.info['dt'],self.info['bands'],  self.info['res']
        self.width, self.height = self.info['width'], self.info['height']
        self.ulxy = [self.transform[0], self.transform[3]]
        self.total_length = self.height * self.width
        self.pixel_count = self.total_length * self.bands
        self.dim = (self.bands, self.height, self.width)
        self.fun_out_band_names_dict = {'stats.ttest_rel' : ['tstat', 'prob'],
                                        'stats.linregress': ['slope', 'intercept', 'r_value', 'p_value', 'std_err'],
                                        'stats.mstats.linregress': ['slope', 'intercept', 'r_value', 'p_value', 'std_err'],
                                        'stats.spearmanr' : ['rho', 'prob'], 'stats.ranksums' : ['zstat', 'pval']}
        
        
        #Sets up the chunk size
        self.file_size =  os.path.getsize(self.input_image)/1024.0
        self.chunk_pointer_maker(self.size_limit_kb)
        
    ###########################################################################################
    #Function that sets up the chunk size based on the specified memory size allocation
    def chunk_pointer_maker(self, size_limit_kb = 100):
        #Calculates the size of the chunk by pixel count
        chunk_no = math.ceil(self.file_size/size_limit_kb)
        pixel_size = float(self.file_size)/ float(self.pixel_count)
        pixels_per_chunk = math.ceil(self.pixel_count/ chunk_no)
        pixels_per_chunk_band = math.ceil(pixels_per_chunk/ self.bands)
        chunk_no_x = math.ceil(math.sqrt(chunk_no))
        chunk_no_y = chunk_no_x
        chunk_size_x = math.ceil(self.width/ chunk_no_x)
        chunk_size_y = math.ceil(self.height/ chunk_no_y)
        self.chunk_size_x = chunk_size_x
        self.chunk_size_y = chunk_size_y
        #Sets the preliminary break points of the pixels
        break_points_x = range(0, int(self.width), int(chunk_size_x))
        break_points_y = range(0, int(self.height), int(chunk_size_y))

        #Sets up the final chunk_list
        #Chunk_list is a list of the chunks
        #Each chunk has the starting_x, starting_y, width_in_pixels, height_in_pixels
        #This is intended to feed into the brick function within the r_numpy_lib.py library
        self.chunk_list = []
        for bp_x in break_points_x:
            stx = bp_x
            spx = bp_x + chunk_size_x
            if spx > self.width:
                spx = self.width
            t_width = spx- stx
            for bp_y in break_points_y:
                sty = bp_y
                spy = bp_y + chunk_size_y
                if spy > self.height:
                    spy = self.height
                t_height = spy - sty
                self.chunk_list.append([stx, sty, int(t_width), int(t_height)])
                
        print 'There are', len(self.chunk_list),'chunks to process'
    ###########################################################################################
    #Creates an empty 3-d array to populate with values using the size of the image (rarely used)
    def empty_stack_maker(self, band_count = '', dt = 'Float32'):
        if band_count == '':
            band_count = self.bands
        #Creates a 3 band 3-d array of zeros to be filled in
        self.empty_stack = []
        for band in range(band_count):
            self.empty_stack.append(empty_raster(self.input_image, dt = dt))
        self.empty_stack = numpy.array(self.empty_stack)
        #return self.empty_stack
    ###########################################################################################
    #Used if array is iterated through with each individual x,y location within the 2-d plane
    #Returns the list of pixels on the z axis for a given x,y location
    def drill(self, column, row):
        self.out_list = []
        for i in range(self.bands):
            self.out_list.append(self.array_list[i][row][column])
        return self.out_list
    ###########################################################################################
    #Fills in the empty 3-d array with the calculated value for each of the corresponding stats
    def stack_filler(self, column, row, fill_list, array_list):
        i = 0
        for s in fill_list:
            self.empty_stack[i][row][column] = s
            i += 1
    ###########################################################################################
    #Transposes a 3-d array to a 2-d array for modeling purposes
    #Returns a 2-d array where each row contains pixels list of values along the z axis
    def vertical_view(self, array_stack, dims):
        return numpy.array(numpy.transpose(array_stack).flat).reshape((dims[1] * dims[2], dims[0]))
    ###########################################################################################
    #The opposite of the function vertical_view
    #Returns a 3-d array from a 2-d array
    def tuple_list_to_array_stack(self, tuple_list, dims):
        return numpy.transpose(numpy.array(tuple_list).reshape(dims))
    ###########################################################################################
    #Mosaics chunks into a single raster
    #Only works on small datasets
    #Will raise a memoryError if the dataset is too large
    def unchunker(self, output, dt = 'Int16'):
        self.empty_stack_maker(band_count = 16, dt = dt)
        i = 0
        brick_list = []
        for chunk in self.output_chunk_list:
            chunk_coords =  self.chunk_list[i]
            bt =  numpy.array(brick(chunk, dt = dt))
            self.empty_stack[0:len(bt),chunk_coords[1]: chunk_coords[1] + chunk_coords[3],chunk_coords[0]: chunk_coords[0] + chunk_coords[2]] = bt
            i += 1
        bt = self.empty_stack
     
        stack(self.empty_stack, output, self.input_image, dt = dt, array_list = True)
    ###########################################################################################
    ###########################################################################################
    ###########################################################################################
    #Stack_fun is a function that allows any function that will work with numpy arrays to easily be applied to an array stack
    #Works with an existing array stack within a time_stack object

    #Parameters:
    #The x_list parameter allows for any uneven time interval to be accounted for (any ordinal value can be used)
    #The x_list parameter default is a sequential list of values incremented by 1 for the number of layers in the stack
    #Only necessary for single_axis = True
    

    #The fun parameter is a string variable corresponding to the desired numpy or scipy function.
    #Must contain the subpackage name if applicable (i.e. stats must be included in stats.linregress unless scipy.stats is imported

    #The single_axis parameter is used to indicate whether the fun needs two variables to model (such as stats.inregress)
    #If the wrong option is chosen, the script will first try and then try to correct the single_axis parameter

    #The args parameter is enables parameters for the chosen fun to be passed in
    #The args are a list of strings that correspond to the parameters within the function call
    #Ex: stack_fun(fun = 'stats.zscore', single_axis = True, args = ['axis = 1'])

    #Possible single_axis = False functions: stats.linregress, stats.pearsonr, stats.spearmanr, stats.ttest_rel, stats.pointbiserialr, stats.ranksums, stats.ansari
    #Possible Single_axis = True functions: stats.zscore args = ['axis = 1'], stats.variation, stats.signaltonoise args = ['axis = 1'], stats.skew args = ['axis = 1'], stats.kurtosis,
    #nd_image.laplace, nd_image.gaussian_laplace args = ['sigma = 1'], nd_image.gaussian_gradient_magnitude, nd_image.gaussian_filter1d args = ['sigma = 1', 'order = 0']
    
    def stack_fun(self, x_list = [], fun = 'stats.linregress', single_axis = True, args = [], na_value = '', min_values_to_run = 3, na_output_value = -32768):

        #Transpose the 3-d array to a 2-d array using the dimensions of the chunk
        t_list = self.vertical_view(self.array_list, self.temp_dim)
       

        #Checks the single_axis setting and runs the corresponding instance of the function
        print 'Computing', fun

        #Single_axis concatenates the call containing any args
        #If no args are specified, only the function and array are passed in
        if single_axis == True:
            try:
                call = fun + '(t_list'
                for arg in args:
                    call += ', ' + arg
                call += ')'
                #The function is called
                stats_list = eval(call)
            except:
                #If this fails, the single_axis parameter is switched in case the user made an error
                single_axis = False
                
        #If single axis is false, the x axis must be included    
        if single_axis == False:
            if x_list == []:
                x_list = numpy.arange(self.bands)
            x_list = numpy.array(x_list)
            ###########################################################################
            ###########################################################################
            #Possible alternate methods of iterating through the list of stacked pixels
            #Starred method (list comprehension) is faster, but does not have a progress bar
            #t_x_array  = numpy.zeros_like(self.array_list)
            #for i in x_list:
            #    t_x_array[i] = i
            #t_x_list = self.vertical_view(t_x_array, self.temp_dim)
   
            #stats_list = map(lambda x,y : eval(fun)(x,y), t_x_list, t_list)
            #**stats_list = [list(eval(fun)(x_list, row)) for row in t_list]
            #stats_list = map(lambda x,y : eval(fun)(x,y), t_x_list, t_list)
            ###########################################################################
            ###########################################################################
            
            #Set up incrementer to provide a progress bar
            i = 0
            last = 0

            #Iterate through each pixel list and append the results to the stats_list
            stats_list = []
            for row in t_list:
                
                if na_value != '':
                    
                    xt_list = x_list[row != na_value]
                    rowt = row[row != na_value]
                else:
                    xt_list = x_list
                    rowt = row
                
                if len(rowt) >= min_values_to_run:
                    
                    try:
                        stats_list.append(list(eval(fun)(xt_list, rowt)))
                    except:
                        fun_parts = fun.split('.mstats')
                        fun = ''
                        for part in fun_parts:
                            
                            fun += part
                        stats_list.append(list(eval(fun)(xt_list, rowt)))
                else:
                    stat_band_count = self.fun_band_no[fun]
                    stats_list.append([na_output_value]*stat_band_count)
                #Check the status with the status_bar function
                last = status_bar(i, len(t_list), last = last)
                i += 1

        #Find the number of dimensions of the output raster stack based on the length of the statistic list that is produced
        try:
            self.stat_dim = len(stats_list[0])
        except:
            self.stat_dim = 1
        print 'Stat dim is', self.stat_dim

        #Converts the list of statistics back to a 3-d stack of the correct number of dimensions
        self.empty_stack = self.tuple_list_to_array_stack(stats_list,(self.temp_dim[2], self.temp_dim[1], int(self.stat_dim)))
    ###########################################################################################
    ###########################################################################################
    ###########################################################################################       
    #Function that handles the chunking, function application, and mosaicking of the stack
    def stack_fit(self, output_image, year_list = [], fun = 'stats.linregress',  single_axis = True, args = [], df = 'HFA',dt = 'Float32', chunk_list_start_stop = [], band_list = [],na_value = '', min_values_to_run = 3, na_output_value = -32768):
        self.fun_band_no = {'stats.linregress': 5, 'numpy.diff': len(band_list)-1, 'stats.variation' : 1, 'stats.skew' : 1,
                            'stats.ttest_rel': 2, 'stats.spearmanr' : 2, 'stats.skew' : 1, 'stats.ranksums' : 2, 'stats.signaltonoise' : 1,
                            'numpy.mean': 1, 'numpy.sum' : 1, 'numpy.std' : 1}
        #Set up the chunk list and start time
        self.output_chunk_list = []
        start = time.time()
        try:
            stat_band_count = self.fun_band_no[fun]
        except:
            if band_list != []:
                stat_band_count = len(band_list)
            else:
                stat_band_count = ''
        all_tiles = tiled_image(output_image, self.input_image, dt = dt, bands = stat_band_count)
        #The option of only processing a subset of the chunk_list is checked (intended to use for parallel processing)
        if chunk_list_start_stop != []:
            self.chunk_list = self.chunk_list[chunk_list_start_stop[0]: chunk_list_start_stop[1]]
            chunk_no = chunk_list_start_stop[0]
        else:
            chunk_no = 1

        #Iterate through each chunk in the chunk_list
        for chunk in self.chunk_list:
            print chunk, chunk_no

            #If only one chunk exists, the output name is assigned to the chunk
            #Otherwise, an extension with the chunk number is added to the name
##            if len(self.chunk_list)> 1:
##                output_chunk = os.path.splitext(output_image)[0] + str(chunk_no) + os.path.splitext(output_image)[1]
##            else:
##                output_chunk = output_image
            
##            #The output list is appended   
##            self.output_chunk_list.append(output_chunk)

            #Checks to see if the chunk exists prior to applying the function
##            if os.path.exists(output_chunk) == False:

            #Reads in the piece of the stack as a Numpy array based on the chunk offsets
            self.array_list = brick(self.input_image, xoffset =  chunk[0], yoffset = chunk[1], width = chunk[2], height = chunk[3], band_list = band_list)
            if band_list != []:
                self.bands = len(band_list)
            self.temp_dim = [self.bands, chunk[3], chunk[2]]

            #Calls on the stack_fun function that populates the self.empty_stack variable
            self.stack_fun(x_list = year_list, fun = fun, single_axis = single_axis, args = args, na_value = na_value, min_values_to_run = min_values_to_run, na_output_value = na_output_value)
            all_tiles.add_tile(self.empty_stack, chunk[0], chunk[1])
            
                #Construct the transform for the chunk
##                t_transform = [self.ulxy[0] + self.res * chunk[0], self.res, 0.0, self.ulxy[1] - (self.res * chunk[1]), 0.0, -1 * self.res]

                #Create a chunk stack using the stack function
                #stack(self.empty_stack, output_chunk, width = chunk[2], height = chunk[3], projection = self.projection, transform = t_transform, df = df, dt = dt, array_list = True)
                
                
                #Tries to unstack the chunk and assign the proper names to it
                #(currently only stats.linregress has names assigned to the statistics returned)
##                try:
##                    var_names = self.fun_out_band_names_dict[fun]
##                    band_count = raster_info(output_chunk)['bands']
##                    for band in range(1, band_count + 1):
##                        restack(output_chunk, os.path.splitext(output_chunk)[0] + '_' + var_names[band-1] + os.path.splitext(output_chunk)[1], df = df, band_list = [band])
##                except:
##                    print 'Could not find variable names'
            #Increments the chunk_no
            chunk_no += 1
        
        
        all_tiles.rm()
##        image_limit_t = 23 * 20000 
##        image_limit = int(math.floor(image_limit_t / self.size_limit_kb))
##        if len(self.output_chunk_list) > 1:
##            if os.path.exists(output_image) == False:
##                sub_chunks = math.ceil(float(len(self.output_chunk_list)) / float(image_limit))
##                if sub_chunks > 1.0:
##                    sub_chunk_list = []
##                    for i in range(int(sub_chunks)):
##                        sub_chunk = os.path.splitext(output_image)[0] + '_sub_chunk_'+ str(i) + os.path.splitext(output_image)[1]
##                        if os.path.exists(sub_chunk) == False:
##                            merge(self.output_chunk_list[i * image_limit : i * image_limit + image_limit], sub_chunk, Format = df)
##                        sub_chunk_list.append(sub_chunk)
##                    if os.path.exists(output_image) == False:
##                        merge(sub_chunk_list, output_image, Format = df)
##                else:
##                    if os.path.exists(output_image) == False:
##                        merge(self.output_chunk_list, output_image, Format = df)
####                if len(self.output_chunk_list) <= 23:
####                    merge(self.output_chunk_list, output_image, Format = 'GTiff')
####                else:
####                    reproject(self.output_chunk_list, output_image)
####
        
        
        try:
            band_count = raster_info(output_image)['bands']
            var_names = self.fun_out_band_names_dict[fun]
            for band in range(1, band_count + 1):
                band_output = os.path.splitext(output_image)[0] + '_' + var_names[band-1] + os.path.splitext(output_image)[1]
                #if os.path.exists(band_output) == False:
                try:
                    restack(output_image, band_output, band_list = [band])
                except:
                    print 'Could not produce', output_image
        except:
            print 'Could not find variable names'
        
        end =  time.time()
        time_diff = end - start
        if time_diff > 60:
            
            print 'Took', time_diff/60, 'minutes to complete'
        else:
            print 'Took', time_diff, 'seconds to complete'

        report_lines = ''
        report_lines += 'Input Image Name: ' + self.input_image + '\n'
        report_lines += 'Output Image Name: ' + output_image + '\n'
        report_lines += 'Function Name: ' + fun + '\n'
        report_lines += 'Arguments: ' + str(args) + '\n'
        report_lines += 'Output data type: ' + dt + '\n'
        report_lines += 'Bands used: ' + str(band_list) + '\n'
        report_lines += 'Output band count: ' + str(stat_band_count) + '\n'
        report_lines +='\nWKT Projection: ' + self.projection + '\nProj4 Projection: ' + self.proj4 + '\nResolution: ' + str(self.res) + '\nWidth: ' + str(self.width) + '\nHeight: ' + str(self.height) + '\nProcessing time (minutes): ' + str(time_diff/60)
        report_filename = os.path.splitext(output_image)[0] + '_metadata.txt'
        report_open = open(report_filename, 'w')
        report_open.writelines(report_lines)
        report_open.close()

    ###########################################################################################
    ###########################################################################################
    ###########################################################################################
    def parallel(self, fun_call, number_of_processes = 2, script_dir = cwd + 'temp/'):
        if os.path.exists(script_dir) == False:
            os.makedirs(script_dir)
##        script_copy = script_dir + os.path.basename(script_name)
##        shutil.copy(script_name, script_copy)
##        script_open = open(script_name, 'r')
##        script_lines = script_open.readlines()
##        script_open.close()
##        for line in script_lines:
##            print line
        chunks_pp = int(math.ceil(float(len(self.chunk_list)) / float(number_of_processes)))
        print chunks_pp
        for process in range(number_of_processes):
            start = process * chunks_pp
            stop = (process * chunks_pp) + chunks_pp
            if stop + 1 > len(self.chunk_list):
                stop = len(self.chunk_list)
            exec('process_' + str(process) + '= ['+str(start)+', '+ str(stop) + ']')
            exec('print process_' + str(process))
            fun_call_temp = fun_call[:-1] + ', chunk_list_start_stop = [' + str(start) + ', ' + str(stop) + '])'
            py_lines = ['from time_series_lib import *\n']
            #py_lines.append(

    ###########################################################################################
    ###########################################################################################
    ###########################################################################################      
    def rm(self):
        self.array_list = None
        self.empty_stack = None
        self.t_x_array = None
        self.stat_list = None
        
