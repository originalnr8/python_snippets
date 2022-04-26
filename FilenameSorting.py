# Description #
# Got a lot of badly patterned filenames? eg Powerpuff Girls - S01E02 - Motherfucking Mojo Jojo - 480p.DiVX.CockRocket.mp4
# This is remove prefix filename duplication and suffix filename duplication chaning to above to 02 - Motherfucking Mojo Jojo.mp4
# Got a folder with folder of folders with badly patterned filenames? It will do that too.
# Just make sure everything is grouped in folders so a clean pattern can be discerned. eg all season 1 stuff in season 1 folder

# Usage #
#  FilenameSorting.py <path to folder>

# Run types #
# Debug run  - Will output a file showing the changes it will make padded to show exactly how.
#            - Will also ask if the generic removal pattern discovered looks right
# Normal run - Will just find generic removal pattern and rename everything

import sys
import os
import datetime

generalised = ""

def fetchPath():
    #return "/Volumes/Refusal/Videos/Daria/Season 04"
    arguments = sys.argv[1:]
    if len(arguments) >= 1:
        return arguments[0]
    else:
        return os.getcwd()

def listDirs(rootdir):
    dirs = []
    for it in os.scandir(rootdir):
        if it.is_dir():
            fullpath = os.path.join(rootdir, it)
            dirs.append(fullpath)
            dirs.extend(listDirs(fullpath))
    return dirs

def listFilenames(mypath):
    onlyfiles = []
    #onlyfiles = [f for f in os.listdir(mypath) if os.path.isfile(os.path.join(mypath, f))]
    for f in os.listdir(mypath):
        if os.path.isfile(os.path.join(mypath, f)):
            onlyfiles.append(f)

    return onlyfiles

def split(word):
    return [char for char in word]

def convert(chars):
    word = ""
    for x in chars:
        word += x
    return word

def analyse(filenames):
    # Get biggest name and smallest
    fn = filenames[0]
    charFN = split(fn)
    max_length = len(fn)
    min_length = max_length
    biggest = ""
    smallest = ""
    for i in filenames:
        filename = i
        if len(filename) < min_length:
            min_length = len(filename)
            smallest = filename
            fn = filename
            charFN = split(fn)
        elif len(filename) > max_length:
            max_length = len(filename)
            biggest = filename

    # Generalise the all names in relation to the largest name
    for i in filenames:
        charFilename = split(i)
        for j in range(min_length):
            if charFN[j] != charFilename[j]:
                charFN[j] = "*"
        generic = convert(charFN)

    return generic

def analyseFilenames(filenames):
    # any?
    if len(filenames) == 0:
        if debug ==True:
            print("No files present")
        return []

    generic = analyse(filenames)
    try:
        i = generic.index('*')
    except:
        if debug ==True:
            print("One file found")
        return []
    idxPrefix = indexStart(generic)

    revGeneric = analyse(reverseFilenames(filenames))
    try:
        i = revGeneric.index('*')
    except:
        if debug ==True:
            print("One file found")
        return []
    idxSuffix = indexStart(revGeneric)

    return [ idxPrefix, idxSuffix ]

def removeFileExtensions(filenames):
    file = []
    for filename in filenames:
        idx = -1 * countFileExtension(filename)
        if len(filename[:idx]) > 0:
            file.append(filename[:idx])
    return file

def reverseFilenames(filenames):
    newfilenames = []
    for filename in filenames:
        file = split(filename)
        newfile = []
        for chr in range(len(file),0,-1):
            newfile.append(file[chr-1])
        newfilename = convert(newfile)
        newfilenames.append(newfilename)
    return newfilenames

def indexStart(name):
    return name.index('*')

def indexEnd(name):
    return name.rindex('*')

def countFileExtension(filename):
    try:
        idx = filename.rindex('.')
    except:
        return 0
    extension = filename[idx:]
    idxExtension = len(extension)
    return idxExtension

def debug_output(textmessage):
    dtnow = datetime.datetime.now()
    dt = dtnow.strftime("%Y%m%d%H%M%S")
    dt = dtnow.strftime("%Y%m%d%H%M")
    f = open(os.path.join(rootfolder, dt + ".log"), "a")
    f.write(textmessage)
    f.close()

def pad(number):
    padding = ""
    for i in range(number):
        padding += " "
    return padding

def renameFile(folder, file, prefix, suffix):
    # chop up information
    extsize = countFileExtension(file) * -1
    fileextension = file[extsize:]
    file_noextension = file[:extsize]
    # original
    filepath = os.path.join(folder, file)
    # new
    choppedfile = file_noextension[prefix:convertSuffixIndexToPrefix(file_noextension, suffix)]
    newfile = choppedfile + fileextension
    newfilepath = os.path.join(folder, newfile)

    if debug == True:
        #debug_output("mv " + filepath + " " + newfilepath)
        #debug_output('\n')
        debug_output(file)
        debug_output('\n')
        debug_output(pad(prefix) + choppedfile + pad(suffix) + fileextension)
        debug_output('\n')
    else:
        os.rename(filepath, newfilepath)

def renameFiles(folderpath, indexes):
    filenames = listFilenames(folderpath)
    for i in filenames:
        length = len(i)
        if indexes[1] < 0:
            renameFile(folderpath, i, indexes[0], length)
        else:
            renameFile(folderpath, i, indexes[0], indexes[1])

def askQuestion_string(question):
    return str(input(question))

def askQuestion_YorN(question):
    result = False
    while result == False:
        result = askQuestion_string(question).lower()
        if result != "y" and result != "n":
            print("Valid answers are either Y or N please type clearly.")
            result = False
    return result

def ContinueProcessing(generic):
    try:
        generic.index('*')
    except:
        return False
    print(generic)
    answer = askQuestion_YorN("Does this look like a suitable replacement scheme?")
    if answer == "n":
        exit()
    return True

def convertSuffixIndexToPrefix(file, index):
    length = len(file)
    return length - index

def createGeneric(file, indexes):
    arr = split(file)
    for i in range(len(arr)):
        if i < indexes[0]:
            arr[i] = "*"
        elif i >= convertSuffixIndexToPrefix(file, indexes[1]):
            arr[i] = "*"
    
    return convert(arr)

def process():
    root = fetchPath()
    alldirs = listDirs(root)
    if len(alldirs) == 0:
        alldirs = [ root ]

    for dir in alldirs:
        if debug ==True:
            print(dir)
        files = listFilenames(dir)
        files_noext = removeFileExtensions(files)
        indices = analyseFilenames(files_noext)
        # Folder with less than 2 files
        if len(indices) == 0:
            continue
        # Check
        if debug ==True:
            answer = ContinueProcessing(createGeneric(files_noext[0], indices))
            if answer == True:
                renameFiles(dir, indices)
        else:
            renameFiles(dir, indices)

if askQuestion_YorN("Debug run: ") == "y":
    debug = True
else:
    debug = False
rootfolder = fetchPath()
process()