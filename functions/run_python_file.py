import os
import subprocess
from google import genai
from google.genai import types

def run_python_file(working_directory, file_path, args=None):
    try:
        working_dir_abs=os.path.abspath(working_directory)
        target_file=os.path.normpath(os.path.join(working_dir_abs, file_path))
        valid_file_path=os.path.commonpath([working_dir_abs,target_file])==working_dir_abs

        if not valid_file_path:
            return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'
        
        if not os.path.isfile(target_file):
            return(f'Error: "{file_path}" does not exist or is not a regular file')
        
        if not file_path.endswith(".py"):
            return f'Error: "{file_path}" is not a Python file'
        
        command=["python", target_file]
        
        if args is not None:
            command.extend(args)

        completed= subprocess.run(
                command,
                cwd=working_dir_abs,
                capture_output=True,
                text=True, 
                timeout=30
        )

        output=[]
        if completed.stdout:
            output.append(f"STDOUT:\n{completed.stdout}")

        if completed.stderr:
            output.append(f"STDERR:\n{completed.stderr}")

        if completed.returncode!=0:
            output.append(f"Process exited with code {completed.returncode}")
        
        if not completed.stdout and not completed.stderr:
            output.append(f"No output produced")
        
        return "\n".join(output)

    except Exception as e:
        return f"Error: executing Python file: {e}"
    
#schema teaches gemini about our tools (our functions)
schema_run_python_file = types.FunctionDeclaration(
    name="run_python_file",
    description="Runs python file within the working directory. Optional args can be passed to the file.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The path to the Python file to run, relative to the working directory.",
            ),
            "args": types.Schema(
                type=types.Type.ARRAY,
                items=types.Schema(
                    type=types.Type.STRING,
                ),
                description="Optional arguments to pass to the Python file.",
            ),
            
        },
        required=["file_path"],
    ),
)