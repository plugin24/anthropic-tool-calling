from tools.tools import Tools
from dotenv import load_dotenv
import anthropic
import os
from langsmith import traceable

client = anthropic.Anthropic()

load_dotenv()

tree_map_tool = {
    "name": "tree_map",
    "description": "This function creates a map of all files in the codebase.",
    "input_schema": {
        "type": "object",
        "properties": {
            "root_dir": {
                "type": "string",
                "description": "path of the root directory of the codebase"
            },
            "exclude_folders": {
                "type": "array",
                "items": {
                    "type": "string"
                },
                "description": "Folders to be excluded while reading directory. eg. ['env', '.venv', 'purecode-env','vendor']"
            }
        },
        "required": ["root_dir", "excluded_folders"]
    }
}

read_files_tool = {
    "name" : "read_file",
    "description" : "This tool reads the content in the file",
    "input_schema" : {
        "type" : "object",
        "properties" : {
            "file_path" : {
                "type" : "string",
                "description" : "Path of the file which we want to read"
            }
        }
    },
    "required" : ["file_path"]
}

write_files_tool = {
    "name" : "write_file",
    "description" : "This tool helps in writing new content in the file, it overrites the original content",
    "input_schema" : {
        "type" : "object",
        "properties" : {
            "file_path" : {
                "type" : "string",
                "description" : "Path of the file which we want to read"
            },
            "file_contents" : {
                "type" : "string",
                "description" : "The contents that we want to write in the file."
            }
        }
    },
    "required" : ["file_path", "file_contents"]
}

# tool_info = {
#     {
#         "name": "tree_map",
#         "description": "This function creates a map of all files in the codebase.",
#         "input_schema": {
#             "type": "object",
#             "properties": {
#                 "root_dir": {
#                     "type": "string",
#                     "description": "path of the root directory of the codebase"
#                 },
#                 "exclude_folders": {
#                     "type": "array",
#                     "items": {
#                         "type": "string"
#                     },
#                     "description": "Folders to be excluded while reading directory. eg. ['env', '.venv', 'purecode-env','vendor']"
#                 }
#             },
#             "required": ["root_dir"]
#         }
#     },
#     {
#         "name" : "read_file",
#         "description" : "This tool reads the content in the file",
#         "input_schema" : {
#             "type" : "object",
#             "properties" : {
#                 "file_path" : {
#                     "type" : "string",
#                     "description" : "Path of the file which we want to read"
#                 }
#             }
#         },
#         "required" : ["file_path"]
#     },
#     {
#         "name" : "write_file",
#         "description" : "This tool helps in writing new content in the file, it overrites the original content",
#         "input_schema" : {
#             "type" : "object",
#             "properties" : {
#                 "file_path" : {
#                     "type" : "string",
#                     "description" : "Path of the file which we want to read"
#                 },
#                 "file_contents" : {
#                     "type" : "string",
#                     "description" : "The contents that we want to write in the file."
#                 }
#             }
#         },
#         "required" : ["file_path", "file_contents"]
#     }
# }

tools = Tools()

def process_tool_call(tool_name, tool_input):
    if tool_name == "tree_map":
        tree = tools.tree_map(tool_input["root_dir"], tool_input['exclude_folders'])
        return tree
    elif tool_name == "read_file":
        return tools.read_file(tool_input['file_path'])
    elif tool_name == "write_file":
        return tools.write_file(tool_input['file_path'], tool_input['file_contents'])

@traceable
def agent_smith():
    user_message = input("\nUser: ")
    messages = [{"role": "user", "content": user_message}]

    while True:
        #If the last message is from the assistant, get another input from the user
        if messages[-1].get("role") == "assistant":
            user_message = input("\nUser: ")
            if user_message == "exit":
                break
            messages.append({"role": "user", "content": user_message})

        system_message = "You are an AI coding assitant, your job is to find out the files that are necessary to change based on user's query. You have tools for this job, but you should only use them when its necessary, if the tool is not required, then don;t use it. Current working directory/root directory is - D:\claude-dev\claude-dev"
        response = client.messages.create(
            model="claude-3-5-sonnet-20240620",
            system=system_message,
            messages=messages,
            max_tokens=300,
            tools=[tree_map_tool]
        )

        print(response)
        print("#"*100)
        messages.append({"role": "assistant", "content": response.content})
        #If Claude stops because it wants to use a tool:
        if response.stop_reason == "tool_use":
            tool_use = response.content[-1] #Naive approach assumes only 1 tool is called at a time
            tool_name = tool_use.name
            tool_input = tool_use.input
            print(f"======Claude wants to use the {tool_name} tool======")
            #Actually run the underlying tool functionality on our db
            tool_result = process_tool_call(tool_name, tool_input)
            #Add our tool_result message:
            messages.append(
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": tool_use.id,
                            "content": str(tool_result),
                        }
                    ],
                },
            )
        else:
            #If Claude does NOT want to use a tool, just print out the text reponse
            print(f"{response.content[0].text}")


if __name__ == "__main__":
    agent_smith()

# user_message = input("\nUser: ")
# messages = [{"role": "user", "content": user_message}]

# system_message = "You are an AI coding assitant, your job is to find out the files that are necessary to change based on user's query. You have tools for this job, but you should only use them when its necessary, if the tool is not required, then don;t use it. Current working directory/root directory is - D:\claude-dev\claude-dev"
# response = client.messages.create(
#     model="claude-3-5-sonnet-20240620",
#     system=system_message,
#     messages=messages,
#     max_tokens=500,
#     tools=[tree_map_tool]
# )

# print(response)