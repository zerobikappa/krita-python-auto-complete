import glob, os, re  #re allows for regular expression patterns
generatorVersion = 0.1
# SETUP
# ---------------------------
# change current directory to the libkis folder in the krita source code
# this is where all the python API files are at that we will read
#os.chdir("C:\\dev\\krita\\libs\\libkis")  # possible Windows OS dir. need to have two "\" symbols
# os.chdir("/home/scottpetrovic/krita/src/libs/libkis")

import tempfile
import imp
from importlib.machinery import SourceFileLoader
from tkinter.filedialog import askdirectory
from tkinter.messagebox import askyesno
kritaHomeDir =  ""
savedConfig = tempfile.gettempdir()+"/kritaHomeDirSave.py"
if os.path.isfile(savedConfig):
    isToLoadSavedConfig = askyesno("use previous config", f"Krita source path config was found in {savedConfig}, would you like to use it?")
    if isToLoadSavedConfig:
#        m = imp.load_source("myModule", savedConfig)
        m = SourceFileLoader("myModule", savedConfig).load_module()
        kritaHomeDir = getattr(m, "kritaHomeDir")
        del m

if kritaHomeDir.__len__() == 0:
    kritaHomeDir = askdirectory(title="choose the directory of Krita source code:")
    if os.path.isdir(kritaHomeDir):
        print(f"kritaHomeDir = {kritaHomeDir}")
        exportSaveConfigFile = open(savedConfig, "w")
        exportSaveConfigFile.write(f"kritaHomeDir = \"{kritaHomeDir}\"")
        exportSaveConfigFile.close()
    else:
        print(f"kritaHomeDir = {kritaHomeDir}, not a vaild path")
        quit(1)
#kritaHomeDir is an apprioporite path where your Krita source code is.
# Note that you need to have the actual source code & not a prebuilt version of Krita. THIS DIRETORY SHOULD HAVE THE CMakeLists.txt FILE directly in it

kritaLibLibKisPath = f"{kritaHomeDir}/libs/libkis"


cwd = os.getcwd()
moduleDestinationPath = fr"{cwd}/output".replace('\\', '/') # Where to store the output module

import os
import glob

packageDestinationPath = moduleDestinationPath + '/pyKrita'
import shutil
try:
    shutil.rmtree(packageDestinationPath)
except:
    pass
# raise ""
# files = glob.glob(packageDestinationPath + '/*')
# for f in files:
#     os.remove(f)
moduleDestinationPath = packageDestinationPath + '/src/krita'
setupPyFilePathIncludingFileNameAndExtension = packageDestinationPath + '/setup.py'
os.chdir(kritaLibLibKisPath)



# YOU SHOULDN'T HAVE TO TOUCH ANYTHING BELOW HERE
#----------------------------------------------

# create new file to save to. "w+" means write and create a file. saves in directory specified above
os.makedirs(f"{moduleDestinationPath}", exist_ok=True)

exportFile = open(f"{moduleDestinationPath}/__init__.py", "w+")

# a bit of a readme for what this does
exportFile.write(f"""
# Auto-generated file that reads from H files in the libkis folder
# The purpose is to use as auto-complete in Python IDEs 

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


""")


# sort header files according to dependence
headerFilelist = glob.glob("*.h")
d = { key: [] for key in headerFilelist}
for file in headerFilelist:
    currentFile = open(file)
    allFileLines = currentFile.readlines()
    for line in allFileLines:
        if line.__contains__("#include"):
            includeFile = line.replace("#include", "").replace("\"", "").replace("\n", "").strip()
            if headerFilelist.__contains__(includeFile):
                d[file].append(includeFile)
            includeFile = ""

headerFilelist2 = []

while d.__len__() > 0:
    beforeLen = d.__len__()
    for key1 in d.keys():
        if d[key1].__len__() == 0:
            headerFilelist2.append(key1)
            for key2 in d.keys():
                while d[key2].__contains__(key1):
                    d[key2].remove(key1)
            del d[key1]
            break
    if d.__len__() == beforeLen:
        print("cycle exists!")
        print(f"headerFilelist = ${headerFilelist}")
        print(f"headerFilelist2 = ${headerFilelist2}")
        quit()

