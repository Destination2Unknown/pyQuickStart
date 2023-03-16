import pandas as pd
import l5x

# Setup File Names
fileName = "PLC01.L5X"
saveFileName = fileName.split(".")[0] + "_tags.xlsx"

# Load the L5X file
prj = l5x.Project(fileName)

# Create a list of dictionaries for the tags
fullTagDataList = []

# Iterate over the tags
for tag in prj.controller.tags.names:
    # Get Tag Name and Data Type
    try:
        dt = prj.controller.tags[tag].data_type
    except:
        fullTagDataList.append({"Name": tag, "Data Type": "Unknown"})
    else:
        fullTagDataList.append({"Name": tag, "Data Type": dt})

    # Get Description
    try:
        desc = prj.controller.tags[tag].description
    except:
        fullTagDataList[-1]["Description"] = "Unknown"
    else:
        fullTagDataList[-1]["Description"] = desc

# Convert the list of dictionaries to a DataFrame
df = pd.DataFrame(fullTagDataList)

# Save the DataFrame to an Excel file
df.to_excel(saveFileName, index=False)
