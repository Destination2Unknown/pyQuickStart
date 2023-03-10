import openpyxl
from asyncua.sync import Client,ua

excelFileName = 'tagsOPC.xlsx'

# Open the workbook
wb = openpyxl.load_workbook(excelFileName)

# Select the sheet
sheet = wb['Sheet1']

# Select the column you want to read
column = sheet['A']

# Extract the tags from the A column, removing the column header
tag_names = [cell.value for cell in sheet['A'] if cell.value][1:]

# Connect to the PLC
plc = Client("opc.tcp://192.168.123.100:49320")
plc.connect()

# Get OPC tag names
tag_names = [plc.get_node(t) for t in tag_names]

###### Option 1: Individual Read
values = [t.read_value() for t in tag_names]

###### Option 2: Multi Read
values = [v for v in plc.read_values(tag_names)]

# Disconnect from the PLC
plc.disconnect()

# Write the values to the next column
for i, value in enumerate(values):
    sheet.cell(row=i+2, column=2).value = value

# Save the workbook
wb.save(excelFileName)