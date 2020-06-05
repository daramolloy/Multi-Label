import tkinter as tk
#from tkinter import *
from tkinter import ttk, filedialog
from PIL import ImageTk, Image, ImageGrab, ImageDraw 
import math
import os
import numpy as np


class App(tk.Tk): 
    def __init__(self): 
        super().__init__() 
        
        self.addMenu()

        self.canvas = tk.Canvas(self, width=0, height=0)
        #self.protocol("WM_DELETE_WINDOW", self.canvas)
        self.canvas.grid(row = 1, column = 3,columnspan=8, rowspan=8, sticky = "n", pady = 2,padx = 2)
        #self.attributes("-fullscreen", True)
        # print(self.winfo_screenwidth())
        self.canvas.config(cursor="cross",relief="ridge")
        
        self.sourceSel = tk.IntVar()
        self.canvas.old_mask_coords = None
        self.canvas.origin_box_coords = None
        self.canvas_tmp_box = None
        self.canvas_tmp_poly = None
        self.canvas_tmp_poly_origin = None
        self.clicked = False
        self.boxingOk = False
        
        self.editedItemTag = None
        self.editingBox = None
        self.editingPoly = None
        self.vertices = []
        self.tmpCoords = []
        self.indexTempCoords = None
        
        self.zoomEnable = False
        self.zoomBox = None
        self.zImg = None
        self.zCanvasImg = None
        self.zoomFactor = 1
        
        
        self.masksVisible = True
        
        self.images = []
        self.polygons = []
        self.boxes = []
        self.currentMask = []
        self.objects = []
        
        self.dispList = []
        self.currSource = [r"test_imgs","","",""]
        self.originalFrame =  "dub.jpg"
        self.currFrame = self.originalFrame
        
        self.currClass = None
        self.mode = "box"
        self.color = "blue"
        
        
        self.loadButtons()   
        self.loadClasses() 
        self.loadImg()
        
        self.onCanvas = False
        
        
        self.canvas.bind("<Enter>",self.startAnnotating)
        self.canvas.bind("<Leave>",self.stopAnnotating)
        
        
        self.bind('<Motion>', lambda event, point="motion": 
                            self.boxing(event,point))
        self.bind('<ButtonPress-1>', self.mouseClicked)
        self.bind('<ButtonRelease-1>', self.mouseClicked)
    



    def setSizes(self):
        
        sW, sH = self.winfo_screenwidth(), self.winfo_screenheight()
        
        btnColSize = sW*(1/15)
        #print(btnColSize)
        rowSize = sH*(1/9)
        
        col_count, row_count = self.grid_size()
        # cols = [1,2,12,13,14,15]
        for col in range(col_count):
            self.grid_columnconfigure(col, minsize=btnColSize)  
            #print(col)
        for row in range(row_count):
            self.grid_columnconfigure(row, minsize=rowSize)   
        


    def startAnnotating(self, event):
        self.onCanvas = True
        self.boxingOk = True

    def stopAnnotating(self, event):
        self.onCanvas = False
        
        
    def addMenu(self):
        
        self.menubar = tk.Menu(self)
        self.prefmenu = tk.Menu(self.menubar, tearoff=0)
        self.polygonTouch = tk.BooleanVar()
        self.polygonTouch.set(False)
        self.prefmenu.add_checkbutton(label="Polygon Touchscreen Mode", onvalue=1, offvalue=0, variable=self.polygonTouch, command=self.polyBind)
        # self.prefmenu.add_command(label="New", command="")
        # self.prefmenu.add_command(label="Open", command="")
        # self.prefmenu.add_command(label="Save", command="")
        # self.prefmenu.add_separator()
        # self.prefmenu.add_command(label="Exit", command=self.quit)
        self.menubar.add_cascade(label="Preferences", menu=self.prefmenu)
        # self.helpmenu = tk.Menu(self.menubar, tearoff=0)
        # self.helpmenu.add_command(label="Help Index", command="")
        # self.helpmenu.add_command(label="About...", command="")
        # self.menubar.add_cascade(label="Help", menu=self.helpmenu)
        self.config(menu=self.menubar)
        
        
    def loadButtons(self):
        self.addSourceBtn = ttk.Button (self,text="Add Source")
        self.rmSource = ttk.Button (self,text="Remove Source")
        self.addSourceBtn.grid(row = 1, column = 0, sticky = "nesw", pady = 5, padx = 5) 
        self.rmSource.grid(row = 1, column = 1, sticky = "nesw", pady = 5, padx = 5)
        
        self.addSourceBtn.bind("<Button-1>", self.addSource)
        self.rmSource.bind("<Button-1>", self.removeSource)


        self.zoomEnableBtn = ttk.Button (self,text="Toggle Zoom")
        self.maskEnableBtn = ttk.Button (self,text="Toggle Masks")
        self.zoomEnableBtn.grid(row = 3, column = 0,columnspan=1, sticky = "nesw", pady = 5, padx = 5) 
        self.maskEnableBtn.grid(row = 3, column = 1,columnspan=1, sticky = "nesw", pady = 5, padx = 5)
        
        self.zoomEnableBtn.bind("<Button-1>", self.zoomToggle)
        self.maskEnableBtn.bind("<Button-1>", self.maskToggle)
        
        

        self.polyBtn = ttk.Button (self,text="Polygon Creation Tool")
        self.boxBtn = ttk.Button (self,text="Box Creation Tool")
        self.polyBtn.grid(row = 5, column = 0,columnspan=2, sticky = "nesw", pady = 5, padx = 5) 
        self.boxBtn.grid(row = 4, column = 0,columnspan=2, sticky = "nesw", pady = 5, padx = 5)
        
        self.polyBtn.bind("<Button-1>", self.polyBindEvent)
        self.boxBtn.bind("<Button-1>", self.boxBind)


        self.classList = tk.Listbox(self,exportselection=0)
        self.classList.grid(row = 6, column = 0,columnspan=2, rowspan = 1, sticky = "nesw", pady = 5, padx = 5) 
        
        
        
        self.saveFrameBtn = ttk.Button (self,text="Save this Frame")
        self.saveFrameBtn.grid(row = 7, column = 0,columnspan=2, sticky = "nesw", pady = 5, padx = 5)
        
        self.saveFrameBtn.bind("<Button-1>", self.saveFrame)
        
        
        
        self.next = ttk.Button (self,text="Next (w)")
        self.previous = ttk.Button (self,text="Previous (q)")
        self.next.grid(row = 8, column = 1,columnspan=1, sticky = "nesw", pady = 5, padx = 5) 
        self.previous.grid(row = 8, column = 0,columnspan=1, sticky = "nesw", pady = 5, padx = 5)
        
        self.bind('w', self.nextFrame)
        self.bind('q', self.previousFrame)
        self.next.bind("<Button-1>", self.nextFrame)
        self.previous.bind("<Button-1>", self.previousFrame)
        
        
        self.objectList = tk.Listbox(self,exportselection=0)
        self.objectList.grid(row = 1, column = 12,columnspan=3, rowspan = 3, sticky = "nesw", pady = 5, padx = 5) 
        self.objScrollbar = tk.Scrollbar(self)
        self.objScrollbar.grid(row = 1, column = 15,columnspan=1, rowspan = 3, sticky = "nes")

        self.objectList.config(yscrollcommand=self.objScrollbar.set)
        self.objScrollbar.config(command=self.objectList.yview)
        self.objectList.bind('<<ListboxSelect>>', self.editCurrent)


        self.frameListLabel1 = ttk.Label(self,text="Source 1:")
        self.frameListLabel1.grid(row = 5, column = 12,columnspan=1, sticky = "s") 
        self.frameList1 = tk.Listbox(self,exportselection=0)
        self.frameList1.grid(row = 6, column = 12,columnspan=1, rowspan = 3, sticky = "nesw", pady = 5, padx = 5) 
        self.frameList1.bind('<<ListboxSelect>>', self.frame1Select)

        self.remapBtn = ttk.Button(self,text=">")
        self.remapBtn.grid(row=7, column=13, sticky = "nesw")
        self.remapAllBtn = ttk.Button(self,text=">>")
        self.remapAllBtn.grid(row=8, column=13, sticky = "nesw")
        
        self.remapBtn.bind("<Button-1>", self.remapOneBind)
        self.remapAllBtn.bind("<Button-1>", self.remapAllBind)
        
        self.frameListLabel2 = ttk.Label(self,text="Source 2:")
        self.frameListLabel2.grid(row = 5, column = 14,columnspan=1, sticky = "s") 
        self.frameList2 = tk.Listbox(self,exportselection=0)
        self.frameList2.grid(row = 6, column = 14,columnspan=1, rowspan = 3, sticky = "nesw", pady = 5, padx = 5) 
        self.frameList2.bind('<<ListboxSelect>>', self.frame2Select)

        
        self.frameScrollbar = tk.Scrollbar(self)
        self.frameScrollbar.grid(row = 6, column = 15,columnspan=1, rowspan = 3, sticky = "nes")

        self.frameList1.config(yscrollcommand=self.frameScrollbar.set)
        self.frameList2.config(yscrollcommand=self.frameScrollbar.set)
        self.frameScrollbar.config(command=self.frameList1.yview)
        self.frameScrollbar.config(command=self.frameList2.yview)
        
                      
        
    def zoomToggle(self,event):
        if self.zoomEnable:
            self.zoomEnable = False
        else:
            self.zoomEnable = True
        
    def maskToggle(self,event):
        if self.masksVisible:
            self.canvas.tag_raise(self.canvas.find_all()[0])
            self.masksVisible = False
        else:
            self.canvas.tag_lower(self.canvas.find_all()[len(self.canvas.find_all())-1])
            self.masksVisible = True
            
        
    def loadClasses(self):
        colour = ["blue", "red", "green", "cyan", "yellow", "magenta", "magenta", "magenta", "magenta", "magenta", "magenta"]
       	f= open("Classes.txt","r")
       	if f.mode == 'r':
           contents =f.read()
           classestxt = contents.split(',')
           for x in range(len(classestxt)):
               self.classList.insert("end",f"{classestxt[x]} -- {colour[x]}")
        self.classList.activate(0)
        self.classList.selection_set(0)
        self.currClass = self.classList.get(0)
        
        
        
    def sourceChanged(self):
        #print("source changed")
        
        if self.sourceSel.get() == 1:
            if self.frameList1.get(0):
                #print(f"2->1   B4: {self.currFrame}")
                if self.currFrame in self.frameList2.get(0, "end"): # Check if it was changed from 2 - 1 or if just called on 1 - 1
                    index = self.frameList2.get(0, "end").index(self.currFrame)
                    self.currFrame = self.frameList1.get(index)
                    self.frameList2.selection_clear(0, "end")
                    self.frameList1.selection_set(index)
                    #print(f"2->1   {index},{self.currFrame}")
            
        elif self.sourceSel.get() == 2:
            #print(f"1->2   B4: {self.currFrame}")
            if self.currFrame in self.frameList1.get(0, "end"): # Check if it was changed from 1 - 2 or if just called on 2 - 2
                index = self.frameList1.get(0, "end").index(self.currFrame)
                self.currFrame = self.frameList2.get(index)
                self.frameList1.selection_clear(0, "end")
                self.frameList2.selection_set(index)
                #print(f"1->2   {index},{self.currFrame}")
            
        self.loadImg()
        
    def firstSource(self,event):
        self.sourceSel.set(1)
        self.sourceChanged()
        
    def secondSource(self,event):
        self.sourceSel.set(2)
        self.sourceChanged()
        
        
    def addSource(self,event):
        
        self.boxingOk = False
        dataDir = filedialog.askdirectory(title = "Select Folder Containing Source")
        
        if self.currSource[1] == "":
            self.sourceList1 = ttk.Radiobutton(self,value=1, text="1:",variable = self.sourceSel, command=self.sourceChanged)
            self.sourceList1.grid(row = 2, column = 0,columnspan=2, sticky = "nesw")     
            self.bind('e',self.firstSource)
            
            self.sourceList1.config(text = f"1: {dataDir.split('/')[-1]} - (e)")
            for file in os.listdir(dataDir):
                if ".jpg" in file or ".png" in file or ".tiff" in file or ".gif" in file:
                    self.frameList1.insert("end",file)
            self.sourceSel.set(1)
            
        elif self.currSource[2] == "":
            self.sourceList2 = ttk.Radiobutton(self,value=2, text=f"2: {dataDir.split('/')[-1]} - (r)",variable = self.sourceSel, command=self.sourceChanged)
            self.sourceList2.grid(row = 2, column = 1,columnspan=2, sticky = "nesw") 
            self.bind('r',self.secondSource)
            
            for file in os.listdir(dataDir):
                if ".jpg" in file or ".png" in file or ".tiff" in file or ".gif" in file:
                    self.frameList2.insert("end",file)
            self.sourceSel.set(2)
            self.currSource[3] = filedialog.askdirectory(title = "Select Folder Containing Disparity Maps")
            for file in os.listdir(self.currSource[3]):
                if ".jpg" in file or ".png" in file or ".tiff" in file or ".gif" in file:
                    self.dispList.append(file)
            
        self.frameList1.selection_clear(0, "end")
        self.frameList2.selection_clear(0, "end")
        self.currSource[self.sourceSel.get()] = dataDir
        if self.sourceSel.get() == 1:
            self.currFrame = self.frameList1.get(0)
            self.frameList1.selection_set(0)
        elif self.sourceSel.get() == 2:
            self.currFrame = self.frameList2.get(0)
            self.frameList2.selection_set(0)
        else:
            print("No Source Selected")
            
        self.loadImg()
        self.boxingOk = True

        
        
        
        
    def removeSource(self,event):
        if self.sourceSel.get() == 1:
            if self.frameList2.size() == 0:
                self.sourceList1.config(text = f"1: ")
                self.frameList1.delete(0,"end")
                self.sourceSel.set(0)
                
                self.currFrame = self.originalFrame
                self.currSource[1] = ""
                
            else:
                newTxt = self.sourceList2.config()['text'][4][3:-3]
                self.sourceList1.config(text = f"1: {newTxt}(e)")
                self.sourceList2.destroy()
                
                self.frameList1.delete(0,"end")
                newItems = self.frameList2.get(0,"end")
                for i in newItems:
                    self.frameList1.insert("end",i)
                self.frameList2.delete(0,"end")
                
                self.sourceSel.set(1)
                self.currFrame = self.frameList1.get(0)
                self.currSource[1] = self.currSource[2]
                self.currSource[2] = ""
                self.currSource[3] = ""
                self.frameList1.selection_set(0)
                
                
        elif self.sourceSel.get() == 2:
            self.sourceList2.destroy()
            self.frameList2.delete(0,"end")
        
            self.sourceSel.set(1)
            self.currFrame = self.frameList1.get(0)
            self.frameList1.selection_set(0)
            self.currSource[2] = ""
            self.currSource[3] = ""
    
        self.loadImg()
    
    
    
    
    def frame1Select(self,event):
        
        index = self.frameList1.curselection()[0]
        
        ls = 0
        flist1 = self.frameList1.get(0,"end")
        flist2 = self.frameList2.get(0,"end")
        for item in flist1:
            if item == self.currFrame:
                ls = 1
        for item in flist2:
            if item == self.currFrame:
                ls = 2
        
        
        if ls == 1:
            self.currFrame = self.frameList1.get(index)
            self.loadImg()
        elif ls == 2:
            self.currFrame = self.frameList2.get(index)
            self.sourceSel.set(1)
            self.sourceChanged()
        
        
        
        
    def frame2Select(self,event):
        
        index = self.frameList2.curselection()[0]
        
        ls = 0
        flist1 = self.frameList1.get(0,"end")
        flist2 = self.frameList2.get(0,"end")
        for item in flist1:
            if item == self.currFrame:
                ls = 1
        for item in flist2:
            if item == self.currFrame:
                ls = 2
                
        
        if ls == 1:
            self.currFrame = self.frameList1.get(index)
            self.sourceSel.set(2)
            self.sourceChanged()
        elif ls == 2:
            self.currFrame = self.frameList2.get(index)
            self.loadImg()
            
        

    def nextFrame(self,event):
        
        self.frameList1.selection_clear(0, "end")
        self.frameList2.selection_clear(0, "end")
        if self.sourceSel.get() == 1:
            if self.frameList1.get(0, "end").index(self.currFrame) < self.frameList1.size()-1:
                curr = self.frameList1.get(0, "end").index(self.currFrame)+1
                self.currFrame = self.frameList1.get(curr)
            else: 
                curr = self.frameList1.get(0, "end").index(self.currFrame)
    
            self.frameList1.selection_set(curr)
        
        elif self.sourceSel.get() == 2:
            if self.frameList2.get(0, "end").index(self.currFrame) < self.frameList2.size()-1:
                curr = self.frameList2.get(0, "end").index(self.currFrame)+1
                self.currFrame = self.frameList2.get(curr)
            else: 
                curr = self.frameList2.get(0, "end").index(self.currFrame)
        
            self.frameList2.selection_set(curr)
            
        else:
            print("No Source Selected")
                
        # self.frameList1.selection_clear(0, "end")
        # self.frameList1.selection_set(curr)
        # if self.currSource[2] != "":
        #     self.frameList2.selection_clear(0, "end")
        #     self.frameList2.selection_set(curr)
            
        self.loadImg()
        
    def previousFrame(self,event):
        
        self.frameList1.selection_clear(0, "end")
        self.frameList2.selection_clear(0, "end")
        if self.sourceSel.get() == 1:
            if self.frameList1.get(0, "end").index(self.currFrame)-1 >= 0:
                curr = self.frameList1.get(0, "end").index(self.currFrame)-1
                self.currFrame = self.frameList1.get(curr)
            else: 
                curr = self.frameList1.get(0, "end").index(self.currFrame)
        
            self.frameList1.selection_set(curr)
            
        elif self.sourceSel.get() == 2:
            if self.frameList2.get(0, "end").index(self.currFrame)-1 >= 0:
                curr = self.frameList2.get(0, "end").index(self.currFrame)-1
                self.currFrame = self.frameList2.get(curr)
            else: 
                curr = self.frameList2.get(0, "end").index(self.currFrame)
        
            self.frameList2.selection_set(curr)
            
        else:
            print("No Source Selected")
            
        # self.frameList1.selection_clear(0, "end")
        # self.frameList1.selection_set(curr)
        # if self.currSource[2] != "":
        #     self.frameList2.selection_clear(0, "end")
        #     self.frameList2.selection_set(curr)
            
        self.loadImg()
            
            
            
        
    def saveFrame(self, event): 
        
        print(self.winfo_screenwidth())
        print(self.winfo_screenheight())
        print('Self.geometry:', (self.winfo_geometry()))
        print('Self.width:', float(self.winfo_width()))
        print('Self.height:', float(self.winfo_height()))
        print('canvas.geometry:', (self.canvas.winfo_geometry()))
        print('canvas.width :', float(self.canvas.winfo_width())*2.5)
        print('canvas.height:', float(self.canvas.winfo_height())*2.5)
        print('canvas.x:', float(self.canvas.winfo_x())*2.5)
        print('canvas.y:', float(self.canvas.winfo_y())*2.5)
        print('canvas.rootx:', float(self.canvas.winfo_rootx())*2.5)
        print('canvas.rooty:', float(self.canvas.winfo_rooty())*2.5)
        
        directory = "saved_frames/"
        if not os.path.exists(directory):
            os.makedirs(directory)
    
        screenShot = ImageGrab.grab()
        wW,wH = screenShot.size
        swW = self.winfo_screenwidth()
        scaling = wW/swW
        
        x1=float(self.canvas.winfo_rootx())*scaling
        y1=float(self.canvas.winfo_rooty())*scaling
        x2=float(self.canvas.winfo_rootx())*scaling + float(self.canvas.winfo_width())*scaling
        y2=float(self.canvas.winfo_rooty())*scaling + float(self.canvas.winfo_height())*scaling
        screenShot.crop((x1,y1,x2,y2)).save(f"{directory}{self.currFrame}")
        
        
    def loadImg(self):
        path = f"{self.currSource[self.sourceSel.get()]}/{self.currFrame}"
        if os.path.isfile(path): # Check if image exists
            self.pilImg = Image.open(path)
            iW,iH = self.pilImg.size
            
            sW, sH = self.winfo_screenwidth(), self.winfo_screenheight()
            ratio = min((sW*0.8)/iW, (sH*0.8)/iH) 
            niH = ratio*iH
            niW= ratio*iW
                
            niH = int(math.floor(niH))
            niW = int(math.floor(niW))
            # print(niH)
            # print(niW)
                
            # print(f"Before Del: {self.canvas.find_all()}")
            self.canvas.delete("all")
            # print(f"After Del: {self.canvas.find_all()}")
            
            self.resizedImg = self.pilImg.resize((niW,niH))
            self.img = ImageTk.PhotoImage(self.resizedImg)
            self.canvas.config(width=niW, height=niH)
            self.canvas.create_image(0,0,anchor="nw" ,image = self.img)
            
            self.xRat = self.resizedImg.size[0]/self.pilImg.size[0]
            self.yRat = self.resizedImg.size[1]/self.pilImg.size[1]
            
            self.objects = []
            self.polygons = []
            self.boxes = []
            self.objectList.delete(0, "end")
            self.images = []
            
            classes = self.classList.get(0, "end")
            
            fileB=f"{self.currSource[self.sourceSel.get()]}/{self.currFrame.split('.')[0]}_box.txt" 
            fileM=f"{self.currSource[self.sourceSel.get()]}/{self.currFrame.split('.')[0]}_mask.txt"
            #print(fileB)
            if os.path.isfile(fileB):
                f = open(fileB, "r")
                for x in f:
                    items = x.split(',')
                    if len(items) == 6:
                        for c in classes:
                            if c.split(' ')[0] == items[1]:
                                self.color = c.split(' ')[2]
        
                        rectCoord = f"{round(float(items[2]),2)},{round(float(items[3]),2)},{round(float(items[4]),2)},{round(float(items[5][:-1]),2)}"
                        self.objects.append((items[0],"box", items[1],rectCoord)) # Adding to object[]
                        self.objectList.insert(int(items[0])-1,(items[0],"box",items[1])) 
                        self.boxes.append(self.create_rectangle(float(items[2])*self.xRat,float(items[3])*self.yRat,float(items[4])*self.xRat,float(items[5][:-1])*self.yRat,width=2,fill=self.color,tags=str(items[0])+"tag",alpha=0.3)) # Create final box)
            
            if os.path.isfile(fileM):
                f = open(fileM, "r")
                for x in f:
                    items = x.split(',')
                    if len(items) > 5:
                        for c in classes:
                            if c.split(' ')[0] == items[1]:
                                self.color = c.split(' ')[2]
                                
                        tmpMaskObj = ""
                        for coord in range(2,len(items)-1):
                            x= float(items[coord].split('_')[0])
                            y= float(items[coord].split('_')[1])
                            pntList = F"{round(x,2)}_{round(y,2)},"
                            tmpMaskObj += pntList
                            self.currentMask.append([x*self.xRat,y*self.yRat])
                        self.polygons.append(self.create_polygon(self.currentMask, fill=self.color,tags=str(items[0])+"tag",alpha=0.3)) # Make the new poly to stay on the canvas
        
                        self.objects.append((items[0],"mask",items[1],tmpMaskObj))
                        self.currentMask = [] # Clear currentMask
                        self.objectList.insert(int(items[0])-1,(items[0],"mask",items[1])) # Add polygon to objectlist
    
                    # self.objects.append([items[0],'mask',items[1]
                    #             self.objects.append((self.objectList.size(),"mask",self.currClass.split(' ')[0],tmpMaskObj))
                    #                      float(items[2])*self.xRat,float(items[3])*self.yRat,float(items[4])*self.xRat,float(items[5][:-1])*self.yRat])
                    #self.objectList.insert("end",(items[0],"box",items[1])) 
                    #self.boxes.append(self.canvas.create_rectangle(float(items[2])*self.xRat,float(items[3])*self.yRat,float(items[4])*self.xRat,float(items[5][:-1])*self.yRat,width=2,fill=self.color)) # Create final box)
            self.setClass()
            
            # print(f"After Repop: {self.canvas.find_all()}")
        else:
            print("Image not found")
        
    
    def addtotxt(self,type):
        file=f"{self.currSource[self.sourceSel.get()]}/{self.currFrame.split('.')[0]}_{type}.txt" 
        str=""
        with open(file, 'w') as filetowrite:
            for obj in self.objects:
                if obj[1]==type:
                    str = str + F"{obj[0]},{obj[2]},{obj[3]}\n"
            filetowrite.write(str)
                
    def polyBindEvent(self, event):
        self.polyBind()
        
    def polyBind(self):
        self.removeEditing()
        self.mode = "mask"
        if self.polygonTouch.get():
            self.bind('<Motion>', self.maskingTouch)
        else:
            self.bind('<Motion>', lambda event, mode="motion": 
                            self.masking(event,mode))
            
            
    def boxBind(self,event):
        self.removeEditing()
        self.bind('<Motion>', lambda event, mode="motion": 
                            self.boxing(event,mode))
        self.mode = "box"
        

            
        
    # Called from the <motion> event when the mask tool is selected    
    def maskingTouch(self,event):
        self.setClass() 
        if self.onCanvas:   # If the cursor is over the canvas
        
                if self.zoomEnable:
                    self.create_rectangle(0,0,0,0,zoom=self.zoomFactor, x=event.x, y=event.y,size = 60)
                    
                if self.clicked:    # If the mouse was clicked i.e. a new mask has been started
                    x, y = event.x, event.y 
                    self.currentMask.append([x,y]) # Add current points to current mask
                    if self.canvas_tmp_poly: # Delete old temperorary mask
                        self.canvas.delete(self.canvas_tmp_poly) 
                    self.canvas_tmp_poly = self.create_polygon(self.currentMask, fill=self.color,alpha=0.2) # Create a new temp mask
                else:
                    if len(self.currentMask) > 0: # If an object was created 
                        if self.canvas_tmp_poly: # Delete the temp poly
                            self.canvas.delete(self.canvas_tmp_poly)
                        
                        if len(self.currentMask) > 2:
                            newID = self.findNextID()
                            self.polygons.append(self.create_polygon(self.currentMask, fill=self.color,tags=str(newID)+"tag",alpha=0.3)) # Make the new poly to stay on the canvas
                            tmpMaskObj = ""
                            for point in self.currentMask: # Add Polygon points to a list to add to txt
                                pntList = F"{round(point[0]/self.xRat,2)}_{round(point[1]/self.yRat,2)},"
                                tmpMaskObj += pntList
                                
                            self.objects.append((newID,"mask",self.currClass.split(' ')[0],tmpMaskObj))
                            self.currentMask = [] # Clear currentMask
                            self.objectList.insert("end",(newID,"mask",self.currClass.split(' ')[0])) # Add polygon to objectlist
                            self.addtotxt("mask")     # For generating .txt file



   # Called from the <Clicked>, <Release> & <Motion> events when the mask tool is selected    
    def masking(self,event, mode):
        self.setClass() 
        if self.onCanvas:   # If the cursor is over the canvas
            if mode == "click":
                
                self.currentMask.append([event.x,event.y]) # Add current points to current mask
                
                if len(self.currentMask) > 1:
                    #Calculate the distance between the first point and the current point to see if polygon is done
                    distance = self.calculateDistance(self.currentMask[0][0],self.currentMask[0][1],event.x,event.y)
                    if distance < 10:
                        self.currentMask.pop()
                        self.currentMask.append(self.currentMask[0])
                        if self.canvas_tmp_poly: # Delete the temp poly
                            self.canvas.delete(self.canvas_tmp_poly)
                            
                        if len(self.currentMask) >3:
                            newID = self.findNextID()
                            self.polygons.append(self.create_polygon(self.currentMask, fill=self.color, tags=str(newID)+"tag",alpha=0.3)) # Make the new poly to stay on the canvas
                            tmpMaskObj = ""
                            for point in self.currentMask: # Add Polygon points to a list to add to txt
                                pntList = F"{round(point[0]/self.xRat,2)}_{round(point[1]/self.yRat,2)},"
                                tmpMaskObj += pntList
                                
                            self.objects.append([newID,"mask",self.currClass.split(' ')[0],tmpMaskObj])
                            self.currentMask = [] # Clear currentMask
                            self.canvas.delete(self.canvas_tmp_poly_origin)
                            self.objectList.insert("end",(newID,"mask",self.currClass.split(' ')[0])) # Add polygon to objectlist
                            self.addtotxt("mask")     # For generating .txt file
                        else:                            
                            self.canvas.delete(self.canvas_tmp_poly_origin)
                            self.currentMask = [] # Clear currentMask
                
                
            if mode == "motion":
                
                if self.zoomEnable:
                    self.create_rectangle(0,0,0,0,zoom=self.zoomFactor, x=event.x, y=event.y,size = 60)
                
                
                if len(self.currentMask) > 0:
                    x, y = event.x, event.y 
                    self.currentMask.append([x,y]) # Add current points to current mask
                    if self.canvas_tmp_poly: # Delete old temperorary mask
                        self.canvas.delete(self.canvas_tmp_poly) 
                    self.canvas_tmp_poly = self.create_polygon(self.currentMask, fill=self.color,alpha=0.2) # Create a new temp mask
                    if self.canvas_tmp_poly: # Delete old temperorary origin
                        self.canvas.delete(self.canvas_tmp_poly_origin) 
                    self.canvas_tmp_poly_origin = self.canvas.create_oval(self.currentMask[0][0]-5,
                                                                          self.currentMask[0][1]-5,
                                                                          self.currentMask[0][0]+5,
                                                                          self.currentMask[0][1]+5, fill = "black")
                    self.canvas.tag_raise( self.canvas_tmp_poly_origin)
                    self.currentMask.pop()


                        
            
            
    # Called from <Clicked>, <Release> & <Motion> when box tool selected
    def boxing(self,event,mode):
        if self.boxingOk:
            if mode == "click": # If click event
                if self.onCanvas:
                    x, y = event.x, event.y 
                    self.canvas.origin_box_coords = x, y # Obtain origin coords
            elif mode =="release": # If release event
                if self.canvas.origin_box_coords:
                    self.setClass()
                    self.canvas.delete(self.canvas_tmp_box) # Del temp box
                    nX, nY = event.x, event.y # Get final coords
                    oX,oY = self.canvas.origin_box_coords # Get origin coords
                    dist = self.calculateDistance(nX,nY,oX,oY)
                    if dist > 5:
                        newID = self.findNextID()
                        self.boxes.append(self.create_rectangle(oX,oY,nX,nY,fill=self.color,tags=str(newID)+"tag",alpha=0.3)) # Create final box
                        rectCoord = f"{round(oX/self.xRat,2)},{round(oY/self.yRat,2)},{round(nX/self.xRat,2)},{round(nY/self.yRat,2)}"
                        self.objects.append((newID,"box", self.currClass.split(' ')[0],rectCoord)) # Adding to object[]
                        self.objectList.insert("end",(newID,"box",self.currClass.split(' ')[0])) # Add to objectlist
                        self.addtotxt("box")     # For generating .txt file
  
            elif mode == "motion": # If mouse moves
                
                if self.zoomEnable: # Check if zoom is enabled
                    self.create_rectangle(0,0,0,0,zoom=self.zoomFactor, x=event.x, y=event.y,size = 60) #Create zoom rect
                    
                if self.canvas.origin_box_coords: # If theres an origin point
                    self.setClass()
                    nX, nY = event.x, event.y
                    oX,oY = self.canvas.origin_box_coords
                    if self.canvas_tmp_box: # Delete old temp box 
                        self.canvas.delete(self.canvas_tmp_box)
                    self.canvas_tmp_box = self.create_rectangle(oX,oY,nX,nY,fill=self.color,alpha=0.2) # Make a temp box
        
                    
    def findNextID(self):
        if len(self.objects) > 0:
            ids = [int(i[0]) for i in self.objects] # Get all current IDs
            ids = sorted(ids) # Sort them numerically
            
            
            # Duplicate ID removing section of code
            idCount = {}
            dIDs = []
            for x in ids: # find duplicates
                if x not in idCount:
                    idCount[x] = 1
                else:
                    if idCount[x] == 1:
                        dIDs.append(x)
                    idCount[x] += 1
            
            if len(dIDs) > 0:
                for duplic in dIDs: #For each duplicate
                    firstOccur = True
                    for objI in range(len(self.objects)): 
                        if int(self.objects[objI][0]) == duplic: 
                            if firstOccur: # Allow to occur once
                                firstOccur = False
                            else:                                       # For more than 1 occurence
                                objectEntry = list(self.objects[objI])  
                                objectEntry[0] = str(max(ids)+1)    #change self.objects and update the image
                                self.objects[objI] = tuple(objectEntry)
                                
                                ids.remove(duplic)
                                ids.append(max(ids)+1)
                                
                self.addtotxt("mask") # Update txt file (which uses self.objects)
                self.addtotxt("box")
                self.loadImg() # Reload image to update IDs and Tags necessary for editing
                
            
            for i in range(max(ids)): 
                
                if i+1 != ids[i]: # Make sure they increment in 1s, if not return i+1 as ID
                    return i+1
        else:
            return 1 # If objects has no length then return ID as 1
                
        return max(ids)+1 # If all increments correctly, return max number incremented
        
        
        
    def setClass(self):
        if self.classList.curselection():
            self.currClass = self.classList.get(self.classList.curselection())
            self.color = self.currClass.split(' ')[2]
        else:
            self.currClass = self.classList.get(0)
            self.color = self.currClass.split(' ')[2]
        
        
    # Called on mouse click and release event
    def mouseClicked(self,event):
        if self.clicked == True: # If mouse has already been pressed
            self.clicked = False # Mouse has been released
            if self.mode == "box": # If we're boxing
                self.boxing(event,"release") # Call boxing and give release event
                self.canvas.origin_box_coords = None # Reset origin
            elif self.mode == "mask":
                self.masking(event,"release")
            elif self.mode == "edit":
                self.editObj(event,"release")

        else: # If mouse has been clicked
            self.clicked = True 
            if self.mode == "box": # If boxing, call box and give click event
                self.boxing(event,"click")
            elif self.mode == "mask":
                self.masking(event,"click")
            elif self.mode == "edit":
                self.editObj(event,"click")
        
        
    def create_polygon(self,coords,**kwargs):
        if 'alpha' in kwargs:
            alpha = int(kwargs.pop('alpha') * 255)
            fill = kwargs.pop('fill')
            r,g,b = self.winfo_rgb(fill) 
            colour = (r//256,g//256,b//256,alpha)
            bbox = [int(self.resizedImg.size[0]),int(self.resizedImg.size[1]),0,0]
            
            for c in coords:
                
                if c[0] < bbox[0]:
                    bbox[0] = round(c[0])
                if c[0] > bbox[2]:
                    bbox[2] = round(c[0])
                    
                if c[1] < bbox[1]:
                    bbox[1] = round(c[1])
                if c[1] > bbox[3]:
                    bbox[3] = round(c[1])
                
            crop = self.resizedImg.crop((bbox[0],bbox[1],bbox[2],bbox[3]))
            newCoords = []
            for c in coords:
                newCoords.append((round(c[0]-bbox[0]),round(c[1]-bbox[1])))
                
            image = Image.new('RGBA', crop.size)
            
            im_mask = Image.new("L", crop.size, 0) # Create mask around polygon to not obstruct other masks in canvas
            draw_mask = ImageDraw.Draw(im_mask)
            draw_mask.polygon(newCoords, fill=255)
            
            image.paste(crop)   #Add crop image RGB - RGBA
            image.putalpha(im_mask) # Add mask to only show area of polygon
                              
            drawing = ImageDraw.Draw(image) 
            drawing.polygon(newCoords, fill =colour) # Add polygon with colour to mix with background
            
            #image.show()
            
            self.images.append(ImageTk.PhotoImage(image)) # Necessary to reference image
            
            if 'tags' in kwargs:
                canvasIndex = self.canvas.create_image(bbox[0],bbox[1],image=self.images[-1], anchor='nw', tags=kwargs.pop('tags'))
            else:
                canvasIndex = self.canvas.create_image(bbox[0],bbox[1],image=self.images[-1], anchor='nw')
            
            return canvasIndex
            
            
        
    def create_rectangle(self, x1, y1, x2, y2, **kwargs):
        if 'alpha' in kwargs:
            alpha = int(kwargs.pop('alpha') * 255)
            fill = kwargs.pop('fill')
            r,g,b = self.winfo_rgb(fill) 
            colour = (r//256,g//256,b//256,alpha)
            image = Image.new('RGBA', (int(abs(x2-x1)), int(abs(y2-y1))), colour)
            self.images.append(ImageTk.PhotoImage(image))
            if 'tags' in kwargs:
                canvasIndex = self.canvas.create_image(min(x1,x2), min(y1,y2), image=self.images[-1], anchor='nw', tags=kwargs.pop('tags'))
            else:
                canvasIndex = self.canvas.create_image(min(x1,x2), min(y1,y2), image=self.images[-1], anchor='nw')
            return canvasIndex
        
        if 'zoom' in kwargs:
            
            if self.zImg is not None:
                self.zImg = None
            if self.zCanvasImg is not None:
                self.canvas.delete(self.zCanvasImg) 
                self.canvas.update_idletasks()
            zoom = float(kwargs.pop('zoom'))
            x = float(kwargs.pop('x'))
            y = float(kwargs.pop('y'))
            size = int(kwargs.pop('size'))
            
            screenShot = ImageGrab.grab() ##Use self.resizedImg instead
            wW,wH = screenShot.size
            swW = self.winfo_screenwidth()
            scaling = wW/swW
            x1=(self.canvas.winfo_rootx()*scaling) + (float(x)*scaling) - ((size*zoom)/2)
            y1=(self.canvas.winfo_rooty()*scaling) + (float(y)*scaling) - ((size*zoom)/2)
            x2=(self.canvas.winfo_rootx()*scaling) + (float(x)*scaling) + ((size*zoom)/2)
            y2=(self.canvas.winfo_rooty()*scaling) + (float(y)*scaling) + ((size*zoom)/2)
            self.zImg = ImageTk.PhotoImage(screenShot.crop((x1,y1,x2,y2)).resize((size,size)))
            self.zCanvasImg = self.canvas.create_image(x-(size/2), y-(size/2), image=self.zImg, anchor='nw')
            #self.zoomBox = self.canvas.create_image(x-(size/2), y-(size/2), image=self.zImg, anchor='nw')
                     
                
    
    def calculateDistance(self, x1, y1, x2, y2):  
         dist = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)  
         return dist  
    
    
    
    
    def delCurrObject(self,event):
        
        index = self.objectList.curselection()[0] # Find what object currently is selected

        self.objectList.select_set(index)
        listInfo = self.objectList.get(index) # Get txt info of the selection

        tag =(str(listInfo[0])+"tag",) # Generate tag specific to that object
        #item = self.canvas.find_withtag(tag) 
        coords = self.canvas.coords(tag)  # Find coords of that object     
        self.canvas.delete(tag)
        self.objectList.delete(index)

        for obj in self.objects:
            if obj[0] == listInfo[0]:
                self.editedItemTag = obj[0]
                self.objects.remove(obj)
                
        for v in self.vertices:
                        self.canvas.delete(v)
                        self.vertices = []
                        
        if listInfo[1] == 'mask':
            self.addtotxt("mask")
        else:
            self.addtotxt("box")
            
        self.removeEditing()
        



    
    def editCurrent(self,event):
        
        
        index = self.objectList.curselection()[0] # Find what object currently is selected
        if self.indexTempCoords is not None or self.editingBox is not None or self.editingPoly is not None or len(self.vertices) > 0:
            self.removeEditing()
                            
        self.mode = "edit"
        self.bind('<Motion>', lambda event, mode="motion": 
                            self.editObj(event,mode))
            
        self.bind("<Delete>",self.delCurrObject)
        self.bind("<BackSpace>",self.delCurrObject)
        
        self.objectList.select_set(index)
        listInfo = self.objectList.get(index) # Get txt info of the selection
        
        classes = self.classList.get(0,"end")
        for c in range(len(classes)):
            if listInfo[2] in classes[c]:
                self.classList.selection_clear(0,"end")
                self.classList.select_set(c)
        self.setClass()
        tag =(str(listInfo[0])+"tag",) # Generate tag specific to that object
        #item = self.canvas.find_withtag(tag) 
        coords = self.canvas.coords(tag)  # Find coords of that object     
        self.canvas.delete(tag)
        
        if listInfo[1] == 'box' and len(coords) == 4:
            oX = coords[0]
            oY = coords[1]
            nX = coords[2]
            nY = coords[3]
            self.tmpCoords = coords
            self.editingBox = self.create_rectangle(oX,oY,nX,nY,width=0,fill=self.color,tags=tag,alpha=0.2)
            self.vertices.append(self.canvas.create_oval(coords[0]-3,
                                                                coords[1]-3,
                                                                coords[0]+3,
                                                                coords[1]+3, fill = "black",width=1,outline="white"))
            self.vertices.append(self.canvas.create_oval(coords[2]-3,
                                                                coords[3]-3,
                                                                coords[2]+3,
                                                                coords[3]+3, fill = "black",width=1,outline="white"))
        elif listInfo[1] == 'mask':
            self.tmpCoords = coords
            self.editingPoly = self.create_polygon(coords, fill=self.color, tags=tag,alpha=0.2)
            for point in range(0,len(coords),2):
                self.vertices.append(self.canvas.create_oval(coords[point]-3,
                                                          coords[point+1]-3,
                                                          coords[point]+3,
                                                          coords[point+1]+3, fill = "black",width=1,outline="white"))
            
                
        
    def editObj(self,event,clickType):
        x = event.x
        y = event.y
        vX = []
        vY = []
        
        # print(f"X: {x}")
        # print(f"Y: {y}")
        
        if clickType == "click":
            if self.onCanvas:
                self.setClass()
                if self.editingBox:
                    vX = [self.tmpCoords[0],self.tmpCoords[2]]
                    vY = [self.tmpCoords[1],self.tmpCoords[3]]
                    
                    d0 = self.calculateDistance(x,y,vX[0],vY[0])
                    d1 = self.calculateDistance(x,y,vX[1],vY[1])
                    
                    if d0 < d1 and d0 < 10:
                        realX = vX[0]
                        self.indexTempCoords = 0
                    elif d1 < 10:
                        realX = vX[1]
                        self.indexTempCoords = 1
                    
                    if self.indexTempCoords is not None:
                        for v in self.vertices:
                            self.canvas.delete(v)
                            self.vertices = []
                            
                        index = self.objectList.curselection()[0] # Find what object currently is selected
                        listInfo = self.objectList.get(index) # Get txt info of the selection
                        self.objectList.delete(index)
                        
                        for obj in self.objects:
                            if obj[0] == listInfo[0]:
                                self.editedItemTag = obj[0]
                                self.objects.remove(obj)
                            
                            
                if self.editingPoly:
                    
                    dists = []
                    for c in range(0, len(self.tmpCoords),2):
                        d = self.calculateDistance(x,y,self.tmpCoords[c],self.tmpCoords[c+1])
                        dists.append(d)
                    print(f"Length Tmp Coords b4: {len(self.tmpCoords)}")
                    if min(dists) < 10:
                        self.indexTempCoords = dists.index(min(dists))*2
                        del self.tmpCoords[self.indexTempCoords:self.indexTempCoords+2]
                    
                    print(f"Length Tmp Coords after: {len(self.tmpCoords)}")
                    print(f"Index of Coord deleted: {self.indexTempCoords}")
                        
                        
                    if self.indexTempCoords is not None:
                        for v in self.vertices:
                            self.canvas.delete(v)
                            self.vertices = []
                            
                        index = self.objectList.curselection()[0] # Find what object currently is selected
                        listInfo = self.objectList.get(index) # Get txt info of the selection
                        self.objectList.delete(index)
                        
                        for obj in self.objects:
                            if obj[0] == listInfo[0]:
                                self.editedItemTag = obj[0]
                                self.objects.remove(obj)
                        print(f"ID: {self.editedItemTag}")
                    
                        
                        
                        
                        
        if clickType == "motion":
            if self.onCanvas:
                
                if self.editingBox:
                    if self.indexTempCoords is not None:
                        rect = self.tmpCoords
                        
                        oX = rect[0]
                        oY = rect[1]
                        nX = rect[2]
                        nY = rect[3]
                        
                        if self.indexTempCoords == 0:
                            oX = x
                            oY = y
                        elif self.indexTempCoords == 1:
                            nX = x
                            nY = y
                        
                        
                        if self.editingBox:
                            self.canvas.delete(self.editingBox)
                            self.editingBox = None
                            
                        self.editingBox = self.create_rectangle(min(oX,nX)
                                                                       ,min(oY,nY)
                                                                       ,max(oX,nX)
                                                                       ,max(oY,nY)
                                                                       ,fill=self.color, alpha=0.2)
                        
                if self.editingPoly:
                    if self.indexTempCoords is not None:
                        
                        tmpPoly = self.tmpCoords.copy()
                        tmpPoly.append(float(x))
                        tmpPoly.append(float(y))
                        
                        self.canvas.delete(self.editingPoly)
                        self.editingPoly = None
                        
                        self.editingPoly = self.create_polygon(tmpPoly, fill=self.color, alpha=0.2)
                
                
                    
        if clickType == "release":
            
            if self.onCanvas:
                if self.indexTempCoords is not None:
                    if self.editingBox:
                            
                        rect = self.tmpCoords
                        self.canvas.delete(self.editingBox)
                        self.editingBox = None
                        self.tmpCoords = []
                        
                        
                        oX = rect[0]
                        oY = rect[1]
                        nX = rect[2]
                        nY = rect[3]
            
                        if self.indexTempCoords == 0:
                            oX = x
                            oY = y
                        elif self.indexTempCoords == 1:
                            nX = x
                            nY = y
                            
                        self.indexTempCoords = None
                        # self.canvas.create_rectangle(min(oX,nX)
                        #                                 ,min(oY,nY)
                        #                                 ,max(oX,nX)
                        #                                 ,max(oY,nY)
                        #                                 ,fill=self.color)
                        
                        rectCoord = f"{round(min(oX,nX)/self.xRat,2)},{round(min(oY,nY)/self.yRat,2)},{round(max(oX,nX)/self.xRat,2)},{round(max(oY,nY)/self.yRat,2)}"
                        self.objects.append((self.editedItemTag,"box", self.currClass.split(' ')[0], rectCoord)) # Adding to object[]
                        #self.objectList.insert("end",(self.editedItemTag,"box",self.currClass.split(' ')[0])) # Add to objectlist
                        self.editedItemTag = None
                        self.addtotxt("box")
                        self.removeEditing()
                            
                        
                        
                    if self.editingPoly:
                        
                        tmpPoly = self.tmpCoords.copy()
                        tmpPoly.append(x)
                        tmpPoly.append(y)
                        
                        self.canvas.delete(self.editingBox)
                        self.editingBox = None
                        self.tmpCoords = []
                        self.indexTempCoords = None
                        
                        #self.polygons.append(self.canvas.create_polygon(tmpPoly, fill=self.color,tags=str(self.findNextID())+"tag")) # Make the new poly to stay on the canvas
                        tmpMaskObj = ""
                        for i in range(0, len(tmpPoly),2): # Add Polygon points to a list to add to txt
                            pntList = F"{round(tmpPoly[i]/self.xRat,2)}_{round(tmpPoly[i+1]/self.yRat,2)},"
                            tmpMaskObj += pntList
                                
                        self.objects.append([self.editedItemTag,"mask", self.currClass.split(' ')[0], tmpMaskObj]) # Adding to object[]
                        #self.objectList.insert("end",(self.editedItemTag,"mask",self.currClass.split(' ')[0])) # Add to objectlist
                        self.editedItemTag = None
                        
                        #self.addtotxt("mask")
                        
                        self.removeEditing()
                        
                        
                        
                        
        
    def removeEditing(self):
        if len(self.vertices) > 0:
            for v in self.vertices:
                self.canvas.delete(v)
            self.vertices = []
        if self.editingBox:
            self.canvas.delete(self.editingBox)
            self.editingBox = None
        if self.editingPoly:
            self.canvas.delete(self.editingPoly)
            self.editingPoly = None
        if self.indexTempCoords is not None:
            self.indexTempCoords = None
        
        self.loadImg()
        
            
            
    
    
    def remapOneBind(self,event):
        self.remap()
        
        
    def remapAllBind(self,event):
        frames = self.frameList1.get(0,"end")
        
        for index in range(len(frames)):
            self.sourceSel.set(1)
            self.currFrame = self.frameList1.get(index)   
            self.frameList1.selection_set(index)  
            self.remap()
        
        
    def remap(self):
        
        if self.sourceSel.get() == 1:
            index = self.frameList1.get(0, "end").index(self.currFrame)
        elif self.sourceSel.get() == 2:
            index = self.frameList2.get(0, "end").index(self.currFrame)
        else:
            print("No Source Selected")
        
        dispFile = self.dispList[index]
        path = f"{self.currSource[3]}/{dispFile}"
        if os.path.isfile(path): # Check if disparity image exists
        
            dispImg = Image.open(path)
            iW,iH = self.pilImg.size
            dW,dH = dispImg.size
            
            self.frameList2.selection_clear(0, "end")
            
            if self.sourceSel.get() == 2:
                self.sourceSel.set(1)
                self.currFrame = self.frameList1.get(index)    
                self.loadImg()
            
            self.frameList1.selection_set(index)   
            
            
            fileB=f"{self.currSource[self.sourceSel.get()]}/{self.currFrame.split('.')[0]}_box.txt" 
            fileM=f"{self.currSource[self.sourceSel.get()]}/{self.currFrame.split('.')[0]}_mask.txt"
            
            tempBoxes = []
            tempMasks = []
            
            if os.path.isfile(fileB):
                f = open(fileB, "r")
                for x in f:
                    items = x.split(',')
                    x1=float(items[2])
                    y1=float(items[3])
                    x2=float(items[4])
                    y2=float(items[5]) 
                    
                    left = min(x1,x2)
                    upper = min(y1,y2)
                    right = max(x1,x2)
                    bottom = max(y1,y2)
                    
                    cropped = dispImg.crop((left,upper,right,bottom))
                                        
                    flattened = np.array(cropped).flatten()
                    rmZero = flattened[flattened!=0]
                    med = np.median(rmZero)
                    #print(f"After Mask {med}")
                    
                    #tempBoxes.append([items[0],'box',items[1],float(items[2]-med),float(items[3]),float(items[4]-med),float(items[5][:-1])])
                    
                    rectCoord = f"{round(x1-med,2)},{round(y1,2)},{round(x2-med,2)},{round(y2,2)}"
                    tempBoxes.append((items[0],"box", items[1],rectCoord)) 

            
            if os.path.isfile(fileM):
                f = open(fileM, "r")
                for x in f:
                    items = x.split(',')
                    tmpMaskObj = ""
                    left=iW
                    upper=iH
                    right=0
                    bottom=0
                    
                    for coord in range(2,len(items)-1):
                        x= float(items[coord].split('_')[0])
                        y= float(items[coord].split('_')[1])
                        
                        if x<left:
                            left=x
                        if y<upper:
                            upper=y
                        if x>right:
                            right=x
                        if y>bottom:
                            bottom=y
                            
                    cropped = dispImg.crop((left,upper,right,bottom))
                    flattened = np.array(cropped).flatten()
                    rmZero = flattened[flattened!=0]
                    med = np.median(rmZero)
                    
                    for coord in range(2,len(items)-1):
                        x= float(items[coord].split('_')[0])
                        y= float(items[coord].split('_')[1]) 
                        pntList = F"{round(x-med,2)}_{round(y,2)},"
                        tmpMaskObj += pntList
                        
                    tempMasks.append((items[0],"mask",items[1],tmpMaskObj))
    
            
    
            self.frameList1.selection_clear(0, "end")
            
           
            self.sourceSel.set(2)
            self.currFrame = self.frameList2.get(index)   
            self.frameList2.selection_set(index)  
              
                    
            #print(dispImg.getpixel((880,108)))

            
            if len(tempBoxes) > 0:
                file=f"{self.currSource[self.sourceSel.get()]}/{self.currFrame.split('.')[0]}_box.txt" 
                str=""
                with open(file, 'w') as filetowrite:
                    for box in tempBoxes:
                        str = str + F"{box[0]},{box[2]},{box[3]}\n"
                    filetowrite.write(str)
                
            if len(tempMasks) > 0:
                file=f"{self.currSource[self.sourceSel.get()]}/{self.currFrame.split('.')[0]}_mask.txt" 
                str=""
                with open(file, 'w') as filetowrite:
                    for mask in tempMasks:
                        str = str + F"{mask[0]},{mask[2]},{mask[3]}\n"
                    filetowrite.write(str)
                
            self.loadImg()

        #load disp img
        #left image txt file
        #parse bounding box, mask
        #get middle region and find the median value, ignoring 0 
        #create right image text file based on left image x correction
    
    
    
if __name__=="__main__":
    app = App() 
    app.title("Multi-Labeller") 
    app.iconbitmap("icon.ico")
    app.mainloop()   
    