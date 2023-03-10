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
# Extract the values from the B column, removing the column header
tag_values = [cell.value for cell in sheet['B'] if cell.value][1:]

# Connect to the PLC
plc = Client("opc.tcp://192.168.123.100:49320")
plc.connect()

# Combine Tag Name with Tag Values
tagNodes = [plc.get_node(t) for t in tag_names]
tagDataTypes = [t.get_data_type_as_variant_type() for t in tagNodes]
# UA format values
tagUA = [ua.DataValue(ua.Variant(v,dt)) for v,dt in list(zip(tag_values,tagDataTypes))]

###### Option 1: Individual Write
# Combine Tags with UA format value
tagsWithValue = list(zip(tagNodes,tagUA))
values = [t.write_value(v) for t,v in tagsWithValue]

###### Option 2: Multi-Write
values = plc.write_values(tagNodes,tagUA)

# Disconnect from the PLC
plc.disconnect()