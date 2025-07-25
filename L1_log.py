# This program contains functions for logging robot parameters to local
# files. The files can be accessed by NodeRed or other programs.
# Nodered can be found by browsing to port 1880 on the shared network AP. ie, 192.168.8.1:1880
# This program works on SCUTTLE with any CPU.

# Import external libraries
import csv      # for handling comma-separated-values file type

# A function for populating 2 text files with updated phi-dots
def writeFiles(current_phis):
    txt = open("/home/debian/basics/PDL.txt", 'w+')         # file for phi dot left
    txt2 = open("/home/debian/basics/PDR.txt", 'w+')        # file for phi dot right
    phi_dotL = round(current_phis[0], 1)
    phi_dotR = round(current_phis[1], 1)
    txt.write(str(round(phi_dotL, 1)))
    txt2.write(str(round(phi_dotR, 1)))
    txt.close()
    txt2.close()


# A function for populating 2 text files with updating variables
def NodeRed2(values):                                       # this function takes a 2-element array called val
    txt = open("/home/debian/basics/a.txt", 'w+')           # file for generic variable a
    txt2 = open("/home/debian/basics/b.txt", 'w+')          # file for generic variable b
    a = round(values[0], 2)
    b = round(values[1], 2)
    txt.write(str(a))
    txt2.write(str(b))
    txt.close()
    txt2.close()


# A function for sending 1 value to a log file of specified name
def uniqueFile(value, fileName):                            # this function takes a 2-element array called val
    txt = open("/home/debian/basics/" + fileName, 'w+')     # file with specified name
    myValue = round(value, 2)
    txt.write(str(myValue))
    txt.close()


# A function for sending 1 value to a log file in a temporary folder
def tmpFile(value, fileName):                               # this function takes a 2-element array called val
    txt = open("/tmp/" + fileName, 'w+')                    # file with specified name
    myValue = round(value, 2)
    txt.write(str(myValue))
    txt.close()
    
    
# A function for saving a single line string to a log file in a temporary folder
def stringTmpFile(myString, fileName):     # this function takes a string and filename
    txt = open("/tmp/" + fileName, 'w+')   # file with specified name
    txt.write(myString)                    # by default the existing txt is overwritten
    txt.close()


# A function for creating a CSV file from a list of values.
def csv_write(list):
    list = [str(i) for i in list]
    with open('/tmp/excel_data.csv', 'a') as csvFile:
        writer = csv.writer(csvFile)
        writer.writerow(list)
    csvFile.close()

# A function for creating a row in a csv file
def csv_row(list):
    row = list.join(",")
    with open('/tmp/excel_data.csv', 'a') as csvFile:
        writer = csv.writer(csvFile)
        writer.writerow(row)
    csvFile.close()

# A function to clear an existing CSV file
def clear_file():
    open('excel_data.csv', 'w').close()