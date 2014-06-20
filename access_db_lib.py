import os, sys, math, random, string, shutil
try:
    import pyodbc
except:
    print 'Could not find pyodbc module'
    print 'Will not be able to use Access db functions'
from dbfpy import dbf
###############################################################################

def access_table_header(mdb, table):
    #Initiate cursor using pyodbc package
    #Think of a cursor as you would see your cursor in a specified table in Access
    #Since pyodbc provides some nifty functions, this is faily simple
    conn = pyodbc.connect('DRIVER={Microsoft Access Driver (*.mdb)};DBQ='+mdb)
    cursor = conn.cursor()
    columns = []
    column_names = cursor.columns(table)

    for column in column_names:
        columns.append(str(column.column_name))
    return columns
############################################################################
#Function to convert a mdb to a list
#Reads in an Access database and extracts a column that begins with a specified set
#of letters from a specified table
#e.g. access_to_list(access_database, some_table_name, column_number, set_of_letters_needed_within_column_number_to_be_included, list of column numbers to return)
def access_to_list(mdb, table = 'plotSpectral', column = 1, prefix = '', wanted_columns = [0,4,5, 6,7], include_all_columns = False, echo = False,tab_delimited = True):
    #Prompt user what database is being compiled
    print 'Compiling: ' + mdb.split('/')[-1]

    #Initiate cursor using pyodbc package
    #Think of a cursor as you would see your cursor in a specified table in Access
    #Since pyodbc provides some nifty functions, this is faily simple
    conn = pyodbc.connect('DRIVER={Microsoft Access Driver (*.mdb)};DBQ='+mdb)
    cursor = conn.cursor()

    #Next, a SQL statement is used to select the table of interest using the .execute function
    cursor.execute("select* from "+table)

    #Next, the data is fetched using the .fetchall function and placed into memory within Python
    mdb_rows = list(cursor.fetchall())

    #The rows are sorted based on their ID
    #This ensures that the list matches the .dbf list's order
    mdb_rows.sort()

    #Initiate some list variables that will be used to build the output list
    out_list = []
    echo_list = []

    if include_all_columns == True:
        wanted_columns = []
        column_names = cursor.columns()
        i = 0
        for column1 in column_names:
            wanted_columns.append(i)
            i += 1

    #Iterate through each row of the mdb rows
    rowi = 1
    for row in mdb_rows:
        #print rowi
        #Pull out the column from the row if it begins with the specified prefix
        #In this case, this ensures that only the later date entry is included in the list
        if str(row[column])[:len(prefix)] == prefix:
            if tab_delimited:
                out_list_row = ''
            else:
                out_list_row = []
            for i in range(len(row)):
                #, row
                if i in wanted_columns:
                    if tab_delimited:
                        try:
                            out_list_row += str(row[i]) + '\t'
                        except:
                            out_list_row += '\t'
                    else:
                        try:
                            out_list_row.append(str(row[i]))
                        except:
                            xrange = 0
            if tab_delimited:
                out_list_row = out_list_row[:-1]
            #The row is appended to the returned list
            out_list.append(out_list_row)

            #This code was created in order to find any duplicate entries
            if echo == True:
                echo_list.append(row[0])

        rowi += 1

    #This checks to find any duplicate points
##    if echo == True:
##        for row in range(1, len(echo_list)):
##            if int(echo_list[row]) != echo_list[row-1] + 1:
##                print 'Duplicate: ' + str(echo_list[row])
    #The out_list is returned
    return out_list
