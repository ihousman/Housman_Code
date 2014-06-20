#Written by: Ian Housman
#Forest Service Remote Sensing Applications Center
##############################################################################################
##############################################################################################
#Returns all files containing an extension or any of a list of extensions
#Can give a single extension or a list of extensions
def glob(Dir, extension):
    if type(extension) != list:
        if extension.find('*') == -1:
            return map(lambda i : Dir + i, filter(lambda i: os.path.splitext(i)[1] == extension, os.listdir(Dir)))
        else:
            return map(lambda i : Dir + i, os.listdir(Dir))
    else:
        out_list = []
        for ext in extension:
            tl = map(lambda i : Dir + i, filter(lambda i: os.path.splitext(i)[1] == ext, os.listdir(Dir)))
            for l in tl:
                out_list.append(l)
        return out_list
##############################################################################################
#Returns all files containing a specified string (Find)
def glob_find(Dir, Find):
    return map(lambda i : Dir + i, filter(lambda i:i.find(Find) > -1, os.listdir(Dir)))
##############################################################################################
#Returns all files ending with a specified string (end)
def glob_end(Dir, end):
    return map(lambda i : Dir + i, filter(lambda i:i[-len(end):] == end, os.listdir(Dir)))
##############################################################################################
##############################################################################################
