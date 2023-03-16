import xlwings as xw
import time
from pycomm3 import LogixDriver

# Define Defaults
fileName = "LiveExcelLogix.xlsx"

# Connect to PLC
IPAddr = "192.168.123.100"
Slot = "2"
plc = LogixDriver(IPAddr + "/" + Slot)
plc.open()

# Open WorkBook
wb = xw.Book(fileName)
sht1 = wb.sheets["Sheet1"]

# Read and Write Values
for x in range(600):
    plc.write(sht1.range("A2").value, sht1.range("B2").value)
    plc.write(sht1.range("A3").value, sht1.range("B3").value)
    time.sleep(0.1)
    sht1.range("B4").value = plc.read(sht1.range("A4").value).value

# Disconnect from PLC
plc.close()
