import tkinter as tk
from tkinter import ttk
from ttkthemes import ThemedTk
from pylogix import PLC
import time
import threading
from PIL import ImageGrab
import cv2
import pytesseract
from pytesseract import Output

class PeriodicInterval(threading.Thread):
    def __init__(self, task_function, period):
        super().__init__()
        self.daemon = True
        self.task_function = task_function
        self.period = period
        self.i = 0
        self.t0 = time.time()
        self.stopper = 0
        self.start()

    def sleep(self):
        self.i += 1
        delta = self.t0 + self.period * self.i - time.time()
        if delta > 0:
            time.sleep(delta)

    def run(self):
        while self.stopper == 0:
            self.task_function()
            self.sleep()

    def stop(self):
        self.stopper = 1

# Setup PLC Comms
comm = PLC()
comm.IPAddress = "192.168.123.100"
comm.ProcessorSlot = 2

# Setup GUI
root = ThemedTk(theme="yaru")
root.title("Python GUI for ControlLogix")
root.state("zoomed")
frameMain = ttk.Frame(root)
frameMain.pack(expand=True, fill="both")
# Add Canvas
canvasHome = tk.Canvas(frameMain)
canvasHome.pack(side="left", fill="both", expand=True)
frameHome = ttk.Frame(frameMain)
frameHome.pack(side="right", fill="both", expand=True)
# Add GUI variables
runTimeText = tk.IntVar(value=0)
convertedText = tk.StringVar(value="")
# Add button
button_clear = ttk.Button(frameHome, text="Clear", command=lambda: [clear()])
button_clear.grid(row=0, column=0, columnspan=1, padx=10, pady=3, sticky="NESW")
# Add Labels
ttk.Label(frameHome, text="").grid(row=1, column=0, padx=10, pady=3, sticky="W")
ttk.Label(frameHome, text="").grid(row=2, column=0, padx=10, pady=3, sticky="W")
ttk.Label(frameHome, text="Run Time: ").grid(row=3, column=0, padx=10, pady=3, sticky="E")
ttk.Label(frameHome, textvariable=runTimeText).grid(row=3, column=1, padx=10, pady=3, sticky="W")
ttk.Label(frameHome, text="Drawing to Text: ").grid(row=4, column=0, padx=10, pady=3, sticky="E")
ttk.Label(frameHome, textvariable=convertedText).grid(row=4, column=1, padx=10, pady=3, sticky="W")

def start():
    # Write Start command to PLC and start loop to read RunTime
    global loop_record
    ret = comm.Write([("Start", 1), ("Stop", 0)])
    loop_record = PeriodicInterval(getData, 0.5)

def stop():
    # Write Stop command to PLC and stop loop
    ret = comm.Write([("Start", 0), ("Stop", 1)])
    loop_record.stop()

def getData():
    # Read current RunTime from PLC and update GUI
    liveData = comm.Read("RunTime")
    runTimeText.set(liveData.Value)

def get_x_and_y(event):
    # Mouse Pointer Location
    global lastx, lasty
    lastx, lasty = event.x, event.y

def draw_smth(event):
    # Draw line at Mouse Pointer Location
    global lastx, lasty
    canvasHome.create_line((lastx, lasty, event.x, event.y), fill="black", width=4)
    lastx, lasty = event.x, event.y

def get_image(widget):
    # Take a snapshot of the canvas and save image
    x = root.winfo_rootx() + widget.winfo_x()
    y = root.winfo_rooty() + widget.winfo_y()
    x1 = x + widget.winfo_width()
    y1 = y + widget.winfo_height()
    ImageGrab.grab().crop((x, y, x1, y1)).save("canvasImage.jpg")

def clear():
    canvasHome.delete("all")
    convertedText.set("")

def convert(event):
    # Read the saved image and covert the image to a string
    get_image(canvasHome)
    img = cv2.imread("canvasImage.jpg")
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    cmdText = pytesseract.image_to_string(img, lang="eng").strip()
    convertedText.set(cmdText)
    if "Start" in cmdText or "start" in cmdText:
        start()
    elif "Stop" in cmdText or "stop" in cmdText:
        stop()

# Left-Click to start drawing
canvasHome.bind("<Button-1>", get_x_and_y)
# Left-Click held down and motion adds drawing to canvas
canvasHome.bind("<B1-Motion>", draw_smth)
# Right-Click or Middle-Click triggers convert function
canvasHome.bind("<Button-2>", convert)
canvasHome.bind("<Button-3>", convert)

root.mainloop()
