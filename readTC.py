import json
with open("TC_langgraph_8.txt", "r") as json_file:
    sample_load_file = json.load(json_file)
if (sample_load_file['generate']['revision_number'] == 4):
    print(sample_load_file['generate']['draft'])


