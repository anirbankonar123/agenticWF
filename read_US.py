import json
file1 = open("MyFile.txt", "r")

str = file1.read()

print(str)

str=str[7:-4]

json_list = []
json_list.append(json.loads(str))

print(json_list[0][5]['UserStory'])
print(json_list[0][5]['RequirementID'])
print(json_list[0][5]['Description'])
print(json_list[0][5]['AcceptanceCriteria'])

