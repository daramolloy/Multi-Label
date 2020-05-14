import tkinter as tk
#from tkinter import *
from tkinter import ttk, filedialog
from PIL import ImageTk, Image, ImageGrab
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
        self.geometry("-5+0")
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
        self.boxingOk = True
        
        
        self.classes = []
        self.images = []
        self.polygons = []
        self.boxes = []
        self.currentMask = []
        self.objects = []
        
        self.dispList = []
        self.currSource = [r"test_imgs","","",""]
        self.currFrame = "dub.jpg"
        
        self.currClass = None
        self.mode = "box"
        self.color = "blue"
        
        
        self.loadButtons()    
        self.loadImg()
        self.loadClasses()
        
        self.onCanvas = False
        
        
        self.canvas.bind("<Enter>",self.startAnnotating)
        self.canvas.bind("<Leave>",self.stopAnnotating)
        
        
        self.bind('<Motion>', lambda event, point="motion": 
                            self.boxing(event,point))
        self.bind('<ButtonPress-1>', self.mouseClicked)
        self.bind('<ButtonRelease-1>', self.mouseClicked)
    
        self.canvas.bind("<MouseWheel>",self.zoomer)
        self.state('zoomed')



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
        
        
        
    def zoomer(self,event):
        return
        # if (event.delta > 0):
        #     self.canvas.scale("all", event.x, event.y, 1.1, 1.1)
        # elif (event.delta < 0):
        #     self.canvas.scale("all", event.x, event.y, 0.9, 0.9)
        # self.canvas.configure(scrollregion = self.canvas.bbox("all"))


    def startAnnotating(self, event):
        self.onCanvas = True

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
        
        self.sourceList1 = ttk.Radiobutton(self,value=1, text="1:",variable = self.sourceSel, command=self.sourceChanged)
        self.sourceList1.grid(row = 2, column = 0,columnspan=2, sticky = "nesw") 
        self.bind('e',self.firstSource)
        self.bind('r',self.secondSource)


        self.zoomIn = ttk.Button (self,text="Zoom In")
        self.zoomOut = ttk.Button (self,text="Zoom Out")
        self.zoomIn.grid(row = 3, column = 0,columnspan=1, sticky = "nesw", pady = 5, padx = 5) 
        self.zoomOut.grid(row = 3, column = 1,columnspan=1, sticky = "nesw", pady = 5, padx = 5)
        
        self.zoomIn.bind("<Button-1>", self.polyBindEvent)
        self.zoomOut.bind("<Button-1>", self.boxBind)
        
        

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

        self.frameListLabel1 = ttk.Label(self,text="Source 1:")
        self.frameListLabel1.grid(row = 5, column = 12,columnspan=1, sticky = "s") 
        self.frameList1 = tk.Listbox(self,exportselection=0)
        self.frameList1.grid(row = 6, column = 12,columnspan=1, rowspan = 3, sticky = "nesw", pady = 5, padx = 5) 
        
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
        self.frameScrollbar = tk.Scrollbar(self)
        self.frameScrollbar.grid(row = 6, column = 15,columnspan=1, rowspan = 3, sticky = "nes")

        self.frameList1.config(yscrollcommand=self.frameScrollbar.set)
        self.frameList2.config(yscrollcommand=self.frameScrollbar.set)
        self.frameScrollbar.config(command=self.frameList1.yview)
        self.frameScrollbar.config(command=self.frameList2.yview)
        
              
        
        
    def loadClasses(self):
        colour = ["blue", "red", "green", "cyan", "yellow", "magenta", "magenta", "magenta", "magenta", "magenta", "magenta"]
       	f= open("Classes.txt","r")
       	if f.mode == 'r':
           contents =f.read()
           classestxt = contents.split(',')
           for x in range(len(classestxt)):
               self.classList.insert("end",f"{classestxt[x]} -- {colour[x]}")
               self.classes.append([classestxt[x],colour[x]])
        self.classList.activate(0)
        self.classList.selection_set(0)
        self.currClass = self.classes[0]
        
        
        
    def sourceChanged(self):
        print("source changed")
        
        if self.sourceSel.get() == 1:
            print(f"2->1   B4: {self.currFrame}")
            index = self.frameList2.get(0, "end").index(self.currFrame)
            self.currFrame = self.frameList1.get(index)
            self.frameList2.selection_clear(0, "end")
            self.frameList1.selection_set(index)
            print(f"2->1   {index},{self.currFrame}")
            
        if self.sourceSel.get() == 2:
            print(f"1->2   B4: {self.currFrame}")
            index = self.frameList1.get(0, "end").index(self.currFrame)
            self.currFrame = self.frameList2.get(index)
            self.frameList1.selection_clear(0, "end")
            self.frameList2.selection_set(index)
            print(f"1->2   {index},{self.currFrame}")
            
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
            self.sourceList1.config(text = f"1: {dataDir.split('/')[-1]}")
            for file in os.listdir(dataDir):
                if ".jpg" in file or ".png" in file or ".tiff" in file or ".gif" in file:
                    self.frameList1.insert("end",file)
            self.sourceSel.set(1)
            
        elif self.currSource[2] == "":
            self.sourceList2 = ttk.Radiobutton(self,value=2, text=f"2: {dataDir.split('/')[-1]}",variable = self.sourceSel, command=self.sourceChanged)
            self.sourceList2.grid(row = 2, column = 1,columnspan=2, sticky = "nesw") 
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
        self.sourceList.delete("anchor")
        
        
    
            
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
        print('  root.geometry:', self.winfo_geometry())
        print('canvas.geometry:', self.canvas.winfo_geometry())
        print('canvas.width :', self.canvas.winfo_width())
        print('canvas.height:', self.canvas.winfo_height())
        print('canvas.x:', self.canvas.winfo_x())
        print('canvas.y:', self.canvas.winfo_y())
        print('canvas.rootx:', self.canvas.winfo_rootx())
        print('canvas.rooty:', self.canvas.winfo_rooty())
        x=976#self.canvas.winfo_rootx()+self.canvas.winfo_x()
        y=65#self.canvas.winfo_rooty()+self.canvas.winfo_y()
        x1=3000#self.canvas.winfo_width()
        y1=3000#self.canvas.winfo_height()
        bb=(x,y,x1,y1)
        self.grabcanvas = ImageGrab.grab(bbox=bb).save("out_snapsave.jpg")
        
        
        
    def loadImg(self):
        path = f"{self.currSource[self.sourceSel.get()]}/{self.currFrame}"
        print(path)
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
                
            
            fileB=f"{self.currSource[self.sourceSel.get()]}/{self.currFrame.split('.')[0]}_box.txt" 
            fileM=f"{self.currSource[self.sourceSel.get()]}/{self.currFrame.split('.')[0]}_mask.txt"
            #print(fileB)
            if os.path.isfile(fileB):
                f = open(fileB, "r")
                for x in f:
                    items = x.split(',')
                    #print(items)
                    self.objects.append([items[0],'box',items[1],float(items[2])*self.xRat,float(items[3])*self.yRat,float(items[4])*self.xRat,float(items[5][:-1])*self.yRat])
                    self.objectList.insert("end",(items[0],"box",items[1])) 
                    self.boxes.append(self.canvas.create_rectangle(float(items[2])*self.xRat,float(items[3])*self.yRat,float(items[4])*self.xRat,float(items[5][:-1])*self.yRat,width=2,fill=self.color)) # Create final box)
            
            if os.path.isfile(fileM):
                f = open(fileM, "r")
                for x in f:
                    items = x.split(',')
                    #print(items)
                    tmpMaskObj = ""
                    for coord in range(2,len(items)-1):
                        x= float(items[coord].split('_')[0])
                        y= float(items[coord].split('_')[1])
                        pntList = F"{round(x*self.xRat,2)}_{round(y*self.yRat,2)},"
                        tmpMaskObj += pntList
                        self.currentMask.append([x*self.xRat,y*self.yRat])
                    self.polygons.append(self.canvas.create_polygon(self.currentMask, fill=self.color)) # Make the new poly to stay on the canvas
    
                    self.objects.append((items[0],"mask",items[1],tmpMaskObj))
                    self.currentMask = [] # Clear currentMask
                    self.objectList.insert("end",(items[0],"mask",items[1])) # Add polygon to objectlist
    
                    # self.objects.append([items[0],'mask',items[1]
                    #             self.objects.append((self.objectList.size(),"mask",self.currClass.split(' ')[0],tmpMaskObj))
                    #                      float(items[2])*self.xRat,float(items[3])*self.yRat,float(items[4])*self.xRat,float(items[5][:-1])*self.yRat])
                    #self.objectList.insert("end",(items[0],"box",items[1])) 
                    #self.boxes.append(self.canvas.create_rectangle(float(items[2])*self.xRat,float(items[3])*self.yRat,float(items[4])*self.xRat,float(items[5][:-1])*self.yRat,width=2,fill=self.color)) # Create final box)
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
        #print(F"Entering Polybind")
        #print(F"polytouch var = {self.polygonTouch.get()}")
        self.mode = "mask"
        if self.polygonTouch.get():
            self.bind('<Motion>', self.maskingTouch)
        else:
            self.bind('<Motion>', lambda event, mode="motion": 
                            self.masking(event,mode))
            
            
    def boxBind(self,event):
        self.bind('<Motion>', lambda event, mode="motion": 
                            self.boxing(event,mode))
        self.mode = "box"
        
        
        
    # Called from the <motion> event when the mask tool is selected    
    def maskingTouch(self,event):
        self.setClass() 
        if self.onCanvas:   # If the cursor is over the canvas
                if self.clicked:    # If the mouse was clicked i.e. a new mask has been started
                    x, y = event.x, event.y 
                    self.currentMask.append([x,y]) # Add current points to current mask
                    if self.canvas_tmp_poly: # Delete old temperorary mask
                        self.canvas.delete(self.canvas_tmp_poly) 
                    self.canvas_tmp_poly = self.canvas.create_polygon(self.currentMask, fill=self.color) # Create a new temp mask
                else:
                    if len(self.currentMask) > 0: # If an object was created 
                        if self.canvas_tmp_poly: # Delete the temp poly
                            self.canvas.delete(self.canvas_tmp_poly)
                        
                        if len(self.currentMask) > 2:
                            self.polygons.append(self.canvas.create_polygon(self.currentMask, fill=self.color)) # Make the new poly to stay on the canvas
                            tmpMaskObj = ""
                            for point in self.currentMask: # Add Polygon points to a list to add to txt
                                pntList = F"{round(point[0]/self.xRat,2)}_{round(point[1]/self.yRat,2)},"
                                tmpMaskObj += pntList
                                    
                            self.objects.append((self.objectList.size(),"mask",self.currClass.split(' ')[0],tmpMaskObj))
                            self.currentMask = [] # Clear currentMask
                            self.objectList.insert("end",(self.objectList.size(),"mask",self.currClass.split(' ')[0])) # Add polygon to objectlist
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
                            self.polygons.append(self.canvas.create_polygon(self.currentMask, fill=self.color)) # Make the new poly to stay on the canvas
                            tmpMaskObj = ""
                            for point in self.currentMask: # Add Polygon points to a list to add to txt
                                pntList = F"{round(point[0]/self.xRat,2)}_{round(point[1]/self.yRat,2)},"
                                tmpMaskObj += pntList
                                    
                            self.objects.append([self.objectList.size(),"mask",self.currClass.split(' ')[0],tmpMaskObj])
                            self.currentMask = [] # Clear currentMask
                            self.canvas.delete(self.canvas_tmp_poly_origin)
                            self.objectList.insert("end",(self.objectList.size(),"mask",self.currClass.split(' ')[0])) # Add polygon to objectlist
                            self.addtotxt("mask")     # For generating .txt file
                        else:                            
                            self.canvas.delete(self.canvas_tmp_poly_origin)
                            self.currentMask = [] # Clear currentMask
                
                
            if mode == "motion":
                if len(self.currentMask) > 0:
                    x, y = event.x, event.y 
                    self.currentMask.append([x,y]) # Add current points to current mask
                    if self.canvas_tmp_poly: # Delete old temperorary mask
                        self.canvas.delete(self.canvas_tmp_poly) 
                    self.canvas_tmp_poly = self.canvas.create_polygon(self.currentMask, fill=self.color) # Create a new temp mask
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
                        self.boxes.append(self.canvas.create_rectangle(oX,oY,nX,nY,width=2,fill=self.color)) # Create final box
                        rectCoord = f"{round(oX/self.xRat,2)},{round(oY/self.yRat,2)},{round(nX/self.xRat,2)},{round(nY/self.yRat,2)}"
                        self.objectList.insert("end",(self.objectList.size(),"box",self.currClass.split(' ')[0])) # Add to objectlist
                        self.objects.append((self.objectList.size(),"box", self.currClass.split(' ')[0],rectCoord)) # Adding to object[]
                        self.addtotxt("box")     # For generating .txt file
    
            elif mode == "motion": # If mouse moves
                if self.canvas.origin_box_coords: # If theres an origin point
                    self.setClass()
                    nX, nY = event.x, event.y
                    oX,oY = self.canvas.origin_box_coords
                    if self.canvas_tmp_box: # Delete old temp box 
                        self.canvas.delete(self.canvas_tmp_box)
                    self.canvas_tmp_box = self.canvas.create_rectangle(oX,oY,nX,nY,outline=self.color,width=1) # Make a temp box
                        
            
    def setClass(self):
        self.currClass = self.classList.get(self.classList.curselection())
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

        else: # If mouse has been clicked
            self.clicked = True 
            if self.mode == "box": # If boxing, call box and give click event
                self.boxing(event,"click")
            elif self.mode == "mask":
                self.masking(event,"click")
        
        
        
    # def create_rectangle(self, x1, y1, x2, y2, **kwargs):
    #     if 'alpha' in kwargs:
    #         alpha = int(kwargs.pop('alpha') * 255)
    #         fill = kwargs.pop('fill')
    #         fill = self.winfo_rgb(fill) + (alpha,)
    #         image = Image.new('RGBA', (abs(x2-x1), abs(y2-y1)), fill)
    #         self.images.append(ImageTk.PhotoImage(image))
    #         self.canvas.create_image(min(x1,x2), min(y1,y2), image=self.images[-1], anchor='nw')
    #     #self.canvas.create_rectangle(x1, y1, x2, y2, **kwargs)
    
    
    def calculateDistance(self, x1, y1, x2, y2):  
         dist = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)  
         return dist  
    
    
    
    
    def remapOneBind(self,event):
        self.remap("curr")
        
        
    def remapAllBind(self,event):
        self.remap("all")
        
        
    def remap(self,mode):
        
        if self.sourceSel.get() == 1:
            index = self.frameList1.get(0, "end").index(self.currFrame)
        elif self.sourceSel.get() == 2:
            index = self.frameList2.get(0, "end").index(self.currFrame)
        else:
            print("No Source Selected")
        
        dispFile = self.dispList[index]
        path = f"{self.currSource[3]}/{dispFile}"
        print(path)
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
                    print(f"After Mask {med}")
                    
                    #tempBoxes.append([items[0],'box',items[1],float(items[2]-med),float(items[3]),float(items[4]-med),float(items[5][:-1])])
                    
                    rectCoord = f"{x1-med},{y1},{x2-med},{y2}"
                    tempBoxes.append((items[0],"box", items[1],rectCoord)) 


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
                
            # if len(tempMasks) > 0:
            #     file=f"{self.currSource[self.sourceSel.get()]}/{self.currFrame.split('.')[0]}_mask.txt" 
            #     str=""
            #     with open(file, 'w') as filetowrite:
            #         for mask in tempMasks:
            #             str = str + F"{mask[0]},{mask[2]},{mask[3]}\n"
            #         filetowrite.write(str)
                
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
    