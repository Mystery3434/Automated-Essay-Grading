#!/usr/bin/env python
import tika
tika.initVM()
from tika import parser
from tika import language
import sys
import time
import os
import logging

def main(
    filename="",
    filepath="",
    newname="",
):
    if not os.path.exists(filepath):
        logging.warn(f'filepath not found: {filepath}\n')
        raise Exception("filepath not found")

    #Perform File Validation
    ftype = filetype(filepath)
    fsize = filesize(filepath)
    logging.warn(f'{ftype}, {fsize}')

    if (ftype==False):
        print("File type is not supported")
        sys.exit()
    elif(fsize==False):
        print("File size is too big")
        sys.exit()
    else:
        #Parse data from file
        raw = parser.from_file(filepath)
        #Get files text content
        text = raw['content']
        text = text.strip('\n')
        print(raw['metadata'])
        logging.warn(f"raw['metadata']: {raw['metadata']}")

        #Remove new lines between lines in pdf
        #Remove page numbers in pdf
        if filepath.endswith('.pdf'):
            textlist = text.split('\n\n')
            print(text)
            for j in range(1, int(raw['metadata']['xmpTPg:NPages'])+1):
                for i in range(0, len(textlist)):
                    if textlist[i] == (str(j)+" \n "):
                        textlist[i]=""
            for k in range(0, len(textlist)):
                if textlist[k] == " ":
                    textlist[k] = "\n\n"
            text = ""
            text = text.join(textlist)

        #Remove Page Numbers in Word
        if filepath.endswith('.docx'):
            textlist = text.split('\n')
            print(textlist)
            for i in range(0, len(textlist)):
                if textlist[i] == ("2"):
                    textlist[i]=""
            text = ""
            text = text.join(textlist)
        ts = time.strftime("%Y%m%d-%H%M%S")
        output = open("/home/flask/app/output_files/{}_converted.txt".format(ts+".txt"), "w+",encoding="utf-8")
        output.write(text)
        output.close()

        return text
    return None

#Check if file type is supported
def filetype(filepath):
    if filepath.endswith('.pdf') or filepath.endswith('.txt') or filepath.endswith('.docx'):
        return(True)
    else:
        return(False)

#Check if file size is within bounds (<4MB)
def filesize(filepath):
    if(os.stat(filepath).st_size < 4000000):
        return(True)
    else:
        return(False)


if __name__ == "__main__":
    for i in range(1, len(sys.argv)):
        filepath = str(sys.argv[i])
        main(
            filename="",
            filepath=filepath,
            newname="",
        )
