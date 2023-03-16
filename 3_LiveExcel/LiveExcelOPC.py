import xlwings as xw
import time
from asyncua.sync import Client, ua

# Define Defaults
fileName = "LiveExcelOPC.xlsx"

# Connect to PLC
OPCAddr = "opc.tcp://192.168.123.100:49320"
plc = Client(OPCAddr)
plc.connect()

# Open WorkBook
wb = xw.Book(fileName)
sht1 = wb.sheets["Sheet1"]

# Read and Write Values
for x in range(600):
    plc.get_node(sht1.range("A2").value).write_value(ua.DataValue(bool(sht1.range("B2").value)))
    plc.get_node(sht1.range("A3").value).write_value(ua.DataValue(bool(sht1.range("B3").value)))
    time.sleep(0.1)
    sht1.range("B4").value = plc.get_node(sht1.range("A4").value).read_value()

# Disconnect from PLC
plc.disconnect()
