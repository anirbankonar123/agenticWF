import google.generativeai as genai
from langchain_community.document_loaders import PyPDFLoader
import json

fileName = "IFB-CO-15079-IAS_Final-PART-2.pdf"
loader = PyPDFLoader(fileName)

pages = loader.load_and_split()

print(len(pages))
text = ""
for page in pages:
    text+=page.page_content

#Prompt to get related requirements for a requirement header
def make_prompt_Reqmnt_to_US(reqmnt, context):
  escaped = context.replace("'", "").replace('"', "").replace("\n", " ")
  prompt = ("""You are an expert Domain specialist who can find out relevant Requirements from 
  the Requirement Header given, using text from the context included below. \
  Generate the User stories for all requirement IDs under this Requirement Header. \
  Be sure to include the User Story, Requirement ID, the Description with flows, Acceptance criteria in detail for each Requirement ID. \
  Map each requirement ID to one User Story strictly, do not combine Requirement IDs into one User Story.\
  Return the information in JSON structure with an array of User stories.\
  give the output in a valid json format.\
  Requirement header : '{reqmnt}'
  Context: '{context}'

  ANSWER:
  """).format(reqmnt=reqmnt,context=escaped)

  return prompt

genai.configure()
model = genai.GenerativeModel('gemini-1.5-pro')
context = text

temperature=1.5
top_p=1.0

reqmnt="Search"
prompt = make_prompt_Reqmnt_to_US(reqmnt, context)
response = model.generate_content(prompt,
    generation_config=genai.types.GenerationConfig(
        temperature=float(temperature),
        top_p=float(top_p))
)

print(response.text)

file1 = open("MyFile.txt", "w")
file1.write(response.text)
file1.close()