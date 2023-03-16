import l5x

# Setup File Names
fileName = "PLC01.L5X"
saveFileName = fileName.split(".")[0] + "_Edited.L5X"

# Load the L5X file
prj = l5x.Project(fileName)

# Create a list of dictionaries for the tags
fullTagDataList = []

# Iterate over the tags
for tag in prj.controller.tags.names:
    # Get Tag Description and update it
    try:
        desc = prj.controller.tags[tag].description
    except:
        pass
    else:
        oldText = "" if desc == None else desc
        prj.controller.tags[tag].description = "New Text Portion " + oldText

# Save to a new L5X file
prj.write(saveFileName)