# grab all h files and iterate through them
#for file in glob.glob("*.h"):
for file in headerFilelist2:
    currentFile = open(file)


    exportFile.write("\n# auto-generated from: "  +  currentFile.name   +   " \n" )

    allFileLines = currentFile.readlines() # readlines creates a list of the lines
    #exportFile.write(allFileLines[1])

    # remove all empty lines
    tempSaveLines = list()
    for line in allFileLines:
        if line.strip().__len__() == 0:
            continue
        else:
            tempSaveLines.append(line)
    allFileLines = tempSaveLines
    del  tempSaveLines

    # if function has too many arguments and some of arguments was splited to the next line
    tempSaveLines = list()
    for i in range(0, allFileLines.__len__() - 1):
        if allFileLines[i].strip()[-1] == ',' and allFileLines[i].count('(') > allFileLines[0].count(')'):
            allFileLines[i+1] = allFileLines[i].replace("\n", "").strip() + allFileLines[i+1].strip()
        else:
            tempSaveLines.append(allFileLines[i])

    allFileLines = tempSaveLines
    del tempSaveLines


    # find all classes that need to be exported
    classPattern = re.compile("KRITALIBKIS_EXPORT")

    lineWithClassFile = -1 # used later to also help with finding class comments

    # in a .h file, this will grab what class things are a part of
    for i, line in enumerate(allFileLines):

        for match in re.finditer(classPattern, line):

            lineWithClassFile = i

            # first order of business is to get the class name from the file
            # currently only one class per file, so this will probably
            # break if there are more
            bracesPrecursor = ""

            # sometimes braces are cuddled and have stuff in it

            if len(allFileLines[i]) <= 2:
                lineWithClassFile = lineWithClassFile - 1

            bracesPrecursor = allFileLines[lineWithClassFile]
            className = bracesPrecursor.split(' ')[2]

            if className[-1] == ":":
                className = className[:-1]
            if className[-1] == "\n":
                className = className[:-1]

            # start getting the format ready for the class
            exportFile.write("class " + className + ":\n")




    # now let's find the comments that exist for the class and append it to the botom
    #after we find the lines that have the class comments, we can concatenate the lines and clean them up

    # we are now checking the next 3 lines above to see if there are comments for the class
    # if there aren't don't try to grab the comments later
    classCommentsEnd = -1
    if "*/" in allFileLines[lineWithClassFile]:
        classCommentsEnd = lineWithClassFile

    if "*/" in allFileLines[lineWithClassFile - 1]:
            classCommentsEnd = lineWithClassFile - 1

    if "*/" in allFileLines[lineWithClassFile - 2]:
        classCommentsEnd = lineWithClassFile - 2


    # if we see some comments for the class, so try to read them...
    indentspace0 = ''
    indentspace4 = '    '
    indentspace8 = '        '
    indentspace = ''
    if classCommentsEnd != -1:

        classCommentsStartIndex = -1

        for a in range(classCommentsEnd, 0, -1 ) :   #go in decreasing order
            if "/*" in allFileLines[a]:
                classCommentsStartIndex = a
                break


        if classCommentsStartIndex != -1:
            classCommentsStart = classCommentsStartIndex + 1
            classCommentsOutput = "" # concatenate everything in here for the comments

            for x in range (classCommentsStart, classCommentsEnd ):
                classCommentsOutput +=  allFileLines[x].strip() + "\n   "

            classCommentsOutput = classCommentsOutput.replace("*", "")
        else:
            classCommentsOutput = "Trouble Parsing class comments"
        indentspace = indentspace4
    else:
        classCommentsOutput = "Class not documented"
        indentspace = indentspace0



    exportFile.write(f"{indentspace}\"\"\" " +  classCommentsOutput   +  "    \"\"\""  +   "\n\n")





    # 2nd thing to do.....find the functions for the class
    # find all the functions and output them.
    # need to add some spaces for proper indenting
    # this just looks for things that have () and

    #we save the line of the previous function to get exactly range between signatures of the methods
    previousFunctionLineNumber = -1
    isInBlockComment = False
    fnPattern = re.compile("\(.*\)")
    for j, line in enumerate(allFileLines):
        if line.__contains__('*/'):
            isInBlockComment = False

        if isInBlockComment:
            continue

        if line.__contains__('/*'):
            isInBlockComment = True

            line = line[:(line.find('/*')-1)]
        

        line  = line.strip() # strip white beginning and trailing white space

        def removeCharactersWithinLimiters(input: str, limitBegin: str, limitEnd) -> str:
            output: str = ""

            areWeWithinLimiters = False
            i = -1
            for char in input:
                i += 1
                if char == limitBegin:
                    areWeWithinLimiters = True
                    continue
                if char == limitEnd:
                    areWeWithinLimiters = False
                
                if not areWeWithinLimiters:
                    output += char
            return output
            
        line = removeCharactersWithinLimiters(line, '<', '>')

        for match in re.finditer(fnPattern, line):
            if line.strip()[0][0] != "*": # this means it is part of a comments

                #these aren't functions we can call

                if "Q_" not in line and "~" not in line and "operator" not in line:

                    # if we made it this far that means we are a valid function
                    # now we need to figure out how to parse this and format it for python
                    isVirtual = False
