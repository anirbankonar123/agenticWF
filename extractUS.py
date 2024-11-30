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
user_stories=""
#Prompt to get related requirements for a requirement header
def make_prompt_Reqmnt_to_US(reqmnt, context, user_stories):
  escaped = context.replace("'", "").replace('"', "").replace("\n", " ")
  prompt = ("""You are an expert Requirement Analyst who can find out relevant Requirements from 
  the Requirement Header given, using text from the context included below. \
  Generate the User stories for all requirement IDs under this Requirement Header. \
  Do not leave out any Requirement ID for this Requirement.\
  Be sure to include the User Story, Requirement ID, the Description with flows, Acceptance criteria in detail for each Requirement ID. \
  Return the information in JSON structure with an array of User stories.\
  Ignore the already available User stories, and do not repeat them.\
  Generate the output in a strictly valid json format.\
  Requirement header : '{reqmnt}'
  User stories already available :{user_stories}
  Context: '{context}'

  ANSWER:
  """).format(reqmnt=reqmnt,context=escaped,user_stories=user_stories)

  return prompt

genai.configure()
model = genai.GenerativeModel('gemini-1.5-pro')
context = text

temperature=0
top_p=1.0

reqmnt="Search"
user_stories_list=[]

for i in range (1,3):
    print(str(i))
    prompt = make_prompt_Reqmnt_to_US(reqmnt, context, user_stories)
    response = model.generate_content(prompt,
        generation_config=genai.types.GenerationConfig(
            temperature=float(temperature),
            top_p=float(top_p))
    )
    user_stories = response.text[7:-4]
    print(user_stories)
    print("**************************************")
    user_stories_list.append(user_stories)

print(user_stories_list)

file1 = open("US.txt", "w")
file1.write("".join(user_stories_list))
file1.close()

#https://cloud.google.com/vertex-ai/generative-ai/docs/learn/models#gemini-1.5-pro