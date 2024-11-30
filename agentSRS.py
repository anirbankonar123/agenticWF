import os
import yaml
from crewai import Agent, Task, Crew
from typing import List
from pydantic import BaseModel, Field

# os.environ['OPENAI_MODEL_NAME'] = 'gpt-4o-mini'

# Define file paths for YAML configurations
files = {
    'agents': 'config_1/agents.yaml',
    'tasks': 'config_1/tasks.yaml'
}

# Load configurations from YAML files
configs = {}
for config_type, file_path in files.items():
    with open(file_path, 'r') as file:
        configs[config_type] = yaml.safe_load(file)

# Assign loaded configurations to specific variables
agents_config = configs['agents']
tasks_config = configs['tasks']

# class TestCase(BaseModel):
#     pre_requisites: List[str] = Field(..., description="Pre-requisite for the Test Case")
#     steps: List[str] = Field(..., description="List of steps for the Test Case")
#     expected_results: List[str] = Field(..., description="List of expected results")


# Creating Agents
quality_assurance_agent = Agent(
  config=agents_config['quality_assurance_agent']
)


test_cases = Task(
  config=tasks_config['testcase_generation'],
  agent=quality_assurance_agent
)

industry = 'Technology'

# Creating Crew
crew = Crew(
  agents=[
    quality_assurance_agent,

  ],
  tasks=[
    test_cases,
  ],
  verbose=True
)

import json
file1 = open("MyFile.txt", "r")

str = file1.read()
str=str[7:-4]

json_list = []
json_list.append(json.loads(str))

print(json_list[0][0]['Requirement ID'])
print(json_list[0][0]['Description'])
print(json_list[0][0]['Acceptance Criteria'])

user_story = json_list[0][0]['Requirement ID']
description = json_list[0][0]['Description']
acceptance_criteria = json_list[0][0]['Acceptance Criteria']

# The given Python dictionary
inputs = {
  'industry': industry,
  'user_story' : user_story,
  'description': description,
  'acceptance_criteria':acceptance_criteria
}

# Run the crew
crew_output = crew.kickoff(
  inputs=inputs
)


# Accessing the crew output
print(f"Raw Output: {crew_output.raw}")
if crew_output.json_dict:
    print(f"JSON Output: {json.dumps(crew_output.json_dict, indent=2)}")
if crew_output.pydantic:
    print(f"Pydantic Output: {crew_output.pydantic}")
print(f"Tasks Output: {crew_output.tasks_output}")
print(f"Token Usage: {crew_output.token_usage}")

file1 = open("TC.txt", "w")
file1.write(crew_output.raw[7:-4])
file1.close()