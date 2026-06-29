import os
import argparse
from dotenv import load_dotenv
from google import genai
from google.genai import types
from prompts import system_prompt
from call_functions import availible_functions
from call_functions import call_function

load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

def main():
    parser = argparse.ArgumentParser(description="Chatbot")
    parser.add_argument("user_prompt", type=str, help="User prompt")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose prompt")
    args = parser.parse_args()

    messages = [
        types.Content(
            role="user",
            parts=[types.Part(text=args.user_prompt)]
        )
    ]
    function_results=[]
    try:
        #response is going to have a response object that contains function_calls
        for i in range (20):
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=messages,
                config=types.GenerateContentConfig(tools=[availible_functions],system_instruction=system_prompt, temperature=0)
            )
            for c in response.candidates:
                messages.append(c.content) #this will keep track of the previous responses
            if response.function_calls: #the function_calls property of the response object
                for function_call in response.function_calls:
                    function_call_result= call_function(function_call, args.verbose)
                    if not function_call_result.parts:
                        raise Exception("Function result has no parts")
                    
                    if function_call_result.parts[0].function_response is None:
                        raise Exception("Function call result has no response")
                    
                    if function_call_result.parts[0].function_response.response is None:
                        raise Exception("Function call result has no response")
                    
                    function_results.append(function_call_result.parts[0])

                    if args.verbose:
                        print(f"-> {function_call_result.parts[0].function_response.response}")

                messages.append( #the function also needs to see the reuslt of the function calls
                    types.Content(
                        role="user",
                        parts=function_results
                    )
                )    
            

            
            else:
                print(response.text)
                return 
        print("max iterations reached")
        exit(1)

    except Exception as e:
        print(f"Error: {e}")
        return

    #print("Response:")

    
   

    if args.verbose:
        print("User prompt:", args.user_prompt)
        print("Prompt tokens:", response.usage_metadata.prompt_token_count)
        print("Response tokens:", response.usage_metadata.candidates_token_count)

 
if __name__ == "__main__":
    main()
