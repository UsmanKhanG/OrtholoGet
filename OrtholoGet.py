import requests, sys, json
from pprint import pprint
import os
from os import path
import tkinter as tk
def setSymbol(symbol):
    global geneName 
    geneName = symbol
def setSpecies(speciesName):
    global species 
    species = speciesName
def saveToFolder():
    for i in range(len(speciesList)):
        if intVarList[i].get():
            if not path.exists(speciesList[i]+'_'+geneName+'.fasta'):
                createRefSeqFile(align_seqList[i],speciesList[i]+'_'+geneName)
            else:
                createRefSeqFile(align_seqList[i],speciesList[i]+'_'+geneName+str(i))
def fetchURI(server, request, contentType):
    r = requests.get(server+request, headers={ "accept" : contentType})
    # Response 200 means request is ok
    # Response 400 means bad request (cannot be processed)
    # If The result from the endpoint is a .json, we have to do parse the data with a .json() function
    print(r)
    if contentType == 'application/json':
        # Returns the data of the response and returns the response to see its response code
        return (r.json(), r)
    else:
        return (r.text, r)
def getOrthologBySymbol(server, symbol):
    contentType = "application/json"
    lookupExt = "/homology/symbol/" + species + '/' + symbol + '?' + contentType  
    orth = fetchURI(server, lookupExt, contentType)
    return orth[0]
def createRefSeqFile(inputString, filename):
    # Create the file, write the contents with the sequence, save as fasta (standard format for sequence data)
    seqFile=open(filename+'.fasta', 'w+')
    seqFile.write('>'+filename+'\n'+inputString)
    seqFile.close()

root = tk.Tk()
root.title('OrtholoGet')
root.geometry("800x600")

def main():
    
    setSpecies(speciesEntry.get())
    setSymbol(symbolEntry.get())
    tempFrame.destroy()
    path = os.getcwd()

    frame = tk.Frame(root,borderwidth=5,relief='groove')
    frame.place(relx=0.1, rely=0.1, relwidth=0.8, relheight=0.8)

    sb = tk.Scrollbar(frame,orient='vertical')
    text = tk.Text(frame,width=40,height=20, yscrollcommand=sb.set, borderwidth=0)
    sb.config(command=text.yview)
    sb.pack(side='right', fill='y')
    text.pack(side='left',fill='both' ,expand=True)

    saveButton = tk.Button(root, text='Save', padx=10,pady=5,fg='white', bg='gray', command=saveToFolder)
    saveButton.pack(side='bottom')

    path+= "/data" + "_" + geneName
    try:
        os.mkdir(path)
    except OSError:
        print("Creation of the directory %s failed " % path)
    else:
        print("Sucessfully created the directory %s" % path)

    os.chdir(path)

    data = getOrthologBySymbol("http://rest.ensembl.org", geneName)['data']
    homologies = data[0]['homologies']
    # pprint(homologies)
    # Parallel lists
    global speciesList
    global align_seqList
    global intVarList
    speciesList = []
    align_seqList = []
    firstHomology = homologies[0]
    source = firstHomology['source']
    species = source['species']
    align_seq = source['align_seq']
    createRefSeqFile(align_seq, species+'_'+geneName+'_source')
    for ortholog in homologies:
        # pprint(ortholog)
        source = ortholog['target']
        species = source['species']
        align_seq = source['align_seq']
        print(species, ':', align_seq, '\n')
        speciesList.append(species)
        align_seqList.append(align_seq)
        # createRefSeqFile(align_seq, species+'_'+geneName)
    intVarList = []
    for i in range(len(speciesList)):
        var = tk.IntVar()
        cb = tk.Checkbutton(text = speciesList[i], variable=var)
        intVarList.append(var)
        text.window_create("end", window=cb)
        text.insert('end', '\n')
    
    # homologies = data['homologies']
    # pprint(homologies)

tempFrame = tk.Frame(root, borderwidth=0, relief ='sunken')
tempFrame.place(relx=0.2, rely=0.2, relwidth=0.6, relheight=0.6)

symbolEntry = tk.Entry(tempFrame, width = 50)
symbolEntry.pack(side = 'top')
symbolEntry.insert(0, 'Please enter the Gene name/symbol')

speciesEntry = tk.Entry(tempFrame, width = 50)
speciesEntry.pack(side = 'top')
speciesEntry.insert(0, 'Please enter the species name')

searchButton = tk.Button(tempFrame, text = 'Search', padx=10,pady=5, fg='white', bg='gray', command=main)
searchButton.pack()


root.mainloop()