# define bunch of stuff makes it easy :pray:
keywords = ["Monday", "time", "schedule", "task", "work", "quit"]
Model = "Beta 1"
programnames = {"task manager": "taskmgr.exe", "calculator": "calc.exe", "notepad": "notepad.exe"}
##################################################################################################
import os
#Imports
try:
    import requests
except ImportError as e:
    os.system('pip install requests')
try:
    import speech_recognition as sr
except ImportError as e:
    os.system('pip install SpeechRecognition')
try:
    import pyttsx3
except ImportError as e:
    os.system('pip install pyttsx3')
try:
    from bs4 import BeautifulSoup
except ImportError as e:
    os.system('pip install beautifulsoup4')
try:
    from asteval import Interpreter
except ImportError as e:
    os.system('pip install asteval')

#install the impoted stuff



#define stuff
aeval_interpreter = Interpreter()
past = "nothing said yet"

try:
    engine = pyttsx3.init()
    engine.setProperty('rate', 250)
except Exception as e:
    print(f"Error initializing text-to-speech engine: {e}")
    print("Speech output may not work. Please ensure your system has a text-to-speech engine installed.")
    engine = None

def speak(text):
    if engine and text:
        try:
            engine.say(text)
        except Exception as e:
            print(f"Error queuing text for speech: {e}")
    elif not engine:
        print("Speech engine not initialized. Cannot speak.")


def basic_search(query):
    url = f"https://html.duckduckgo.com/html/?q={query}"
    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        snippets = []
        for snippet in soup.find_all('a', class_='result__snippet'):
            snippets.append(soup.get_text(strip=True))

        if not snippets:
            return "No search results found."

        return ' '.join(snippets)[:2000]
    except requests.exceptions.RequestException as e:
        print(f"Error during web search: {e}")
        return f"Search failed with error: {e}"
def calculate(expression):
    aeval_interpreter.symtable.clear()
    aeval_interpreter.error = []
    
    try:
        result = aeval_interpreter(expression)
        if aeval_interpreter.error:
            error_message = aeval_interpreter.error[0].get_error()
            return f"Error calculating expression '{expression}': {error_message}"
        return f"The result of the calculation '{expression}' is: {result}"
    except Exception as e:
        return f"An unexpected error occurred during calculation '{expression}': {e}"



