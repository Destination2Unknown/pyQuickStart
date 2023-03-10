import openpyxl
from pylogix import PLC

excelFileName = 'tagsLogix.xlsx'

# Open the workbook
wb = openpyxl.load_workbook(excelFileName)

# Select the sheet
sheet = wb['Sheet1']

# Extract the tags from the A column, removing the column header
tag_names = [cell.value for cell in sheet['A'] if cell.value][1:]
# Extract the values from the B column, removing the column header
tag_values = [cell.value for cell in sheet['B'] if cell.value][1:]

# Connect to the PLC
plc = PLC()
plc.IPAddress = '192.168.123.100'
plc.ProcessorSlot = 2
plc.SocketTimeout = 2.5

# Combine Tag Name with Tag Values
tagsWithValue = list(zip(tag_names,tag_values))

###### Option 1: Individual Write
values = [plc.Write(t,v) for t,v in tagsWithValue]

###### Option 2: Multi-Write
values = plc.Write(tagsWithValue)

# Disconnect from the PLC
plc.Close()