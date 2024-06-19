#!/usr/bin/python3

import sys
import csv
from pathlib import Path
import pcbnew

gUNIT = "mil"
#gUNIT = "mm"

gSCALE = 1000000

gROWSTART = 5

gCOLREF = 0
gCOLDEVICETYPE = 1
gCOLVALUE = 2
gCOLTOL = 3
gCOLPACKAGE = 4
gCOLPOSX = 5
gCOLPOSY = 6
gCOLROTATE = 7
gCOLMIRROR = 8

class Component:
    ref = ""
    type = ""
    value = ""
    tol = ""
    package = ""
    posX = 0
    posY = 0
    rotate = 0
    mirror = "NO"

def fromMil(value):
    return int(float(value)*gSCALE*0.0254)

def normalizeUnit(value):
    retVal = 0
    if gUNIT == "mm":
        retVal = float(value) * gSCALE
    if gUNIT == "mil":
        retVal = fromMil(value)
    return retVal

def parseCsvFile(file):
    datafile = open(file)
    datareader = csv.reader(datafile, delimiter=';')
    components = []
    begin = False
    for row in datareader:
        if row[0] == "REFDES":
            begin = True
            continue

        if begin:
            comp = Component()
            comp.ref = row[gCOLREF]
            comp.type = row[gCOLDEVICETYPE]
            comp.value = row[gCOLVALUE]
            comp.tol = row[gCOLTOL]
            comp.package = row[gCOLPACKAGE]
            comp.posX = normalizeUnit(row[gCOLPOSX])
            posY = 500 - float(row[gCOLPOSY])
            comp.posY = normalizeUnit(posY)
            comp.rotate = int(row[gCOLROTATE])
            comp.mirror = row[gCOLMIRROR]
            components.append(comp)
    return components

def main(boardFile, csvFile):
    board = pcbnew.LoadBoard(boardFile)
    #for fp in list(board.GetFootprints()):
    #    print(f"{fp.GetReference()} {fp.GetPosition()}")

    csvComponents = parseCsvFile(csvFile)
    errorList = []
    for comp in csvComponents:
        print(f"Processing component: {comp.ref}")
        mod = board.FindFootprintByReference(comp.ref)
        if mod:
            print(f"\tFound {comp.ref} in board")
            mod.SetX(comp.posX)
            mod.SetY(comp.posY)
            rotate = comp.rotate            

            if comp.mirror == "YES":
                mod.Flip(mod.GetPosition(), False)   

            if rotate == 270:
                rotate = -90
            mod.SetOrientationDegrees(rotate) 

            print(f"\t Applying: {comp.ref, comp.type, comp.value, comp.tol, comp.package, comp.posX, comp.posY, comp.rotate, comp.mirror}")        
        else:
            errorList.append(f"Error {comp.ref} not found in board")
            print(f"\tError {comp.ref} not found in board")    

    outFilename = Path(boardFile).stem + "-1.kicad_pcb"
    print(f"Saving PCB to {outFilename}")
    pcbnew.SaveBoard(outFilename, board)

    if len(errorList) == 0:
        print("No errors were encountered, files processed succesfully.")
    else:
        print("Following errors were detected during processing files.")
        for e in errorList:
            print(f"\t{e}")

boardFile=sys.argv[1]
csvFile=sys.argv[2]

main(boardFile, csvFile)