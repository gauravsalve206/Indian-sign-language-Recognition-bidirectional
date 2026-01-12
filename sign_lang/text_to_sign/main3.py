import streamlit as st
import speech_recognition as sr
import numpy as np
import cv2
import os
from PIL import Image
import string
import tempfile

# Page setup
st.set_page_config(page_title="Sign Language Interpreter", page_icon="👋", layout="wide")
st.title("👋 Sign Language Interpreter")
st.write("Speak and see the sign language representation")

# ISL GIF database
isl_gif = ['any questions', 'are you angry', 'are you busy', 'are you hungry', 'are you sick', 'be careful',
        'can we meet tomorrow', 'did you book tickets', 'did you finish homework', 'do you go to office', 'do you have money',
        'do you want something to drink', 'do you want tea or coffee', 'do you watch TV', 'dont worry', 'flower is beautiful',
        'good afternoon', 'good evening', 'good morning', 'good night', 'good question', 'had your lunch', 'happy journey',
        'hello what is your name', 'how many people are there in your family', 'i am a clerk', 'i am bore doing nothing', 
        'i am fine', 'i am sorry', 'i am thinking', 'i am tired', 'i dont understand anything', 'i go to a theatre', 'i love to shop',
        'i had to say something but i forgot', 'i have headache', 'i like pink colour', 'i live in nagpur', 'lets go for lunch', 'my mother is a homemaker',
        'my name is john', 'nice to meet you', 'no smoking please', 'open the door', 'please call me later',
        'please clean the room', 'please give me your pen', 'please use dustbin dont throw garbage', 'please wait for sometime', 'shall I help you',
        'shall we go together tommorow', 'sign language interpreter', 'sit down', 'stand up', 'take care', 'there was traffic jam', 'wait I am thinking',
        'what are you doing', 'what is the problem', 'what is todays date', 'what is your father do', 'what is your job',
        'what is your mobile number', 'what is your name', 'whats up', 'when is your interview', 'when we will go', 'where do you stay',
        'where is the bathroom', 'where is the police station', 'you are wrong','address','agra','ahemdabad', 'all', 'april', 'assam', 'august', 'australia', 'badoda', 'banana', 'banaras', 'banglore',
        'bihar','bihar','bridge','cat', 'chandigarh', 'chennai', 'christmas', 'church', 'clinic', 'coconut', 'crocodile','dasara',
        'deaf', 'december', 'deer', 'delhi', 'dollar', 'duck', 'febuary', 'friday', 'fruits', 'glass', 'grapes', 'gujrat', 'hello',
        'hindu', 'hyderabad', 'india', 'january', 'jesus', 'job', 'july', 'july', 'karnataka', 'kerala', 'krishna', 'litre', 'mango',
        'may', 'mile', 'monday', 'mumbai', 'museum', 'muslim', 'nagpur', 'october', 'orange', 'pakistan', 'pass', 'police station',
        'post office', 'pune', 'punjab', 'rajasthan', 'ram', 'restaurant', 'saturday', 'september', 'shop', 'sleep', 'southafrica',
        'story', 'sunday', 'tamil nadu', 'temperature', 'temple', 'thursday', 'toilet', 'tomato', 'town', 'tuesday', 'usa', 'village',
        'voice', 'wednesday', 'weight','please wait for sometime','what is your mobile number','what are you doing','are you busy']

arr = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']

def speech_to_sign():
    r = sr.Recognizer()
    
    # Create placeholders for dynamic content
    status_placeholder = st.empty()
    result_placeholder = st.empty()
    image_placeholder = st.empty()
    gif_placeholder = st.empty()
    
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source)
        
        while True:
            status_placeholder.info("🎤 Listening... Speak now!")
            
            try:
                audio = r.listen(source, timeout=5)
                status_placeholder.success("✅ Processing speech...")
                
                a = r.recognize_google(audio)  # Using Google for better accuracy
                a = a.lower()
                status_placeholder.write(f"🎯 You said: **{a}**")
                
                # Clean punctuation
                for c in string.punctuation:
                    a = a.replace(c, "")
                
                # Exit condition
                if a in ['goodbye', 'good bye', 'bye', 'exit', 'quit']:
                    status_placeholder.warning("👋 Time to say goodbye!")
                    break
                
                # Check if it's in ISL GIF database
                if a in isl_gif:
                    gif_path = f'ISL_Gifs/{a}.gif'
                    if os.path.exists(gif_path):
                        gif_placeholder.image(gif_path, caption=f"Sign for: {a}", use_column_width=True)
                        image_placeholder.empty()  # Clear letter images
                    else:
                        st.warning(f"GIF not found for: {a}")
                
                else:
                    # Show individual letters
                    gif_placeholder.empty()  # Clear GIF
                    result_placeholder.write(f"🔤 Spelling out: {a}")
                    
                    cols = st.columns(min(len(a), 5))  # Create columns for letters
                    for i, char in enumerate(a):
                        if char in arr:
                            image_path = f'letters/{char}.jpg'
                            if os.path.exists(image_path):
                                with cols[i % len(cols)]:
                                    st.image(image_path, caption=char.upper(), width=100)
                        else:
                            continue
                
            except sr.WaitTimeoutError:
                status_placeholder.warning("⏰ Listening timeout. Try speaking again.")
            except sr.UnknownValueError:
                status_placeholder.error("❌ Could not understand audio")
            except sr.RequestError as e:
                status_placeholder.error(f"🚫 Error with speech recognition: {e}")
            except Exception as e:
                status_placeholder.error(f"💥 Unexpected error: {e}")

# Main app interface
st.sidebar.title("Controls")

if st.sidebar.button("🎤 Start Live Voice Recognition"):
    speech_to_sign()

if st.sidebar.button("🛑 Stop Recognition"):
    st.experimental_rerun()

st.sidebar.info("""
**Instructions:**
1. Click 'Start Live Voice Recognition'
2. Speak clearly into your microphone
3. Say 'goodbye' to stop
4. The app will show sign language GIFs or spell out letters
""")

# Display available commands
with st.expander("📋 Available Commands"):
    st.write("Full words/phrases available:")
    cols = st.columns(3)
    for i, word in enumerate(isl_gif[:30]):  # Show first 30 commands
        with cols[i % 3]:
            st.write(f"• {word}")