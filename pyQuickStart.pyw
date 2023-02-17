import tkinter as tk
from tkinter import ttk
from pylogix import PLC
from asyncua.sync import Client,ua
from ttkthemes import ThemedTk

defaultIPAddress="192.168.123.100"
defaultSlot=2
defaultOPCAddress="opc.tcp://192.168.123.100:49320"
defaultLogixTagName="myReal"
defaultOPCTagName="ns=2;s=Channel1.Device1.myReal"

class GUI(object):
    def __init__(self):
        #Tkinter Setup
        self.root = ThemedTk(theme='yaru')
        self.root.title("pyQuickStart")
        self.root.state('zoomed')
        self.frameMain = ttk.Frame(self.root)
        self.frameMain.pack(expand=True, fill="both")
        #Add frames
        self.frameTags=ttk.LabelFrame(self.frameMain,padding=15,text="Tag Setup")
        self.frameTags.grid(row=0, column=0, padx=10,pady=10, sticky="NESW")
        self.frameComms=ttk.LabelFrame(self.frameMain,padding=15,text="Comms Setup")
        self.frameComms.grid(row=1, column=0, padx=10,pady=10, sticky="NESW")
        self.widgetsTagsFrame()
        self.widgetsCommsFrame()

    def widgetsTagsFrame(self):
        #Static Labels
        ttk.Label(self.frameTags, text="Tag Address").grid(row=0,column=0,padx=10,pady=10,sticky="W")
        ttk.Label(self.frameTags, text="Value").grid(row=0,column=1,padx=10,pady=10)
        ttk.Label(self.frameTags, text="Actual Value").grid(row=0,column=2,padx=10,pady=10)
        ttk.Label(self.frameTags, text="Status").grid(row=0,column=3,padx=10,pady=10)
        #Tag Name
        self.tagName=tk.StringVar(value=defaultLogixTagName)
        self.tagNameEntry = ttk.Entry(self.frameTags, width=40,textvariable=self.tagName)
        self.tagNameEntry.grid(row=1,column=0,padx=10,pady=10)
        #Value to Write
        self.writeValue=tk.DoubleVar(value=0.0)
        self.writeValueEntry = ttk.Entry(self.frameTags, width=10,textvariable=self.writeValue,justify='center')
        self.writeValueEntry.grid(row=1,column=1,padx=10,pady=10)
        #Actual Value and Status
        self.tagValue=tk.StringVar(value="")
        ttk.Label(self.frameTags, textvariable=self.tagValue).grid(row=1,column=2,padx=10,pady=10)
        self.tagStatus=tk.StringVar(value="")
        ttk.Label(self.frameTags, textvariable=self.tagStatus).grid(row=1,column=3,padx=10,pady=10)
        #Buttons Setup
        self.buttonWrite = ttk.Button(self.frameTags, text="Write to PLC", command=lambda :[self.writeData()])
        self.buttonWrite.grid(row=3,column=1,padx=10,pady=10,sticky="NESW")
        self.buttonRead = ttk.Button(self.frameTags, text="Read from PLC", command=lambda :[self.readData()])
        self.buttonRead.grid(row=3,column=2,padx=10,pady=10,sticky="NESW")
        self.buttonReset = ttk.Button(self.frameTags, text="Reset", command=lambda :[self.reset()])
        self.buttonReset.grid(row=3,column=3,padx=10,pady=10,sticky="NESW")

    def widgetsCommsFrame(self):
        #Comms Setup
        ttk.Label(self.frameComms, text="PLC Address:").grid(row=0,column=0,padx=10,pady=10,sticky="E")
        self.plcAddress=tk.StringVar(value=defaultIPAddress)
        self.addressEntry = ttk.Entry(self.frameComms, width=40,textvariable=self.plcAddress)
        self.addressEntry.grid(row=0,column=1,padx=10,pady=10,sticky="W")
        #Slot
        ttk.Label(self.frameComms, text="Slot:").grid(row=1,column=0,padx=10,pady=10,sticky="E")
        self.plcSlot=tk.IntVar(value=defaultSlot)
        self.slotEntry = ttk.Entry(self.frameComms, width=5,textvariable=self.plcSlot)
        self.slotEntry.grid(row=1,column=1,padx=10,pady=10,sticky="W")
        #Error Note
        self.guiErrorNote=tk.StringVar(value="")
        ttk.Label(self.frameComms, textvariable=self.guiErrorNote).grid(row=2,column=0,columnspan=3,padx=10,pady=10,sticky="W")
        #Radio Buttons
        self.radioSelector=tk.StringVar(value="Logix")
        self.radiobuttonLogix=ttk.Radiobutton(self.frameComms, text = "Logix", variable=self.radioSelector, command=self.pickLogix, value = "Logix")
        self.radiobuttonLogix.grid(row=0,column=2, padx=10,pady=10)
        self.radiobuttonOPC=ttk.Radiobutton(self.frameComms, text = "OPC-UA", variable=self.radioSelector,command=self.pickOPC, value = "OPC")
        self.radiobuttonOPC.grid(row=0,column=3, padx=10,pady=10)

    def readData(self):
        try:
            if self.radioSelector.get()=="Logix":
                tag=self.tagName.get()
                self.comm=PLC()
                self.comm.IPAddress=self.plcAddress.get()
                self.comm.ProcessorSlot=self.plcSlot.get()
                ret=self.comm.Read(tag)
                self.tagValue.set(ret.Value if ret.Value==None else round(ret.Value,2))
                self.tagStatus.set(ret.Status)
                self.comm.Close()
        
            else:
                tag=self.tagName.get()
                self.comm=Client(self.plcAddress.get())
                self.comm.connect()
                ret=self.comm.get_node(tag).read_value()
                self.tagValue.set(ret if ret==None else round(ret,2))
                self.tagStatus.set("Error" if ret==None else "Success")
                self.comm.disconnect()

        except Exception as e:
            self.guiErrorNote.set(str(e))

    def writeData(self):
        try:
            if self.radioSelector.get()=="Logix":
                tag=self.tagName.get()
                val=self.writeValue.get()                
                self.comm=PLC()
                self.comm.IPAddress=self.plcAddress.get()
                self.comm.ProcessorSlot=self.plcSlot.get()
                ret=self.comm.Write(tag,val)
                self.tagValue.set(ret.Value if ret.Value==None else round(ret.Value,2))
                self.tagStatus.set(ret.Status)
                self.comm.Close()

            else:
                tag=self.tagName.get()
                val=self.writeValue.get()  
                self.comm=Client(self.plcAddress.get())
                self.comm.connect()
                self.comm.get_node(tag).write_value(ua.DataValue(float(val)))
                ret=self.comm.get_node(tag).read_value()
                self.tagValue.set(ret if ret==None else round(ret,2))
                self.tagStatus.set("Error" if ret==None else "Success")
                self.comm.disconnect()

        except Exception as e:
            self.guiErrorNote.set(str(e))

    def reset(self):
        self.tagValue.set("")
        self.tagStatus.set("")
        self.guiErrorNote.set("")
        self.writeValue.set(0.0)

    def pickLogix(self):
        self.plcAddress.set(defaultIPAddress)
        self.plcSlot.set(defaultSlot)
        self.tagName.set(defaultLogixTagName)

    def pickOPC(self):
        self.plcAddress.set(defaultOPCAddress)
        self.plcSlot.set(0)
        self.tagName.set(defaultOPCTagName)

gui=GUI()
gui.root.mainloop()