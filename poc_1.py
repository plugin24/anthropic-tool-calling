from dotenv import load_dotenv
import anthropic
import os   
# from langsmith import traceable
from tools.anthropic_tools import AnthropicTools
import sys
from prompts.general_prompt import prompt1

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
                "description": "Folders to be exclude while reading directory. eg. ['env', '.venv', 'purecode-env','vendor']"
            }
        },
        "required": ["root_dir", "exclude_folders"]
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
        },
        "required" : ["file_path"]
    }
}

delete_file_tool = {
    "name" : "delete_file",
    "description" : "This tool deletes the file if the path is given",
    "input_schema" : {
        "type" : "object",
        "properties" : {
            "file_path" : {
                "type" : "string",
                "description" : "The file path of the file that we want to delete"
            }
        },
        "required" : ["file_path"]
    }
}

write_files_tool = {
    "name" : "write_file",
    "description" : "This tool helps in writing new code in the file. It checks if the file is present, if its not present, it can create file as well.",
    "input_schema" : {
        "type" : "object",
        "properties" : {
            "file_path" : {
                "type" : "string",
                "description" : "Path of the file which we want to read"
            },
            "new_code" : {
                "type" : "string",
                "description" : "This is the newly generated code that we want to write in the file."
            }
        },
        "required" : ["file_path", "new_code"]
    }
}

# ask_permission_tool = {
#     "name" : "ask_user_permission",
#     "description" : "Use this tool to take permission from user. Frame the question in such a way that it has only yes/no answer.",
#     "input_schema" : {
#         "type" : "object",
#         "properties" : {
#             "question" : {
#                 "type" : "string",
#                 "description" : "Question for which we need answer, frame the question who has Yes/No answer."
#             }
#         }
#     },
#     "required" : ["question"]
# }

anthropic_tools = AnthropicTools()

def process_tool_call(tool_name, tool_input):
    choice = "no" 
    if tool_name == "tree_map":
        tree = anthropic_tools.tree_map(tool_input["root_dir"], tool_input['exclude_folders'])
        return tree
    elif tool_name == "read_file":
        return anthropic_tools.read_file(tool_input['file_path'])
    elif tool_name == "write_file":
        choice = input(f"\nLLM wants to write into {tool_input['file_path']}, are you allowing it?(yes/no) : ")
        if choice.lower() == "yes":
            return anthropic_tools.write_file(tool_input['file_path'], tool_input['new_code'])
        else:
            sys.exit(0)
    elif tool_name == "delete_file":
        choice = input(f"\nLLM wants to write into {tool_input['file_path']}, are you allowing it?(yes/no) : ")
        if choice.lower() == "yes":
            return anthropic_tools.delete_file(tool_input['file_path'])
        else:
            sys.exit(0)
        return tools.delete_file(tool_input['file_path'])

# @traceable
def agent_smith(system_prompt):
    user_message = input("\nUser: ")
    messages = [{"role": "user", "content": user_message}]

    while True:
        #If the last message is from the assistant, get another input from the user
        if messages[-1].get("role") == "assistant":
            user_message = input("\nUser: ")
            if user_message == "exit":
                break
            messages.append({"role": "user", "content": user_message})

        # system_message1 = "You are an AI coding assitant, your job is to find out the files that are necessary to change based on user's query. You have tools for this job, but you should only use them when its necessary, if the tool is not required, then don;t use it. Current working directory/root directory is - D:\claude-dev\claude-dev"
        # system_message2 = """You are an AI coding assistant, your job is to help user in coding by doing tasks given by user. To complete those tasks, you may use tools provided to you. But only use tools when its necessary to use them. Current working directory/root directory is - D:\claude-dev\claude-dev
        # You can also take permission from user."""
        response = client.messages.create(
            model="claude-3-5-sonnet-20240620",
            system=system_prompt,
            messages=messages,
            max_tokens=1000,
            temperature=0,
            tools=[tree_map_tool, read_files_tool, write_files_tool, delete_file_tool]
        )

        print("\n", response.content[0].text, "\n")
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

    system_prompt = prompt1()
    agent_smith(system_prompt)

# user_message = input("\nUser: ")
# messages = [{"role": "user", "content": user_message}]


# system_message1 = "You are an AI coding assitant, your job is to find out the files that are necessary to change based on user's query. You have tools for this job, but you should only use them when its necessary, if the tool is not required, then don;t use it. Current working directory/root directory is - D:\claude-dev\claude-dev"

# system_messsage2 = "Use given tool"
# response = client.messages.create(
#     model="claude-3-5-sonnet-20240620",
#     system=system_messsage2,
#     messages=messages,
#     max_tokens=200,
#     tools=tool_info
# )

# print(response)