#                    returnType = "void"
                    returnType = "None"
                    isExplicit = False
                    isStatic = False

                    functionLineNumber = j
                    functionList = line.split("(")[0]
                    functionList = functionList.replace("*", "").replace("const", "").replace(">", "")

                    if "virtual" in functionList:
                        isVirtual = True
                        functionList = functionList.split("virtual")[1]

                    if "explicit" in functionList:
                        isExplicit = True
                        functionList = functionList.split("explicit")[1]

                    if functionList.strip()[0:7] == "static ":
                        isStatic = True
                        functionList = functionList.split("static")[1]
                    


                    functionList = functionList.strip() # extra spaces at the beginning need to be removed

                    #first word is usually the return type
                    if " " in functionList:
                        returnType = functionList.split(' ')[0]
                        if returnType == "void":
                            returnType = "None"
                        elif returnType == "QString":
                            returnType = "str"
                        elif returnType == "QList":
                            returnType = "list"
                        functionList = functionList.split(' ')[1]

                    if functionList.__len__() < 1:
                        continue
                    if functionList[0] == '=':
                        continue


                    # save off the parameters elsewhere as we have to parse each differently
                    # we need to clean it up a bit since it is loose and doesn't need variable names and types. we will just keep the types
                    paramsList = "(" + line.split("(")[1]
                    paramsList = paramsList.replace("const", "").replace("&", "").replace("*", "").replace(";", "").replace("override", "") # remove const stuff
                    paramsList = paramsList.replace("(", "").replace(")", "").strip()

                    # clean up parameters with multiple
                    class ParamTypeAndName:
                        name: str = ""
                        type: str = ""
                    listOfParamTypesAndNames: list[ParamTypeAndName] = []
                    longestParamName = 0
                    if True:
                    # if "," in paramsList:

                        multipleParamsList = []
                        if paramsList.__contains__(','):
                            paramsListSplit = paramsList.split(",")
                        else:
                            paramsListSplit = [paramsList]

                        # break it apart and clear everything after the first word
                        for p in paramsListSplit:
                            print(p)
                            try:
                                splittedStr = p.strip().split(" ", 1)
                                print(f"splittedStr {splittedStr}")
                                if splittedStr[1].__contains__('='):
                                    parameterName = splittedStr[1][:((splittedStr[1].find('=')))].strip()
                                else:
                                    parameterName = splittedStr[1]
                                parameterType = splittedStr[0]
                                print(f"splittedStr: {splittedStr}")
                                multipleParamsList.append(f"{parameterName}")
                                paramTypeAndName = ParamTypeAndName()
                                paramTypeAndName.name = parameterName
                                paramTypeAndName.type = parameterType
                                listOfParamTypesAndNames.append(paramTypeAndName)
                                longestParamName = max(parameterName.__len__(), longestParamName)
                                # multipleParamsList.append(f"{parameterName}: {splittedStr[0]}") # @todo Make sure all types are declared in Python, currently we cant type hint
                                # due to the actual types never being declared.
                                
                            except Exception as exception:
                                print(f"Paramsplitting error -> {exception} <- for '{p}' in {paramsList} in '{line}' in {file}")
                                # raise exception
                                

                        paramsList = ",".join(multipleParamsList )

                    elif paramsList != "":
                        paramsList = paramsList.strip().split(" ")[0]
                        #Only one parameter. remove everything after the first word
