import openpyxl
from pylogix import PLC

# Open the workbook
wb = openpyxl.load_workbook('tagsLogix.xlsx')

# Select the sheet
sheet = wb['Sheet1']

# Select the column you want to read
column = sheet['A']

# Extract the tags from the A column, removing the column header
tag_names = [cell.value for cell in sheet['A'] if cell.value][1:]

# Connect to the PLC
plc = PLC()
plc.IPAddress = '192.168.123.100'
plc.ProcessorSlot = 2

###### Option 1: Individual Read
values = [plc.Read(tag_name).Value for tag_name in tag_names]

###### Option 2: Multi Read
values =[t.Value for t in plc.Read(tag_names)]

# Disconnect from the PLC
plc.Close()

# Write the values to the next column
for i, value in enumerate(values):
    sheet.cell(row=i+2, column=2).value = value

# Save the workbook
wb.save('tagsLogix.xlsx')