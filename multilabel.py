import tkinter as tk
from tkinter import *
from tkinter import ttk, filedialog
from PIL import ImageTk, Image, ImageGrab
import math
import os


class Root(tk.Toplevel):
    
    def __init__(self):
        super(Root, self).__init__()
        self.canvas = tk.Canvas(self, width=0, height=0)
        #self.protocol("WM_DELETE_WINDOW", self.canvas)
        self.canvas.grid(row = 1, column = 3,columnspan=8, rowspan=8, sticky = "n", pady = 2,padx = 2)
        self.geometry("-5+0")
        # self.attributes("-fullscreen", True)
        # print(self.winfo_screenwidth())
        self.canvas.config(cursor="cross",relief="ridge")
        

        # self.bboxbut = ttk.Button(self,text = "Bounding Box")
        #self.bboxbut.grid(column=0,row=0)
        #self.paintbut = ttk.Button(self,text = "Paint Box")
        #self.paintbut.grid(column=0,row=1)
        #self.but = Label (self,text="Bounding Box")
        #self.but.pack(side=BOTTOM)
        
        self.canvas.old_mask_coords = None
        self.canvas.old_box_coords = None
        self.canvas_tmp_box = None
        self.clicked = False
        
        self.classes = []
        self.images = []
        self.polgons = []
        self.boxes = []
        self.currentMask = []
        self.objects = []
        
        self.currSource = r"C:\Users\daram\Desktop\Multi-Source Labelling\Img"
        self.currFrame = "dub.jpg"
        
        self.currClass = None
        self.mode = "box"
        self.color = "blue"
        
        
        self.loadButtons()        
        self.loadImg()
        self.loadClasses()
        
        self.annotating = False
        
        
        
        self.canvas.bind("<Enter>",self.startAnnotating)
        self.canvas.bind("<Leave>",self.stopAnnotating)
        
        
        self.bind('<Motion>', lambda event, point="motion": 
                            self.boxing(event,point))
        self.bind('<ButtonPress-1>', self.mouseClicked)
        self.bind('<ButtonRelease-1>', self.mouseClicked)
    
        self.canvas.bind("<MouseWheel>",self.zoomer)


    def zoomer(self,event):
        return
        # if (event.delta > 0):
        #     self.canvas.scale("all", event.x, event.y, 1.1, 1.1)
        # elif (event.delta < 0):
        #     self.canvas.scale("all", event.x, event.y, 0.9, 0.9)
        # self.canvas.configure(scrollregion = self.canvas.bbox("all"))


    def startAnnotating(self, event):
        self.annotating = True

    def stopAnnotating(self, event):
        self.annotating = False
        
        
    def loadButtons(self):
        self.addSourceBtn = ttk.Button (self,text="Add Source")
        self.rmSource = ttk.Button (self,text="Remove Source")
        self.addSourceBtn.grid(row = 1, column = 0, sticky = "nesw", pady = 5, padx = 5) 
        self.rmSource.grid(row = 1, column = 1, sticky = "nesw", pady = 5, padx = 5)
        
        self.addSourceBtn.bind("<Button-1>", self.addSource)
        self.rmSource.bind("<Button-1>", self.removeSource)
        
        self.sourceList = tk.Listbox(self,exportselection=0)
        self.sourceList.grid(row = 2, column = 0,columnspan=2, sticky = "nesw", pady = 5, padx = 5) 

        self.zoomIn = ttk.Button (self,text="Zoom In")
        self.zoomOut = ttk.Button (self,text="Zoom Out")
        self.zoomIn.grid(row = 3, column = 0,columnspan=1, sticky = "nesw", pady = 5, padx = 5) 
        self.zoomOut.grid(row = 3, column = 1,columnspan=1, sticky = "nesw", pady = 5, padx = 5)
        
        self.zoomIn.bind("<Button-1>", self.maskBind)
        self.zoomOut.bind("<Button-1>", self.boxBind)
        
        

        self.maskBtn = ttk.Button (self,text="Mask Creation Tool")
        self.boxBtn = ttk.Button (self,text="Box Creation Tool")
        self.maskBtn.grid(row = 5, column = 0,columnspan=2, sticky = "nesw", pady = 5, padx = 5) 
        self.boxBtn.grid(row = 4, column = 0,columnspan=2, sticky = "nesw", pady = 5, padx = 5)
        
        self.maskBtn.bind("<Button-1>", self.maskBind)
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
        self.objectList.grid(row = 1, column = 12,columnspan=2, rowspan = 3, sticky = "nesw", pady = 5, padx = 5) 
        self.objScrollbar = Scrollbar(self)
        self.objScrollbar.grid(row = 1, column = 14,columnspan=1, rowspan = 3, sticky = "nes")

        self.objectList.config(yscrollcommand=self.objScrollbar.set)
        self.objScrollbar.config(command=self.objectList.yview)

        
        self.frameList = tk.Listbox(self,exportselection=0)
        self.frameList.grid(row = 6, column = 12,columnspan=2, rowspan = 3, sticky = "nesw", pady = 5, padx = 5) 
        self.frameScrollbar = Scrollbar(self)
        self.frameScrollbar.grid(row = 6, column = 14,columnspan=1, rowspan = 3, sticky = "nes")

        self.frameList.config(yscrollcommand=self.frameScrollbar.set)
        self.frameScrollbar.config(command=self.frameList.yview)
        
        
        
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
        
        
    def addSource(self,event):
        
        dataDir = filedialog.askdirectory()
        #fname = QFileDialog.getOpenFileName(None, 'Open file', 'c:\\',"Image files (*.jpg *.gif *.png *.bmp)")
        #dir = fname[0].rsplit('/', 1)[0]
        self.sourceList.insert("end",dataDir)
        
        
        for file in os.listdir(dataDir):
            self.frameList.insert("end",file)
                
        #self.frameList.activate(0)
        #self.classList.selection_set(0)
        #self.frameList.activate(0)
        #self.frameList.selection_set(0)
        
        self.currSource = dataDir
        self.currFrame = self.frameList.get(0)
        
        self.loadImg()
        
        
    def removeSource(self,event):
        
        self.sourceList.delete("anchor")
        
        
    
    def maskBind(self,event):
        self.bind('<Motion>', self.masking)
        self.mode = "mask"
            
    def boxBind(self,event):
        self.bind('<Motion>', lambda event, point="motion": 
                            self.boxing(event,point))
        self.mode = "box"
    
            
    def nextFrame(self,event):
        
        curr = self.frameList.get(0, "end").index(self.currFrame)+1
        self.frameList.selection_clear(0, "end")
        self.frameList.selection_set(curr)
        self.currFrame = self.frameList.get(curr)
        self.loadImg()
        
        
    def previousFrame(self,event):
        curr = self.frameList.get(0, "end").index(self.currFrame)-1
        self.frameList.selection_clear(0, "end")
        self.frameList.selection_set(curr)
        self.currFrame = self.frameList.get(curr)
        self.loadImg()
        
        
    def saveFrame(self, event): 
        x=self.canvas.winfo_rootx()+self.canvas.winfo_x()
        y=self.canvas.winfo_rooty()+self.canvas.winfo_y()
        x1=x+self.canvas.winfo_width()
        y1=y+self.canvas.winfo_height()
        bb=(x,y,x1,y1)
        self.grabcanvas = ImageGrab.grab(bbox=bb).save("out_snapsave.jpg")
        
        
        
    def loadImg(self):
        path = f"{self.currSource}/{self.currFrame}"
        #print(path)

        self.pilImg = Image.open(path)
        iW,iH = self.pilImg.size
        
        sW, sH = self.winfo_screenwidth(), self.winfo_screenheight()
        ratio = min((sW*0.9)/iW, (sH*0.9)/iH) 
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
        
        
    
    def addtotxt(self,type):
        file=f"{self.currSource}/{self.currFrame.split('.')[0]}_{type}.txt" 
        str=""
        with open(file, 'w') as filetowrite:
            for obj in self.objects:
                if obj[1]==type:
                    str = str + F"{obj[0]},{obj[2]},{obj[3]}\n"
            filetowrite.write(str)
                
        
        
        
    def masking(self,event):
        self.setClass()
        if self.annotating:
            if self.clicked:
                x, y = event.x, event.y
                self.currentMask.append([x,y])
                self.canvas.create_polygon(self.currentMask, fill=self.color)
            else:
                if len(self.currentMask) > 0:
                    poly = self.canvas.create_polygon(self.currentMask, fill=self.color)
                    tmpMaskObj = []
                    for point in self.currentMask:
                        tmpMaskObj.append([round(point[0]/self.xRat,2),round(point[1]/self.yRat,2)])
                            
                    self.objects.append((self.objectList.size(),"mask",self.currClass.split(' ')[0],tmpMaskObj))
                    self.currentMask = []
                    self.objectList.insert("end",(self.objectList.size(),"mask",self.currClass.split(' ')[0]))
                    self.addtotxt("mask")     # For generating .txt file
                # if self.canvas.old_mask_coords:
                #     x1, y1 = self.canvas.old_mask_coords
                #     self.canvas.create_oval(x-5, y-5,x+5 , y+5, fill='#000000')
                # self.canvas.old_mask_coords = x, y
            
            
            
    def boxing(self,event,point):
        if self.annotating:
                    
            if point == "click":
                x, y = event.x, event.y
                self.canvas.old_box_coords = x, y
            elif point =="release":
                self.setClass()
                self.canvas.delete(self.canvas_tmp_box)
                nX, nY = event.x, event.y
                oX,oY = self.canvas.old_box_coords
                boxy = self.create_rectangle(oX,oY,nX,nY,width=2,fill=self.color, alpha=.2)
                rectCoord = f"{round(oX/self.xRat,2)},{round(oY/self.yRat,2)},{round(nX/self.xRat,2)},{round(nY/self.yRat,2)}"
                self.objectList.insert("end",(self.objectList.size(),"box",self.currClass.split(' ')[0]))
                self.objects.append((self.objectList.size(),"box", self.currClass.split(' ')[0],rectCoord))
                self.addtotxt("box")     # For generating .txt file

            elif point == "motion":
                if self.canvas.old_box_coords:
                    self.setClass()
                    nX, nY = event.x, event.y
                    oX,oY = self.canvas.old_box_coords
                    if self.canvas_tmp_box:
                        self.canvas.delete(self.canvas_tmp_box)
                    self.canvas_tmp_box = self.canvas.create_rectangle(oX,oY,nX,nY,outline=self.color,width=1)
                    
            
    def setClass(self):
        self.currClass = self.classList.get(self.classList.curselection())
        self.color = self.currClass.split(' ')[2]
        
    
    def mouseClicked(self,event):
        if self.annotating:
            #print(self.classList.curselection())
            if self.clicked == True:
                self.clicked = False
                self.canvas.old_coords = None
                
                if self.mode == "box":
                    self.boxing(event,"release")
                    self.canvas.old_box_coords = None
    
            else:
                self.clicked = True
                if self.mode == "box":
                    self.boxing(event,"click")
        
        
        
    def create_rectangle(self, x1, y1, x2, y2, **kwargs):
        if 'alpha' in kwargs:
            alpha = int(kwargs.pop('alpha') * 255)
            fill = kwargs.pop('fill')
            fill = root.winfo_rgb(fill) + (alpha,)
            image = Image.new('RGBA', (abs(x2-x1), abs(y2-y1)), fill)
            self.images.append(ImageTk.PhotoImage(image))
            self.canvas.create_image(min(x1,x2), min(y1,y2), image=self.images[-1], anchor='nw')
        #self.canvas.create_rectangle(x1, y1, x2, y2, **kwargs)
    
if __name__=="__main__":
    
    root = Root()
    #root = Tk()
    #top = tk.Toplevel(root)
    root.iconbitmap("icon.ico")
    root.title("Multi Source Labeller")
    #top.withdraw()
    root.mainloop()
    