########################################################################################
#Function to convert a specified column from a specified dbf file into a list
#e.g. dbf_to_list(some_dbf_file, integer_column_number)
def dbf_to_list(dbf_file, field_name):
    if os.path.splitext(dbf_file)[1] == '.shp':
        dbf_file = os.path.splitext(dbf_file)[0] + '.dbf'
    #The next exception that is handled is handled within an if loop
    #This exception would occur if a non .dbf file was entered
    #First it finds wither the extension is not a .dbf by splitting the extension out
    if os.path.splitext(dbf_file)[1] != '.dbf':
        #Then the user is prompted with what occured and prompted to exit as above
        print 'Must input a .dbf file'
        print 'Cannot compile ' + dbf_file
        raw_input('Press enter to continue')
        sys.exit()

    #Finally- the actual function code body
    #First the dbf file is read in using the dbfpy Dbf function
    db = dbf.Dbf(dbf_file)
    #Db is now a dbf object within the dbfpy class

    #Next find out how long the dbf is
    rows = len(db)

    #Set up a list variable to write the column numbers to
    out_list = []

    #Iterate through each row within the dbf
    for row in range(rows):
        #Add each number in the specified column number to the list
        out_list.append(db[row][field_name])
    db.close()
    #Return the list
    #This makes the entire function equal to the out_list
    return out_list
################################################################
#Rotates a 2-d array 90 degrees
def transpose(in_array):
    tab = in_array
    out_tab = []
    for row in range(len(tab[0])):
        temp = []
        for column in range(len(tab)):
            temp.append(tab[column][row])
        out_tab.append(temp)
    return out_tab
#Extracts a list of fields from a dbf or shp to a 2-d array and returns the array
def multiple_field_extraction(dbf, field_list, Transpose = True):
    tab = []
    if os.path.splitext(dbf)[1] == '.shp':
        dbf = os.path.splitext(dbf)[0] + '.dbf'
    for field in field_list:
        print 'Extracting field:', field
        temp = dbf_to_list(dbf, field)
        tab.append(temp)

    if Transpose == True:
        return transpose(tab)
    else:
        return tab
##
##Dir = 'R:/NAFD/Acc_Assessment/VCT_Outputs/Final_Mosaic/'
##mich = Dir + 'vct_glri_final_output_michigan_clump.tif.vat.dbf'
##sup = Dir + 'vct_glri_final_output_superior_clump.tif.vat.dbf'
##m = multiple_field_extraction(mich, ['Value'])
##print len(m)
#Dir = 'W:\03_Data-Archive\02_Inputs\SA
################################################################
def unscrambler(ordered_list, scrambled_list, dec_places = 1):
    out_dict = []

    i1 = 0
    for order in ordered_list:

        temp_o = []
        for o in order:
            o = float(o)
            temp_o.append(round(o, dec_places))
        i2 = 0
        for scramble in scrambled_list:
            temp_s = []
            for s in scramble:
                s = float(s)
                temp_s.append(round(s, dec_places))
            if temp_s == temp_o:

                out_dict.append([i1, i2])

            i2 +=1
        i1 += 1
    out_dict = dict(out_dict)
    return out_dict
#############################################################
def unique(List):
    return list(set(List))
################################################################
def open_mdb(mdb):
    conn = pyodbc.connect('DRIVER={Microsoft Access Driver (*.mdb)};DBQ='+mdb)
    cursor = conn.cursor()
    return conn, cursor

def add_row(mdb, table, field_names = [], values = []):
    db = open_mdb(mdb)
    cursor = db[1]
    conn = db[0]
    execute_string = 'insert into ' +table + '('
    for field in field_names:
        execute_string += str(field) + ', '
    execute_string = execute_string[:-2] + ') values ('
    for value in values:
        execute_string += str(value) + ', '
    execute_string = execute_string[:-2] + ')'
    print execute_string
    cursor.execute(execute_string)
    conn.commit()

def delete_row(mdb, table, field_name, field_value):
    db = open_mdb(mdb)
    cursor = db[1]
    conn = db[0]
    cursor.execute('delete from ' + table + ' where ' + field_name + ' = ' + str(field_value) + '')
    conn.commit()

def cbind(column_list):
    out_list = []

    for row in range(len(column_list[0])):
        temp = []
        for column in column_list:
            temp.append(column[row])
        out_list.append(temp)
    return out_list
##Dir = 'R:/NAFD/Acc_Assessment/Comparison/QA/Inputs/'
##mdb = Dir + 'template_database_summer.mdb'
##table = 'plots'
##field_names = ['plotid', 'X', 'Y']
##values = [1,2,3]
##add_row(mdb, table, field_names, values)
##delete_row(mdb, table, field_names[0], values[0])