#                    if paramsList.__len__() < 2:
#                        continue

                    if isStatic:
                        exportFile.write(f"{indentspace}@staticmethod\n")

                    exportFile.write(f"{indentspace}def " + functionList + "(" + paramsList + "):\n")





                    # now let's figure out what comments we have. we figured out the return type above. but we need to scrape the h file for comments
                    #functionLineNumber
                    functionCommentsEnd = functionLineNumber - 1
                    functionCommentsStartIndex = previousFunctionLineNumber

                    for b in range(functionCommentsEnd, functionCommentsStartIndex+1, -1 ) :   #go in decreasing order
                        if "/*" in allFileLines[b]:
                            functionCommentsStartIndex = b
                            break

                    if functionCommentsStartIndex != -1:
                        classCommentsStart = classCommentsStartIndex +1 # first line just has "/*", so we can skip that

                        functionCommentsOutput = "" # concatenate everything in here for the comments
                        for x in range (functionCommentsStartIndex, functionCommentsEnd ):
                            functionCommentsOutput +=  allFileLines[x].strip()

                            functionCommentsOutput = functionCommentsOutput.replace("*", "").replace("/ ", "")
                    else:
                        functionCommentsOutput = "Missing function documentation"
                    longestParamName = max(longestParamName, 'return'.__len__())
                    def formatParamForDocString(paramName: str, paramType: str) -> str:
                        formatParamForDocStringSpacing = ""
                        i9 = -1
                        while i9 < longestParamName - paramName.__len__():
                            i9 += 1
                            formatParamForDocStringSpacing += " "
                        return f"\n{indentspace8}{paramName}: {formatParamForDocStringSpacing}{paramType}"
                    # finally export the final file
                    # listOfParamTypesAndNames.reverse()
                    parameterPartOfComment = ""
                    for param in listOfParamTypesAndNames:
                        parameterPartOfComment = f"{parameterPartOfComment}{formatParamForDocString(param.name, param.type)}"
                    newLine = '\n'
                    
                    functionCommentsOutput = f"{newLine}{indentspace8}{functionCommentsOutput}{newLine}{indentspace8}{parameterPartOfComment}{formatParamForDocString('return', returnType)}{newLine}"
                        
                    exportFile.write(f"{indentspace8}\"\"\" " + functionCommentsOutput + f"{indentspace8}\"\"\"\n" )
                    exportFile.write(f"{indentspace8}return {returnType}\n\n" )




    # file is done. add some spacing for readability
    exportFile.write("\n")


    # close the file that we are done with it
    currentFile.close()

# exportFileAsStr = exportFile.__str__()
# exportFileAsListOfStringsWhereEachStringRepresentsALine: list[str] = exportFileAsStr.split('\n')
# exportFileAsStrFINAL = ""
# newLine = '\n'
# for line in exportFileAsListOfStringsWhereEachStringRepresentsALine:
#     if line.__contains__('#include'):
#         continue
#     exportFileAsStrFINAL += f"{line}{newLine}"
exportFile.close()


