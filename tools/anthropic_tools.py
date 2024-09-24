import os
# from langchain.agents import tool

class AnthropicTools:

    def __init__(self) -> None:
        pass
    
    # @tool
    def tree_map(self, root_dir, exclude_folders=None, prefix=''):
        """
        Generate a tree structure of directories and files, excluding certain folders, and store the output in a variable.
        
        Args:

            root_dir (str): The path of the root directory from which to start generating the tree.

            exclude_folders (list, optional): A list of folder names or paths to exclude from the tree.
        
        Returns:

            str: A string representation of the directory tree, where directories and files are 
             represented with lines and branches in a tree structure.

        """

        if exclude_folders is None:
            exclude_folders = []

        contents = os.listdir(root_dir)
        contents.sort()

        result = ""

        # Iterate over the items
        for idx, name in enumerate(contents):
            path = os.path.join(root_dir, name)

            # Skip excluded folders
            if any(excluded in path for excluded in exclude_folders):
                continue

            # Determine the connector based on whether it's the last item
            connector = '└── ' if idx == len(contents) - 1 else '├── '
            result += prefix + connector + name + "\n"

            # Recursively list directories
            if os.path.isdir(path):
                next_prefix = '    ' if idx == len(contents) - 1 else '│   '
                result += self.tree_map(path, exclude_folders, prefix + next_prefix)

        return result

        

    # @tool
    def read_file(self, file_path: str):

        """
        Generate a tree structure of directories and files, excluding certain folders, and store the output in a variable.
        
        Args:

            file_oath (str): The path of the file from which we are going to read the contents.
        
        Returns:

            file_contents: All contents of file.

        """

        file_contents = ""
        try:
            with open(file_path, "r") as f:
                file_contents = f.read()
                return file_contents
        except FileNotFoundError:
            return f"Error: {file_path} not found"
    
    # @tool
    def write_file(self, file_path: str, new_code: str):
        """
        Creates a new file and writes the provided code/content to it. 
        If no code/content is provided, it creates an empty file.

        Args:
            file_path (str): The path where the new file will be created.
            new_code (str): The content to be written into the new file (default is an empty string).

        Returns:
            str: Success message if the file is created and written successfully, otherwise an error message.
        """
        try:
            with open(file_path, 'w') as f:
                f.write(new_code)
                return f"{file_path} updated successfully"
        except Exception as e:
            return f"Error: {e}"


    def delete_file(self, file_path: str):
        try:
            os.remove(file_path)
            return "file removed successfully"
        except FileNotFoundError:
            return f"Error: {file_path} not found"
    
    # def create_file(self, file_path: str, content: str = ''):
    #     """
    #     Creates a new file and writes the provided content to it. 
    #     If no content is provided, it creates an empty file.

    #     Args:
    #         file_path (str): The path where the new file will be created.
    #         content (str): The content to be written into the new file (default is an empty string).

    #     Returns:
    #         str: Success message if the file is created and written successfully, otherwise an error message.
    #     """
    #     try:
    #         # 'x' mode will create a new file, and raise an error if it already exists
    #         with open(file_path, 'x') as f:
    #             f.write(content)
    #         return f"File created successfully at {file_path}."
    #     except FileExistsError:
    #         return f"Error: File already exists at {file_path}."
    #     except Exception as e:
    #         return f"Error: {e}"

    # def ask_user_permission(self, question):

    #     print(question)
    #     permission = input("\nDo you give permission?(Yes/No)")

    #     if permission.lower() == "yes" or permission.lower() == "no":
    #         return permission.lower()
    #     else:
    #         print("\nInvalid input\n")
    #         self.ask_user_permission(question)