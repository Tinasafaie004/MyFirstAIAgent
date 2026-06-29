import os
from google import genai
from google.genai import types

def write_file(working_directory, file_path, content):
    try:
        working_dir_abs= os.path.abspath(working_directory)
        target_file=os.path.normpath(os.path.join(working_dir_abs, file_path))
        #commonpath accepts an *array* of paths
        valid_file_path=os.path.commonpath([working_dir_abs, target_file])==working_dir_abs

        if not valid_file_path:
            return f'Error: Cannot write to "{file_path}" as it is outside the permitted working directory'

        if os.path.isdir(target_file):
            return f'Error: Cannot write to "{file_path}" as it is a directory'
        #think of the example as in working dir is calculator
        #then target_file is calcualtor/notes/today.txt
        #common will be calcultaor which is safe
        #now we when we get get parent_dir through dir_name of the target_file
        #we goota makedir "notes" as we don't have it --> now we can safely write
        parent_dir=os.path.dirname(target_file)
        os.makedirs(parent_dir, exist_ok=True)  #exist_ok=True, creates without raising Error if in case it doens't exist

        with open(target_file, "w") as f:
            f.write(content)
        
        return f'Successfully wrote to "{file_path}" ({len(content)} characters written)'
           

    except Exception as e:
        return f'Error: {e}'

schema_write_file = types.FunctionDeclaration(
    name="write_file",
    description="Writes content to a file within the working directory. Creates the file if it doesn't exist and overwrites it if it does.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The path to the file to write to, relative to the working directory.",
            ),
            "content": types.Schema(
                type=types.Type.STRING,
                description="The content to write to the file.",
            ),
            
        },
        required=["file_path", "content"],
    ),
)