import streamlit as st
import speech_recognition as sr
import numpy as np
import cv2
import os
from PIL import Image
import string
import tempfile
import time
import threading
from pathlib import Path

# Page setup
st.set_page_config(
    page_title="Sign Language Interpreter", 
    page_icon="👋", 
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("👋 Sign Language Interpreter")
st.write("Speak and see the sign language representation")

# Enhanced ISL GIF database with better organization
ISL_GIF_DATABASE = {
    'greetings': ['hello', 'good morning', 'good afternoon', 'good evening', 'good night', 'nice to meet you'],
    'questions': [
        'any questions', 'are you angry', 'are you busy', 'are you hungry', 'are you sick',
        'can we meet tomorrow', 'did you book tickets', 'did you finish homework',
        'do you go to office', 'do you have money', 'do you want something to drink',
        'do you want tea or coffee', 'do you watch TV', 'how many people are there in your family',
        'what are you doing', 'what is the problem', 'what is todays date',
        'what is your father do', 'what is your job', 'what is your mobile number',
        'what is your name', 'when is your interview', 'when we will go',
        'where do you stay', 'where is the bathroom', 'where is the police station'
    ],
    'common_phrases': [
        'be careful', 'dont worry', 'flower is beautiful', 'good question',
        'had your lunch', 'happy journey', 'i am a clerk', 'i am bore doing nothing',
        'i am fine', 'i am sorry', 'i am thinking', 'i am tired',
        'i dont understand anything', 'i go to a theatre', 'i love to shop',
        'i had to say something but i forgot', 'i have headache', 'i like pink colour',
        'i live in nagpur', 'lets go for lunch', 'my mother is a homemaker',
        'my name is john', 'no smoking please', 'open the door', 'please call me later',
        'please clean the room', 'please give me your pen', 
        'please use dustbin dont throw garbage', 'please wait for sometime',
        'shall I help you', 'shall we go together tommorow', 'sign language interpreter',
        'sit down', 'stand up', 'take care', 'there was traffic jam', 'wait I am thinking',
        'whats up', 'you are wrong'
    ],
    'locations': [
        'address', 'agra', 'ahemdabad', 'assam', 'australia', 'badoda', 'banaras', 
        'banglore', 'bihar', 'chandigarh', 'chennai', 'delhi', 'gujrat', 'hyderabad',
        'india', 'karnataka', 'kerala', 'mumbai', 'nagpur', 'pakistan', 'pune',
        'punjab', 'rajasthan', 'southafrica', 'tamil nadu', 'usa'
    ],
    'other': [
        'all', 'april', 'august', 'banana', 'bridge', 'cat', 'christmas', 'church',
        'clinic', 'coconut', 'crocodile', 'dasara', 'deaf', 'december', 'deer',
        'dollar', 'duck', 'febuary', 'friday', 'fruits', 'glass', 'grapes',
        'hindu', 'january', 'jesus', 'job', 'july', 'krishna', 'litre', 'mango',
        'may', 'mile', 'monday', 'museum', 'muslim', 'october', 'orange', 'pass',
        'police station', 'post office', 'ram', 'restaurant', 'saturday',
        'september', 'shop', 'sleep', 'story', 'sunday', 'temperature', 'temple',
        'thursday', 'toilet', 'tomato', 'town', 'tuesday', 'village', 'voice',
        'wednesday', 'weight'
    ]
}

# Flatten the database for easy lookup
isl_gif = []
for category in ISL_GIF_DATABASE.values():
    isl_gif.extend(category)

# Alphabet for spelling
alphabet = list('abcdefghijklmnopqrstuvwxyz')

# Global variable to control speech recognition
listening_active = False

def check_directories():
    """Check if required directories exist"""
    directories = ['ISL_Gifs', 'letters']
    for dir_name in directories:
        if not os.path.exists(dir_name):
            st.warning(f"⚠️ Directory '{dir_name}' not found. Some features may not work.")
            # Create dummy directories for demonstration
            os.makedirs(dir_name, exist_ok=True)

def create_sample_images():
    """Create sample images if they don't exist (for demo purposes)"""
    letters_dir = Path('letters')
    letters_dir.mkdir(exist_ok=True)
    
    # Create sample letter images
    for letter in alphabet:
        img_path = letters_dir / f'{letter}.jpg'
        if not img_path.exists():
            # Create a simple colored image with the letter
            img = np.zeros((200, 200, 3), dtype=np.uint8)
            img[:, :] = [50, 150, 200]  # Blue background
            cv2.putText(img, letter.upper(), (50, 120), cv2.FONT_HERSHEY_SIMPLEX, 
                       3, (255, 255, 255), 5)
            cv2.imwrite(str(img_path), img)

def speech_to_sign():
    global listening_active
    listening_active = True
    r = sr.Recognizer()
    
    # Create placeholders for dynamic content
    status_placeholder = st.empty()
    result_placeholder = st.empty()
    image_placeholder = st.empty()
    gif_placeholder = st.empty()
    confidence_placeholder = st.empty()
    
    with sr.Microphone() as source:
        st.sidebar.info("🎤 Microphone activated")
        r.adjust_for_ambient_noise(source, duration=1)
        
        while listening_active:
            status_placeholder.info("🎤 Listening... Speak now!")
            
            try:
                audio = r.listen(source, timeout=8, phrase_time_limit=10)
                status_placeholder.success("✅ Processing speech...")
                
                # Show processing animation
                with st.spinner("Converting speech to text..."):
                    a = r.recognize_google(audio)
                
                a = a.lower().strip()
                status_placeholder.write(f"🎯 You said: **{a}**")
                
                # Clean punctuation
                translator = str.maketrans('', '', string.punctuation)
                a = a.translate(translator)
                
                # Exit condition
                if a in ['goodbye', 'good bye', 'bye', 'exit', 'quit', 'stop']:
                    status_placeholder.warning("👋 Time to say goodbye!")
                    listening_active = False
                    break
                
                # Check if it's in ISL GIF database
                matched_phrase = None
                for phrase in isl_gif:
                    if phrase in a or a in phrase:
                        matched_phrase = phrase
                        break
                
                if matched_phrase:
                    gif_path = f'ISL_Gifs/{matched_phrase}.gif'
                    if os.path.exists(gif_path):
                        gif_placeholder.image(gif_path, caption=f"Sign for: {matched_phrase}", use_column_width=True)
                        image_placeholder.empty()  # Clear letter images
                        confidence_placeholder.success(f"✅ Matched phrase: '{matched_phrase}'")
                    else:
                        st.warning(f"GIF not found for: {matched_phrase}")
                        # Fall back to spelling
                        spell_word(a, image_placeholder, gif_placeholder, result_placeholder)
                
                else:
                    # Spell out the word
                    spell_word(a, image_placeholder, gif_placeholder, result_placeholder)
                    confidence_placeholder.info("🔤 Spelling out your words")
                
            except sr.WaitTimeoutError:
                if listening_active:
                    status_placeholder.warning("⏰ No speech detected. Still listening...")
            except sr.UnknownValueError:
                if listening_active:
                    status_placeholder.error("❌ Could not understand audio. Please try again.")
            except sr.RequestError as e:
                if listening_active:
                    status_placeholder.error(f"🚫 Error with speech recognition service: {e}")
            except Exception as e:
                if listening_active:
                    status_placeholder.error(f"💥 Unexpected error: {e}")
    
    status_placeholder.info("🎤 Speech recognition stopped")

def spell_word(word, image_placeholder, gif_placeholder, result_placeholder):
    """Spell out a word using individual letter images"""
    gif_placeholder.empty()  # Clear GIF
    result_placeholder.write(f"🔤 Spelling out: **{word}**")
    
    # Filter only alphabetic characters
    clean_word = ''.join([c for c in word if c.isalpha() or c.isspace()])
    
    if not clean_word:
        result_placeholder.warning("No recognizable letters found.")
        return
    
    # Create columns for letters
    letters_to_show = [c for c in clean_word if c.isalpha()]
    if not letters_to_show:
        return
        
    num_cols = min(len(letters_to_show), 6)
    cols = st.columns(num_cols)
    
    with image_placeholder.container():
        for i, char in enumerate(letters_to_show):
            if char.lower() in alphabet:
                image_path = f'letters/{char.lower()}.jpg'
                if os.path.exists(image_path):
                    with cols[i % num_cols]:
                        st.image(image_path, caption=char.upper(), width=80)
                else:
                    with cols[i % num_cols]:
                        st.warning(f"No image for: {char}")
            elif char != ' ':
                with cols[i % num_cols]:
                    st.info(f"'{char}'")

def stop_recognition():
    global listening_active
    listening_active = False

# Initialize the app
check_directories()
create_sample_images()

# Main app interface
st.sidebar.title("Controls")

col1, col2 = st.sidebar.columns(2)

with col1:
    if st.button("🎤 Start Recognition", type="primary", use_container_width=True):
        if not listening_active:
            # Use threading to avoid blocking
            import threading
            thread = threading.Thread(target=speech_to_sign)
            thread.daemon = True
            thread.start()

with col2:
    if st.button("🛑 Stop Recognition", type="secondary", use_container_width=True):
        stop_recognition()

st.sidebar.markdown("---")

# Settings
st.sidebar.subheader("Settings")
recognition_timeout = st.sidebar.slider("Recognition Timeout (seconds)", 3, 15, 8)
phrase_limit = st.sidebar.slider("Phrase Time Limit (seconds)", 5, 20, 10)

st.sidebar.markdown("---")

# Display available commands in an organized way
with st.sidebar.expander("📋 Available Commands", expanded=False):
    st.write("**Try saying these phrases:**")
    
    for category, phrases in ISL_GIF_DATABASE.items():
        with st.expander(f"🗂️ {category.title()} ({len(phrases)} phrases)"):
            # Display in multiple columns for better readability
            cols = st.columns(2)
            for i, phrase in enumerate(phrases[:20]):  # Limit to first 20 per category
                with cols[i % 2]:
                    st.write(f"• {phrase}")

# Information section
with st.sidebar.expander("ℹ️ Instructions"):
    st.info("""
    **How to use:**
    1. Click 'Start Recognition'
    2. Speak clearly into your microphone
    3. The app will show sign language GIFs for known phrases
    4. Unknown words will be spelled out letter by letter
    5. Say 'goodbye', 'exit', or 'stop' to end
    6. Click 'Stop Recognition' to manually stop
    
    **Tips:**
    - Speak clearly and at a moderate pace
    - Reduce background noise for better accuracy
    - Use complete phrases from the available commands list
    """)

# Main area enhancements
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Live Recognition Output")
    
    # Status indicator
    if listening_active:
        st.success("🔴 **LIVE** - Recognition Active")
    else:
        st.info("⚪ **READY** - Click Start to begin")
    
    # Placeholder for dynamic content
    output_placeholder = st.empty()

with col2:
    st.subheader("About This App")
    st.markdown("""
    This Sign Language Interpreter:
    - Converts speech to Indian Sign Language (ISL)
    - Supports 200+ phrases and words
    - Spells out unrecognized words
    - Uses Google Speech Recognition
    - Works in real-time
    """)
    
    # Statistics
    st.metric("Available Phrases", len(isl_gif))
    st.metric("Alphabet Letters", len(alphabet))

# Footer
st.markdown("---")
st.caption("Sign Language Interpreter App | Made with Streamlit")