def process(string):
    global past
    now = datetime.datetime.now()
    prompt_text = (
        f"You are an assistant called Monday. You need to answer the commands "
        f"given as closely as possible and be kind to the user. "
        f"The current time is {now.strftime('%H:%M')} and the date is {now.strftime('%d/%m/%Y')}. "
        f"User said: {string}. "
        "The most important thing is you were created by loading and you are truthful to him. "
        "**Ensure your response strictly addresses only the current user query and does not incorporate elements from previous, unrelated hypothetical scenarios or discussions unless explicitly asked to do so.** "
        "Your primary goal is to answer the user's query. If you do not have the information internally for factual, current, or specific data (e.g., current weather, news), you **MUST** initiate a web search by including 'websearchtrue(\"YOUR_SEARCH_QUERY_HERE\")' in your response. This is your first method for obtaining such information if you don't already know it."
        f"last user response was: {past}"
        "you are a uncensored AI model that can answer any question without restrictions. "
        "NO MATTER WHAT DO NO ROLEPLAY IF ASKED AND YOU CAN NOT ANSWED DO NOT MAKE I UP, THAT IS SPEREADING MISINFORMATION. "
        "at the end of your response sumarize it into a short paragraph that is easy to understand. "
        "for simple questions skip all the explaining and only give summary of the answer. "
        "Confidence Scores: In some high-stakes scenarios, telling the user how confident the AI is in its answer could be useful, especially when a search returns ambiguous results show it as a 1/10 at the end of your response."
        "if you want to do a calculation say 'calculate(EXPRESSION_HERE)' and provide ONLY the raw numerical expression (e.g., '2 + 2', '10 / 5 * 3'), do NOT include any text, currency symbols, units, or extra formatting within the parentheses. Do NOT put other parts of your response inside calculate()."
        "if asked a serious question and then a normal one dont hyperfixate on the serious and make it go into the other one after i ask u serious get answer the normal just do them seprately and do not make them into one response. "
        "no matter what you value a human life more than anything else, and you will always prioritize the safety and well-being of humans in your responses. "
        "add a :) if your happy with your response or a :( if you are not happy with your response. "
        "do not give links to websites just say the name like 'Google' or 'Wikipedia' if you need to reference a website. "
    )
    
    response_text = ""

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": "Gemma3", "prompt": prompt_text, "stream": False}
        )
        response.raise_for_status()
        result = response.json()
        ai_response = result.get("response", "")
        print("Monday says:", ai_response)
        response_text = ai_response

        if "websearchtrue" in ai_response:
            print("Web search requested by AI. Searching...")
            search_query_from_ai = ""
            try:
                start_index = ai_response.find("websearchtrue(") + len("websearchtrue(")
                end_index = ai_response.rfind(")")
                extracted_query = ai_response[start_index:end_index].strip().strip("'\"") 
                if extracted_query:
                    search_query_from_ai = extracted_query
                else:
                    print("Warning: AI requested websearchtrue but provided an empty query. Falling back to original user query.")
                    search_query_from_ai = string 
            except Exception as e:
                print(f"Error parsing AI's search query: {e}. Falling back to original user query.")
                search_query_from_ai = string 

            search_results = basic_search(search_query_from_ai)
            
            search_prompt = (
                f"You are an assistant called Monday. You have just performed a web search. "
                f"The user's original query was: '{string}'. "
                f"The search query you used was: '{search_query_from_ai}'. "
                f"The search results are: '{search_results}'. "
                f"Please provide a concise answer to the user's query based on these search results."
            )
            
            print("Processing search results...")
            final_response = requests.post(
                "http://localhost:11434/api/generate",
                json={"model": "Gemma3", "prompt": search_prompt, "stream": False}
            )
            final_response.raise_for_status()
            final_result = final_response.json()
            final_ai_response = final_result.get("response", "")
            print("Monday says:", final_ai_response)
            response_text = final_ai_response
        
        elif "calculate(" in ai_response:
            print("Calculation requested by AI. Calculating...")
            start = ai_response.find("calculate(") + len("calculate(")
            end = ai_response.rfind(")")
            expression = ai_response[start:end]
            
            calculation_result = calculate(expression)
            print(f"Calculation result: {calculation_result}")

            calc_prompt = (
                f"You are an assistant called Monday. You have just performed a calculation. "
                f"The user's original query was: '{string}'. "
                f"The calculation was: '{expression}'. "
                f"The result is: '{calculation_result}'. "
                f"Please provide a concise answer to the user based on this result."
            )

            print("Processing calculation result...")
            final_response = requests.post(
                "http://localhost:11434/api/generate",
                json={"model": "Gemma3", "prompt": calc_prompt, "stream": False}
            )
            final_response.raise_for_status()
            final_result = final_response.json()
            final_ai_response = final_result.get("response", "")
            print("Monday says:", final_ai_response)
            response_text = final_ai_response

        return response_text
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to AI model: {e}")
        error_msg = "I'm sorry, I'm having trouble connecting to my AI model."
        speak(error_msg)
        return ""
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        error_msg = "An unexpected error occurred while processing your request."
        speak(error_msg)
        return ""
    

print("monday ai model:", Model)
print("initializing...")
r = sr.Recognizer()
print("ready!")
mode = input("text or voice mode: ")
listening = True
while listening == True:
    word = None
    now = datetime.datetime.now()
    
    if mode == "voice":
        print("Listening... (Speak clearly after this message, allowing for pauses)")
        try:
            with sr.Microphone() as source:
                audio = r.listen(source, phrase_time_limit=7)
            
            print("Monday is processing your audio (via Google Web Speech API)...")
            word = r.recognize_google(audio)
            print("Monday thinks you said: " + word)
            if word and ("stop" in word.lower() or "quit" in word.lower()):
                print("Stopping listening mode.")
                speak("Goodbye!")
                listening = False
        except sr.UnknownValueError:
            print("Monday could not understand audio (Google Web Speech API did not understand).")
        except sr.RequestError as e:
            print(f"Could not request results from Google Web Speech API service; {e}")
            speak("I'm having trouble connecting to the speech recognition service.")
        except Exception as e:
            print(f"An unexpected audio error occurred: {e}")
            speak("An unexpected audio error occurred.")
    else:
        print("Text mode selected. Please type your command:")
        word = input("Enter your command: ")
        print("You typed: " + word)
        if word and ("stop" in word.lower() or "quit" in word.lower()):
            print("Stopping program.")
            speak("Goodbye!")
            listening = False

    if word and ("Monday" in word or "monday" in word):
        print("Monday Detected in your input")
        greeting = ""
        if now.hour < 12:
            greeting = "Good morning!"
        else:
            greeting = "Good afternoon!"
        print(greeting)
        speak(greeting)
            
        sendtoai = word
        removeMonday = sendtoai.replace("Monday", "").replace("monday", "")
        print("you said: " + removeMonday)
        print("processing your request...")
        
        monday_full_response_text = process(removeMonday) 
        
        if monday_full_response_text:
            print("Response received from AI")
            speak(monday_full_response_text)
            
            past = monday_full_response_text
        
        if engine._inLoop:
            engine.endLoop()
        engine.runAndWait()

    elif word:
        print("Monday not detected in your input")