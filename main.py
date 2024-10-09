import google.generativeai as genai
import pyttsx3
import speech_recognition as sr
import pyaudio

def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

def get_voice_input(prompt):
    recognizer = sr.Recognizer()
    
    with sr.Microphone() as source:
        speak(prompt)
        audio = recognizer.listen(source)
        
        try:
            return recognizer.recognize_google(audio)
        except sr.UnknownValueError:
            speak("Sorry, I didn't understand you.")
            return None
        except sr.RequestError:
            speak("Oh no, I had a problem connecting to the speech services.")
            return None

def generate_recipe(ingredients, api_key):
    genai.configure(api_key=api_key)
    
    model = genai.GenerativeModel('gemini-pro')
    
    prompt = (
        f"Firstly provide the name of the dish, then the recipe, "
        f"and include the cooking devices used in each step. "
        f"Generate a recipe using the following ingredients: {', '.join(ingredients)}"
    )
    response = model.generate_content(prompt)

    if hasattr(response, 'safety_ratings') and response.safety_ratings:
        speak("The content generated was blocked for safety reasons.")
        return "Unable to generate a recipe due to safety restrictions."
    
    if hasattr(response, 'text'):
        return response.text
    else:
        return "No valid recipe could be generated."

def extract_additional_items(recipe):
    common_additional_items = ["salt", "pepper", "olive oil", "butter", "sugar", "flour", "baking powder", "vanilla extract", "garlic", "onion"]
    additional_items = []

    for item in common_additional_items:
        if item in recipe.lower():
            additional_items.append(item)

    return additional_items

def extract_devices(recipe):
    common_devices = ["oven", "stove", "microwave", "blender", "mixer", "pan", "pot", "baking dish", "grater", "knife"]
    devices = []

    for device in common_devices:
        if device in recipe.lower():
            devices.append(device)

    return devices

def get_feedback():
    speak("What did you think of the recipe? Please say your feedback.")
    feedback = get_voice_input("")  # No prompt needed here
    
    if feedback:
        speak("Thank you for your feedback!")
    else:
        feedback = "No feedback provided."
        speak("No feedback was provided.")
    
    return feedback

def generate_shopping_list(ingredients, additional_items, devices):
    all_items = set(ingredients + additional_items + devices)  # Combine and deduplicate
    shopping_list = "\nShopping List:\n" + "\n".join(all_items)
    return shopping_list

def save_history(ingredients, generated_recipe, feedback, shopping_list):
    with open("recipe_history.txt", "a") as file:
        file.write("Ingredients: " + ', '.join(ingredients) + '\n')
        file.write("Generated Recipe: " + generated_recipe + '\n')
        file.write("User Feedback: " + feedback + '\n')
        file.write("Shopping List: " + shopping_list + '\n')
        file.write("-" * 40 + '\n')  # Separator for readability

def read_history():
    try:
        with open("recipe_history.txt", "r") as file:
            history = file.read()
            print(history)
            speak(history)  # Optional: read out loud
    except FileNotFoundError:
        speak("No recipe history found.")

# Start of the main program
user_input = get_voice_input("Please speak your ingredients.")

if user_input:
    ingredients = [ingredient.strip() for ingredient in user_input.split(',')]
    
    api_key = 'AIzaSyCeG9T3KdVxhfFJ5YJ2OOJnrH5ogTQecLQ'

    generated_recipe = generate_recipe(ingredients, api_key)

    print(generated_recipe)
    speak(generated_recipe)
    
    # Extract additional items and devices from the generated recipe
    additional_items = extract_additional_items(generated_recipe)
    devices = extract_devices(generated_recipe)
    
    # Generate the shopping list including all user-provided ingredients
    shopping_list = generate_shopping_list(ingredients, additional_items, devices)
    
    # Get feedback from the user
    feedback = get_feedback()
    
    # Save the history of the recipe, feedback, and shopping list
    save_history(ingredients, generated_recipe, feedback, shopping_list)
    
    # Display the shopping list
    print(shopping_list)
    speak(shopping_list)
    
else:
    speak("No ingredients were provided.")
