import os
import google.generativeai as genai

api_key = os.environ.get("GEMINI_API_KEY", "")

def test_tool(a: str) -> str:
    """A test functionality."""
    return f"Tested {a}"

try:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model_name='gemini-flash-latest', tools=[test_tool])
    chat = model.start_chat()
    response = chat.send_message("Please test the tool with the argument 'hello'")
        
    print("Response structure:")
    print(dir(response))
    if hasattr(response, 'function_call'):
        print(response.function_call)
    elif response.parts and hasattr(response.parts[0], 'function_call') and response.parts[0].function_call:
        print("it is in parts")
        print(response.parts[0].function_call.name)
    else:
        print(response.text)
    
except Exception as e:
    import traceback
    traceback.print_exc()
