##########################
# Author: Surbhi Mittal  #
##########################

import os
import json

def read_text_from_file(path, file_name):
    """
    Opens and returns the contents of a text file.

    Parameters
    ----------
    path: path where text file exists
    file_name: name of the text file

    Returns
    -------
    contents of text file
    """
    
    #file_name = path + "\\" + file_name	#windows
    file_name = path + "/" + file_name
    file = open(file_name,'r')
    text = file.read()
    file.close()
    return text

def write_text_to_file(path, file_name,text):
    """
    Creates a text file from given text.

    Parameters
    ----------
    path: path where text file is to be created
    file_name: name of the text file
    text: text content to be written to the file
    """
    
    #file_name = path + "\\" + file_name	#windows
    file_name = path + "/" + file_name
    text = str((text.encode('ascii','ignore')).decode('utf-8'))
    file = open(file_name,'w')
    file.write(text)
    file.close()
    
def read_list_from_file(path, file_name):
    """
    Opens and returns the contents of a text file as a list.

    Parameters
    ----------
    path: path where text file exists
    file_name: name of the text file

    Returns
    -------
    contents of text file as a 1-D list of strings.
    """
    
    #file_name = path + "\\" + file_name	#windows
    file_name = path + "/" + file_name
    li = []
    with open(file_name) as file:
        for line in file:
            line = line.strip() #or some other preprocessing
            li.append(line)
        file.close()
    return li
    
def write_list_to_file(path, file_name, li):
    """
    Creates a text file from given list.

    Parameters
    ----------
    path: path where text file is to be created
    file_name: name of the text file
    li: list to be written to the file
    """

    #file_name = path + "\\" + file_name	#windows
    file_name = path + "/" + file_name
    with open(file_name, 'w') as file:
        for item in li:
            i = str(item)
            file.write("%s\n" % i)
        file.close()    
    
def read_dict_from_file(path, file_name):
    """
    Opens and returns the contents of a text file as a dictionary.

    Parameters
    ----------
    path: path where text file exists
    file_name: name of the text file

    Returns
    -------
    contents of text file as a dictionary
    """

    di = {}
    #file_name = path + "\\" + file_name	#windows
    file_name = path + "/" + file_name
    with open(file_name, 'r') as file:
        t = file.read()
        di = json.loads(t)
        file.close()
    return di
    
def write_dict_to_file(path, file_name, di):
    """
    Creates a text file from given dictionary.

    Parameters
    ----------
    path: path where text file is to be created
    file_name: name of the text file
    di: dictionary to be written to the file
    """

    #file_name = path + "\\" + file_name	#windows
    file_name = path + "/" + file_name
    with open(file_name, 'w') as file:
        file.write(json.dumps(di))
        file.close()

def create_folder(path, folder_name):
    """
    Creates a folder with given name.

    Parameters
    ----------
    path: path where the folder should be created
    folder_name: name of the folder to be created
    """
    
    #path = path + "\\" + folder_name
    path = path + "/" + folder_name
    print(path)
    try:
        os.mkdir(path)
    except OSError:
        print ("Creation of the directory %s failed" % path)
