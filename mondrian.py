#Upon further research, I decided to use tkinter instead of jupyter, as it better fits my needs.
import sys
import tkinter as tk
from tkinter import filedialog
import csv

#Erases all table visuals to make way for updates
def clearTables():
    for widget in singleTable.winfo_children():
        widget.destroy()
    for widget in totalTable.winfo_children():
        widget.destroy()
        
#Return how many CSVs have values at a point r,c
#If the point is out of bounds for every CSV, return -1
def oddsOfValue(r,c):
    #Avoid divide by 0
    if len(storedCSVData) == 0:
        return 0
    has = 0
    inBounds = False
    for data in storedCSVData:
        if (r < len(data)) and (c < len(data[r])):
            inBounds = True
            if (data[r][c]):
                has = has + 1
    if (not inBounds):
        return -1
    return has/len(storedCSVData)
        
#Hold any new CSVs and their data into the global varaibles
def updateCSVs(filepath, data):
    #Skip duplicates
    if (filepath in storedCSVs):
        return
    storedCSVs.append(filepath)
    storedCSVData.append(data)
    findRegions()

#The bread and butter of this program
#Seperate into square regions
def findRegions():
    global regionData
    regionData = {}
    regionNumber = 0

    row = 0
    col = 0
    while(oddsOfValue(row, col) >= 0):
        print(1)
        while(oddsOfValue(row, col) >= 0):
            if oddsOfValue(row, col) <= 0:
                col = col + 1
                continue
            if (row, col) in regionData:
                col = col + 1
                continue

            #Find rectangle starting from (row, col)
            r = row
            c = col
            # Expand down first
            end_row = r
            while oddsOfValue(end_row + 1, c) > 0:
                end_row += 1

            #Expand downward for width
            end_col = c
            #Check for a high majority to account for bad data
            while True:
                avg = 0
                maxOdds = oddsOfValue(r, c)
                for rr in range (row, end_row + 1):
                    avg = avg + oddsOfValue(rr, end_col + 1)
                    #This is to consider large groups of "new"  cells
                    maxOdds = max(maxOdds, oddsOfValue(rr, end_col + 1))
                avg = avg / (end_row + 1 - row)
                if (avg >= 0.75 * maxOdds):
                    end_col += 1
                else:
                    break

            #Lable Region
            for rr in range(r, end_row + 1):
                for cc in range(c, end_col + 1):
                    regionData[(rr, cc)] = regionNumber
                    print(f"Added [{rr}, {cc}] to region {regionNumber}")

            col = col + 1
            regionNumber = regionNumber + 1
            print(2)
        col = 0
        row = row + 1
    return

#Return a coloring based on the region.
def applyGroupColoring(row, col, value):
    if (oddsOfValue(row, col) > 0):
        colors = [(255, 0, 0),(0, 255, 0),(0, 0, 255),(255, 255, 0),(255, 0, 255),(0, 255, 255), (125, 255, 0), (125, 0, 255), (255, 125, 0), (0, 125, 255), (255, 0, 125), (0, 255, 125)]
        r = colors[regionData.get((row,col), 0) % 6][0]
        g = colors[regionData.get((row,col), 0) % 6][1]
        b = colors[regionData.get((row,col), 0) % 6][2]
        #Decoloring regions that aren't exact matches with each other.  NOT DONE in the original paper!, but I thought it would be a neat touch.
        r = int(r + (255 - r) * (1 - oddsOfValue(row, col)))
        g = int(g + (255 - g) * (1 - oddsOfValue(row, col)))
        b = int(b + (255 - b) * (1 - oddsOfValue(row, col)))
        return f"#{r:02x}{g:02x}{b:02x}"
    return "white"

#Change the tables to reflect an update.
def updateVisuals(data):
    clearTables()
    for r, row in enumerate(data):
        for c, value in enumerate(row):
            bg = applyGroupColoring(r, c, value)
                
            labelS = tk.Label(singleTable, text=value, borderwidth=1, relief="solid", bg=bg)
            labelS.grid(row=r, column=c, sticky="nsew", padx=0, pady=0)
            
            labelT = tk.Label(totalTable, text="     ", borderwidth=1, relief="solid", bg=bg)
            labelT.grid(row=r, column=c, sticky="nsew", padx=0, pady=0)

#Read the CSV and apply update functions
def openCSV(filepath):
    with open(filepath, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        data = list(reader)
        updateCSVs(filepath, data)
        updateVisuals(data)

#Load and store a CSV
def loadCSV():
    filepath = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if not filepath:
        print("Error reading file at loadCSV(), filepath is " + str(filepath))
        return
    openCSV(filepath)

#Create a scrollable frame
def scrollFrame(parent):
    canvas = tk.Canvas(parent)
    canvas.grid(row=0, column=0, sticky="nsew")

    parent.grid_rowconfigure(0, weight=1)
    parent.grid_columnconfigure(0, weight=1)

    scrollbarV = tk.Scrollbar(parent, orient="vertical", command=canvas.yview)
    scrollbarV.grid(row=0, column=1, sticky="ns")
    scrollbarH = tk.Scrollbar(parent, orient="horizontal", command=canvas.xview)
    scrollbarH.grid(row=1, column=0, sticky="ew")
    
    canvas.configure(yscrollcommand=scrollbarV.set, xscrollcommand=scrollbarH.set)
    scrollFrame = tk.Frame(canvas)
    
    canvas.create_window((0, 0), window=scrollFrame, anchor="nw")
    
    def on_frame_configure(event):
        canvas.configure(scrollregion=canvas.bbox("all"))
    scrollFrame.bind("<Configure>", on_frame_configure)
    
    return scrollFrame, canvas

#Global Variables
storedCSVData = []
storedCSVs = []
regionData = {}
    
#UI Setup
root = tk.Tk()
root.title("Mondrian Spreadsheet Viewer")
root.geometry("1000x600")

leftFrame = tk.Frame(root, bd =2, relief = "solid")
rightFrame = tk.Frame(root, bd = 2, relief = "solid")

leftFrame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
rightFrame.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
    
singleTable, singleTableCanvas = scrollFrame(leftFrame)
totalTable, totalTableCanvas = scrollFrame(rightFrame)

loadBTN = tk.Button(root, text="Load CSV", command=loadCSV)
loadBTN.grid(row=1, column=0, pady=10)

root.grid_rowconfigure(0, weight=4)
root.grid_rowconfigure(1, weight=1)
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)
    
#Keep Window Open
root.mainloop()