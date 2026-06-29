from functions.get_files_info import schema_get_files_info , get_files_info
from functions.get_file_content import schema_get_file_content, get_file_content
from functions.write_file import schema_write_file, write_file
from functions.run_python_file import schema_run_python_file, run_python_file
from google import genai
from google.genai import types
from collections.abc import Callable


availible_functions=types.Tool(
    function_declarations=[
        schema_get_files_info,
        schema_get_file_content,
        schema_write_file,
        schema_run_python_file,
    ]
)

#function_call will be of FunctionCall obj that has two properties: name & args
def call_function(function_call:types.FunctionCall, verbose:bool=False)->types.Content:
    if verbose: 
        print(f"Calling function: {function_call.name}({function_call.args})")
    else:
        print(f" - Calling function: {function_call.name}")
    
    #dict takes two aparmeters : str: is the key   Callable: is the value --> Callable takes a paarameter and return : ...: I don;t care what paarm and str is the return 
    function_map:dict[str, Callable[...,str]]={   #function map is like a an array of functors that I can call later , this is a map though and has keys and values 
        "get_file_content": get_file_content,
        "get_files_info":get_files_info,
        "write_file":write_file,
        "run_python_file": run_python_file,
    }

    function_name= function_call.name or ""

    if function_name not in function_map:
        return types.Content(
            role="tool",
            parts=[
                types.Part.from_function_response(
                    name=function_name,
                    response={"error": f"Unknown function {function_name}"},
                )
            ],
        )
    
    #dict constructor craetes a dictionary 
    #args makes a copy of args to amke sure original is not changed
    args=dict(function_call.args) if function_call.args else{}

    args["working_directory"]= "./calculator"
    function_result=function_map[function_name](**args)

    return types.Content(
        role="tool",
        parts=[
            #this will be function_repsonse   
            types.Part.from_function_response(  #from_fucntion_response has a function_response property and that has repsosne
                name=function_name,
                #response must be a dictioray that's why we have to shove the function_result to "result"
                response={"result": function_result},
            )
        ],
    )

