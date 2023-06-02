import threading
import time
import winreg
import ttkbootstrap as ttk
from ttkbootstrap.scrolled import ScrolledFrame
from pycomm3 import LogixDriver


class AutocompleteCombobox(ttk.Combobox):
    def __init__(self, parent, values, **kwargs):
        super().__init__(parent, **kwargs)
        self.values = values
        self.configure(values=self.values)
        self.bind("<KeyRelease>", self.autocomplete)

    def autocomplete(self, event):
        """
        Filter tag values
        """
        current_text = self.get()
        matching_values = [value for value in self.values if current_text.lower() in value.lower()]
        self.configure(values=matching_values)


class PeriodicInterval(threading.Thread):
    def __init__(self, task_function, period):
        super().__init__()
        self.daemon = True
        self.task_function = task_function
        self.period = period
        self.i = 0
        self.t0 = time.time()
        self.stopper = threading.Event()
        self.start()

    def sleep(self):
        self.i += 1
        delta = self.t0 + self.period * self.i - time.time()
        if delta > 0:
            self.stopper.wait(delta)

    def run(self):
        while not self.stopper.is_set():
            self.task_function()
            self.sleep()

    def stop(self):
        self.stopper.set()

    def starter(self):
        self.stopper.clear()
        self.i = 0
        self.t0 = time.time()


class GUIApp(object):
    def __init__(self):
        # Setup defaults
        self.rows = []
        self.comm = None
        self.cyclicThread = None
        # Setup Window
        self.root = ttk.Window()
        self.root.state("zoomed")
        self.root.title("pyQuickWatch")
        try:
            style = ttk.Style()
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize")
            subkeyLightMode = winreg.QueryValueEx(key, "AppsUseLightTheme")[0]
            if subkeyLightMode:
                style.theme_use("yeti")
            else:
                style.theme_use("vapor")
        except:
            pass

        # Create the two frames
        self.frameControl = ttk.LabelFrame(self.root, text=" Control ", padding=10, bootstyle="primary")
        self.frameControl.pack(side="left", fill="both", expand=False, padx=10, pady=10)
        self.frameWatch = ttk.LabelFrame(self.root, text=" Watch Window ", padding=10, bootstyle="primary")
        self.frameWatch.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        self.watchPane = ScrolledFrame(self.frameWatch, autohide=False)
        self.watchPane.pack(fill="both", expand=True)
        self.frameTable = ttk.Frame(self.watchPane)
        self.frameTable.pack(fill="x", padx=(0, 10))
        self.frameAddRemove = ttk.Frame(self.watchPane)
        self.frameAddRemove.pack(fill="x")

        ## Control Frame
        # Open File Button Placement
        self.button_connect = ttk.Button(self.frameControl, text="Connect", command=lambda: [self.connect_to_PLC()])
        self.button_connect.grid(row=0, column=0, columnspan=1, padx=10, pady=10, sticky="NESW")
        # Check Config Button Placement
        self.button_start = ttk.Button(self.frameControl, text="Start", bootstyle="success", command=lambda: [self.start()])
        self.button_start.grid(row=1, column=0, columnspan=1, padx=10, pady=10, sticky="NESW")
        # Read Button Placement
        self.button_stop = ttk.Button(self.frameControl, bootstyle="warning", text="Stop", command=lambda: [self.stop()])
        self.button_stop.grid(row=2, column=0, columnspan=1, padx=10, pady=10, sticky="NESW")
        # Write Button Placement
        self.button_reset = ttk.Button(self.frameControl, bootstyle="danger", text="Reset", command=lambda: [self.reset()])
        self.button_reset.grid(row=3, column=0, columnspan=1, padx=10, pady=10, sticky="NESW")

        # Scale
        ttk.Label(self.frameControl, text="Fast Refresh Rate").grid(row=4, column=0, padx=10, pady=10, sticky="NESW")
        self.refreshRate = ttk.DoubleVar(value=1.0)
        self.refreshRateSlider = ttk.Scale(self.frameControl, bootstyle="primary", orient="vertical", variable=self.refreshRate, from_=0.001, to=2.0)
        self.refreshRateSlider.grid(row=5, column=0, rowspan=5, padx=10, pady=10, sticky="NESW")
        ttk.Label(self.frameControl, text="Slow Refresh Rate").grid(row=10, column=0, padx=10, pady=10, sticky="NESW")

        # Separator
        ttk.Separator(self.frameControl, bootstyle="secondary", orient="horizontal").grid(row=11, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

        # Setup GUI tags
        self.ipAddress = ttk.StringVar()
        self.plcSlot = ttk.StringVar()
        self.status = ttk.StringVar()

        # PLC Comms
        ttk.Label(self.frameControl, text="IP Address:").grid(row=12, column=0, padx=10, pady=10, sticky="NESW")
        self.ipEntryBox = ttk.Entry(self.frameControl, textvariable=self.ipAddress, bootstyle="primary", width=15)
        self.ipEntryBox.grid(row=12, column=1, padx=4, pady=3, sticky="W")
        ttk.Label(self.frameControl, text="Slot:").grid(row=13, column=0, padx=10, pady=10, sticky="NESW")
        self.slotEntryBox = ttk.Entry(self.frameControl, textvariable=self.plcSlot, bootstyle="primary", width=3)
        self.slotEntryBox.grid(row=13, column=1, padx=4, pady=3, sticky="W")
        # Status
        ttk.Label(self.frameControl, text="Status:").grid(row=14, column=0, padx=10, pady=10, columnspan=6, sticky="W")
        ttk.Label(self.frameControl, textvariable=self.status, bootstyle="danger", wraplength=100, width=20).grid(row=14, column=1, padx=10, pady=10, columnspan=1, sticky="W")

        # Create a button to add another row
        self.button_add = ttk.Button(self.frameAddRemove, text="Add New Row", command=self.add_row)
        self.button_add.pack(side="left", padx=5, pady=5)

        # Create a button to remove the last row
        self.button_remove = ttk.Button(self.frameAddRemove, text="Remove Last Row", command=self.remove_row)
        self.button_remove.pack(side="left", padx=5, pady=5)
        self.button_remove.configure(state="disabled")
        # Reset GUI at startup
        self.reset()

    def connect_to_PLC(self):
        """
        Connect to PLC and get the tag list
        """
        self.status.set("")
        self.button_connect.configure(state="disabled")
        try:
            self.comm = LogixDriver(self.ipAddress.get() + "/" + self.plcSlot.get())
            self.comm.open()
            self.fullBaseTagList = get_all_tags(self.comm.tags)
            for row in self.rows:
                row[4].configure(values=self.fullBaseTagList)
                row[4].values = self.fullBaseTagList

        except Exception as e:
            self.status.set(str(e))
            self.button_connect.configure(state="normal")
        else:
            self.button_start.configure(state="normal")
            self.button_reset.configure(state="normal")
            self.ipEntryBox.configure(state="disabled")
            self.slotEntryBox.configure(state="disabled")

    def start(self):
        """
        Setup the timeout, read the tags once and get the data type
        """
        self.status.set("")
        self.button_start.configure(state="disabled")
        try:
            # Generate a tagList
            self.tagList = []
            for row in self.rows:
                if row[0].get():
                    self.tagList.append(row[0].get())
            # If the taglist is empty raise exception otherwise remove empty rows
            if len(self.tagList) == 0:
                raise Exception("Empty Tag List")
            else:
                for i in range(len(self.rows) - 1, -1, -1):
                    if not self.rows[i][0].get():
                        self.rows[i][3].destroy()
                        self.rows.pop(i)
                    else:
                        self.rows[i][4].configure(state="disabled")
            # Set the timeout
            self.comm._sock.sock.settimeout(self.refreshRate.get() + 0.5)
            retData = self.comm.read(*self.tagList)
            ret = retData if isinstance(retData, list) else [retData]
            for i, row in enumerate(self.rows):
                row[1].set(ret[i].error if ret[i].value == None else ret[i].value)
                row[2].set(ret[i].type)
        except Exception as e:
            self.status.set(str(e))
            self.button_start.configure(state="normal")
            self.refreshRateSlider.configure(state="normal")
            for row in self.rows:
                row[4].configure(state="normal")
        else:
            self.button_stop.configure(state="normal")
            self.button_add.configure(state="disabled")
            self.button_remove.configure(state="disabled")
            self.refreshRateSlider.configure(state="disabled")
            self.cyclicThread = PeriodicInterval(self.loop_read, self.refreshRate.get())

    def loop_read(self):
        """
        Read the taglist from the PLC
        """
        try:
            retData = self.comm.read(*self.tagList)
            ret = retData if isinstance(retData, list) else [retData]
            for i, row in enumerate(self.rows):
                row[1].set(ret[i].error if ret[i].value == None else ret[i].value)
        except Exception as e:
            self.status.set(time.strftime("%H:%M:%S -> ") + str(e))

    def stop(self):
        """
        Stop the periodic thread and re-enable entry boxes
        """
        try:
            self.cyclicThread.stop()
            self.refreshRateSlider.configure(state="normal")
            for row in self.rows:
                row[4].configure(state="normal")
            self.button_add.configure(state="normal")
            if len(self.rows) > 1:
                self.button_remove.configure(state="normal")
        except Exception as e:
            self.status.set(str(e))
        finally:
            self.button_start.configure(state="normal")
            self.button_stop.configure(state="disabled")
            self.cyclicThread = None

    def reset(self):
        """
        Reset everything to start-up state
        """
        self.status.set("")
        self.ipAddress.set("192.168.123.100")
        self.plcSlot.set("2")
        self.button_connect.configure(state="normal")
        self.button_start.configure(state="disabled")
        self.button_stop.configure(state="disabled")
        self.button_reset.configure(state="disabled")
        self.refreshRateSlider.configure(state="normal")
        self.ipEntryBox.configure(state="normal")
        self.slotEntryBox.configure(state="normal")
        for widget in self.frameTable.winfo_children():
            widget.destroy()
        if self.comm:
            try:
                self.comm.close()
            except:
                pass
        if self.cyclicThread:
            self.cyclicThread.stop()
        self.comm = None
        self.cyclicThread = None
        self.rows = []
        self.fullBaseTagList = []
        self.add_row()
        self.button_add.configure(state="normal")
        self.button_remove.configure(state="disabled")

    def add_row(self):
        self.button_remove.configure(state="normal")
        # Create a new row with three entry boxes
        row_frame = ttk.Frame(self.frameTable)
        row_frame.pack(side="top", fill="x", padx=5, pady=5)

        tag_entry_var = ttk.StringVar()
        tag_entry = AutocompleteCombobox(row_frame, textvariable=tag_entry_var, values=self.fullBaseTagList)
        tag_entry.pack(side="left", padx=(0, 5), expand=True, fill="x")

        value_entry_var = ttk.StringVar()
        value_entry = ttk.Entry(row_frame, textvariable=value_entry_var, state="disabled")
        value_entry.pack(side="left", padx=(0, 5))

        datatype_entry_var = ttk.StringVar()
        datatype_entry = ttk.Entry(row_frame, textvariable=datatype_entry_var, state="disabled")
        datatype_entry.pack(side="left")

        # Add the new entry variables and row frame to the row list
        self.rows.append((tag_entry_var, value_entry_var, datatype_entry_var, row_frame, tag_entry))

    def remove_row(self):
        if len(self.rows) > 1:
            self.rows[-1][3].destroy()
            self.rows.pop()
        if len(self.rows) < 2:
            self.button_remove.configure(state="disabled")


def explode_struct(struct):
    """
    Breaks down a structure
    """
    exploded_tags = []
    for attr in struct["attributes"]:
        exploded_tags.append(attr)
        if struct["internal_tags"][attr]["tag_type"] == "struct":
            exploded_tags.extend(f"{attr}.{x}" for x in explode_struct(struct["internal_tags"][attr]["data_type"]))
    return exploded_tags


def get_all_tags(tags):
    """
    Takes in a list of Tags in dictionary format and returns a list of all tags
    """
    full_list_of_tags = []
    for tag, tag_data in tags.items():
        full_list_of_tags.append(tag)
        if tag_data["tag_type"] == "struct":
            full_list_of_tags.extend(f"{tag}.{attr}" for attr in explode_struct(tag_data["data_type"]))
    return full_list_of_tags


if __name__ == "__main__":
    pyQuickWatch = GUIApp()
    pyQuickWatch.root.mainloop()
