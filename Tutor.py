import streamlit as st
import google.generativeai as genai
import math
import plotly.graph_objects as go
import pandas as pd
import plotly.express as px
import hashlib
import sqlite3
import json
from datetime import datetime
import re
import sympy as sp
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io
import random
import pytesseract
from PIL import Image


pytesseract.pytesseract.tesseract_cmd = 'C:\Program Files\Tesseract-OCR\Tesseract.exe'
from PIL import Image, ImageOps, ImageEnhance

# Configure the Google Gemini API
genai.configure(api_key="AIzaSyBkaIzPFM_uJ-JfLj7AFbik9ml2upq2qy4")
model = genai.GenerativeModel('gemini-1.5-flash-latest')

# Set up the Streamlit app
st.set_page_config(page_title="Advanced AI Math Tutor", layout="wide", initial_sidebar_state="expanded")

# CSS for a vibrant dark theme
st.markdown("""
<style>

.stApp {
    background: linear-gradient(135deg, #0a0a0a, #161616);
    color: #e0e0e0;
    font-family: 'Poppins', sans-serif;
}

.stSidebar {
    background: rgba(20, 20, 20, 0.85);
    color: white;
    padding: 20px;
    border-radius: 12px;
    box-shadow: 0 0 5px rgba(255, 49, 49, 0.1);
    border: 1px solid rgba(255, 49, 49, 0.1);
    backdrop-filter: blur(10px);
}

.stSidebar .stRadio, .stSidebar .stSelectbox {
    background: rgba(50, 50, 50, 0.2);
    color: #ffffff;
    border-radius: 10px;
    padding: 10px;
    font-weight: bold;
    transition: all 0.3s ease;
}

.stSidebar .stRadio:hover, .stSidebar .stSelectbox:hover {
    background: rgba(70, 70, 70, 0.3);
}

.stButton>button {
    background: linear-gradient(90deg, #ff3131, #990000);
    color: white;
    border-radius: 10px;
    font-size: 1.1rem;
    padding: 10px 16px;
    transition: all 0.3s ease-in-out;
    box-shadow: 0 0 4px rgba(255, 49, 49, 0.3);
    border: none;
}

.stButton>button:hover {
    background: linear-gradient(90deg, #990000, #ff3131);
    box-shadow: 0 0 6px rgba(255, 49, 49, 0.4);
}

.stTextInput>div>div>input, .stTextArea textarea, .stSelectbox>div>div>select {
    background: rgba(40, 40, 40, 0.9);
    color: #e0e0e0;
    border-radius: 8px;
    padding: 10px;
    border: 1px solid #ff3131;
    transition: all 0.2s ease;
}

.stTextInput>div>div>input:focus, .stTextArea textarea:focus, .stSelectbox>div>div>select:focus {
    border-color: #990000;
    box-shadow: 0 0 4px rgba(153, 0, 0, 0.4);
}

h1, h2, h3 {
    font-family: 'Poppins', sans-serif;
    color: #ff3131;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    text-shadow: 0 0 5px rgba(255, 49, 49, 0.3);
}

code {
    background: #1a1a1a;
    color: #ff3131;
    padding: 6px 10px;
    border-radius: 6px;
    box-shadow: 0 0 3px rgba(255, 49, 49, 0.2);
}

.custom-card {
    background: rgba(255, 255, 255, 0.05);
    padding: 15px;
    border-radius: 12px;
    box-shadow: 0 0 5px rgba(255, 49, 49, 0.1);
    transition: transform 0.2s ease-in-out;
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 49, 49, 0.1);
}

.custom-card:hover {
    transform: scale(1.02);
}

a {
    color: #ff3131;
    font-weight: bold;
    text-decoration: none;
    transition: color 0.3s ease;
}

a:hover {
    color: #990000;
}

::-webkit-scrollbar {
    width: 8px;
}

::-webkit-scrollbar-thumb {
    background: linear-gradient(180deg, #ff3131, #990000);
    border-radius: 8px;
    box-shadow: 0 0 5px rgba(255, 49, 49, 0.3);
}

.stFooter {
    background: rgba(20, 20, 20, 0.85);
    padding: 15px;
    text-align: center;
    color: #e0e0e0;
    border-radius: 10px;
    font-size: 0.9rem;
}
.stSidebar label[data-testid="stRadioLabel"] {
    display: block;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    font-size: 14px;
    width: 100%;
}
</style>
""", unsafe_allow_html=True)


def render_math(text):
    st.write(text)

conn = sqlite3.connect('math_tutor.db')
c = conn.cursor()

c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password TEXT,
        progress TEXT
    )
""")
conn.commit()  

c.execute("PRAGMA table_info(users)")
columns = [column[1] for column in c.fetchall()]
if 'progress' not in columns:
    c.execute("ALTER TABLE users ADD COLUMN progress TEXT")
    conn.commit()

# User Authentication
def hash_password(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_user(username, password):
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, hash_password(password)))
    return c.fetchone() is not None

def create_user(username, password):
    try:
        progress = json.dumps({"completed_topics": [], "quiz_scores": {}, "practice_sets": {}})
        c.execute("INSERT INTO users (username, password, progress) VALUES (?, ?, ?)", (username, hash_password(password), progress))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False

def update_progress(username, topic, score=None, practice_set=None):
    c.execute("SELECT progress FROM users WHERE username=?", (username,))
    result = c.fetchone()
    if result:
        progress = json.loads(result[0] or '{"completed_topics": [], "quiz_scores": {}, "practice_sets": {}}')
    else:
        progress = {"completed_topics": [], "quiz_scores": {}, "practice_sets": {}}
    
    if topic not in progress["completed_topics"]:
        progress["completed_topics"].append(topic)
    if score is not None:
        progress["quiz_scores"][topic] = score
    if practice_set is not None:
        progress["practice_sets"][topic] = practice_set
    c.execute("UPDATE users SET progress=? WHERE username=?", (json.dumps(progress), username))
    conn.commit()

def get_progress(username):
    c.execute("SELECT progress FROM users WHERE username=?", (username,))
    result = c.fetchone()
    if result and result[0]:
        return json.loads(result[0])
    return {"completed_topics": [], "quiz_scores": {}, "practice_sets": {}}

def save_practice_set_as_pdf(practice_set):
    pdf_buffer = io.BytesIO()
    c = canvas.Canvas(pdf_buffer, pagesize=letter)
    c.setFont("Helvetica", 12)
    c.drawString(100, 750, "Practice Set")
    y = 730
    
    for q in practice_set:
        lines = q.split(" ")
        line = ""
        for word in lines:
            if c.stringWidth(line + word, "Helvetica", 12) < 400:
                line += word + " "
            else:
                c.drawString(100, y, line.strip())
                y -= 20
                line = word + " "
                if y < 50:
                    c.showPage()
                    c.setFont("Helvetica", 12)
                    y = 750
        c.drawString(100, y, line.strip())
        y -= 20
        if y < 50:
            c.showPage()
            c.setFont("Helvetica", 12)
            y = 750
    
    c.save()
    pdf_buffer.seek(0)
    return pdf_buffer

def extract_text_from_image(image_file):
    try:
        image = Image.open(image_file)
        image = image.convert('L')  
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(2.0) 
        image = image.point(lambda x: 0 if x < 128 else 255, '1') 
        image = image.resize((image.width * 2, image.height * 2), Image.Resampling.LANCZOS)
        extracted_text = pytesseract.image_to_string(image, lang='eng')
        return extracted_text.strip()  
    except Exception as e:
        st.error(f"Error extracting text: {e}")
        return None


if 'user' not in st.session_state:
    st.session_state.user = None

if st.session_state.user is None:
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    with tab1:
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            if check_user(username, password):
                st.session_state.user = username
                st.success("Logged in successfully!")
                st.rerun()
            else:
                st.error("Invalid username or password")
    with tab2:
        new_username = st.text_input("New Username")
        new_password = st.text_input("New Password", type="password")
        if st.button("Sign Up"):
            if create_user(new_username, new_password):
                st.success("Account created successfully! Please log in.")
            else:
                st.error("Username already exists")
    
if st.session_state.get("user", None) is not None:
   
    st.sidebar.title(f"Welcome, {st.session_state.user}!")

    st.sidebar.markdown("---")
    
    if "selected_menu" not in st.session_state:
        st.session_state.selected_menu = None

    menu_choice = st.sidebar.radio("Select a Feature", ["Basic Features", "Advanced Features","Study Plan Generator","Performance Analytics"], key="menu_type")
    if menu_choice=="Basic Features":
        main_options = ["Problem Solver", "Handwritten Problem Solver", "Practice Questions", "Concept Explorer", "Formula Generator", "Quiz"]
        selected_main = st.sidebar.radio("Basic Features", main_options,key="main_menu_radio")
        if selected_main and selected_main != st.session_state.selected_menu:
            st.session_state.selected_menu = selected_main

    elif menu_choice=="Advanced Features":
        advanced_options = ["Virtual Math Manipulatives", "Historical Math Context", "Real-World Applications", "Customizable Practice Sets", "AI Tutor Chat"]
        selected_advanced = st.sidebar.radio("Advanced Features", advanced_options,key="advanced_menu_radio")   
        if selected_advanced and selected_advanced != st.session_state.selected_menu:
            st.session_state.selected_menu = selected_advanced
        
    elif menu_choice=="Study Plan Generator":
        plan_options=["Study Plan Generator"]
        selected_plan=st.sidebar.radio("Study Plan Generator",plan_options,key="study_plan")
        if selected_plan and selected_plan != st.session_state.selected_menu:
            st.session_state.selected_menu = selected_plan
    
    elif menu_choice=="Performance Analytics":
        performance=["Performance Analytics"]
        selected_option=st.sidebar.radio("Performance Analytics",performance,key="performance_analytics")
        if selected_option and selected_option != st.session_state.selected_menu:
            st.session_state.selected_menu = selected_option
        
        st.sidebar.markdown("---")

    skill_level = st.sidebar.selectbox("Select your skill level:", ["Beginner", "Intermediate", "Advanced", "Expert"])
    topic = st.sidebar.selectbox("Choose a math topic:", ["Arithmetic", "Algebra", "Geometry", "Trigonometry", "Calculus", "Linear Algebra", "Statistics", "Number Theory", "Complex Analysis", "Differential Equations"])

    st.sidebar.markdown("---")

    progress = get_progress(st.session_state.user)
    st.sidebar.subheader("Your Progress")
    st.sidebar.write(f"Completed Topics: {', '.join(progress['completed_topics'])}")
    st.sidebar.write("Quiz Scores:")
    for t, score in progress['quiz_scores'].items():
        st.sidebar.write(f"{t}: {score}%")

    st.sidebar.markdown("---")

    if st.sidebar.button("Logout"):
        st.session_state.user = None
        st.rerun()
        
    def execute_function(option):
        if option == "Problem Solver":
            problem = st.text_area("Enter your math problem:")
            if st.button("Solve Step-by-Step"):
                if problem:
                    prompt = f"""Solve this {skill_level.lower()} level {topic.lower()} problem step by step, providing detailed explanations for each step."""
                    response = model.generate_content(prompt + problem)
                    render_math(response.text)
                    update_progress(st.session_state.user, topic)
                else:
                    st.warning("Please enter a math problem.")

        elif option == "Practice Questions":
            if st.button("Generate Practice Questions"):
                num_questions = 10
                prompt = f"""Generate {num_questions} {skill_level.lower()} level {topic.lower()} math questions with detailed solutions.
                Ensure each question and solution is in this format:
                Q: [question]\nS: [solution]\nSeparate each question-answer pair with a blank line."""
                
                try:
                    response = model.generate_content(prompt)
                    if not response or not hasattr(response, 'text'):
                        st.error("API response blocked or invalid. Please try again.")
                        return
                    
                    raw_text = response.text.strip()
                    
                    question_solution_pairs = re.findall(r"Q:\s*(.*?)\s*S:\s*(.*?)\n?", raw_text, re.DOTALL)
                    
                    if not question_solution_pairs:
                        st.error("Failed to extract questions and solutions. Please regenerate.")
                        return
                    
                    st.session_state.practice_questions = question_solution_pairs
                except Exception as e:
                    st.error(f"An error occurred: {e}")
                    return
            
            if "practice_questions" in st.session_state and st.session_state.practice_questions:
                for i, (q, s) in enumerate(st.session_state.practice_questions, 1):
                    st.subheader(f"Question {i}")
                    st.write(q.strip())
                    user_solution = st.text_area(f"Your Solution for Question {i}", key=f"solution_{i}")
                    
                    if st.button(f"Check Solution {i}", key=f"check_{i}"):
                        st.write("**Correct Solution:**")
                        st.write(s.strip())
                        
                        if user_solution.strip():
                            feedback_prompt = f"""Compare the following solutions and provide feedback:
                            Correct Solution: {s.strip()}
                            User's Solution: {user_solution.strip()}
                            Provide constructive feedback and suggestions for improvement."""
                            try:
                                feedback = model.generate_content(feedback_prompt)
                                st.write("**Feedback:**")
                                st.write(feedback.text)
                            except Exception as e:
                                st.error(f"An error occurred while generating feedback: {e}")
                
                st.markdown("""<br><br>""", unsafe_allow_html=True)
                
                if st.button("Reset Questions"):
                    del st.session_state.practice_questions
                    st.rerun()
            
        elif option == "Concept Explorer":
            concept = st.text_input("Enter a math concept you'd like explored:")
            if st.button("Explore Concept"):
                if concept.strip():
                    prompt = f"""Provide a comprehensive explanation of '{concept}' suitable for a {skill_level.lower()} level student. Include:
                    1. Definition
                    2. Historical context
                    3. Key principles
                    4. Real-world applications
                    5. Related concepts
                    6. Common misconceptions
                    7. Advanced implications (if applicable)"""
                    
                    try:
                        response = model.generate_content(prompt)
                        if not response or not hasattr(response, 'text'):
                            st.error("API response blocked or invalid. Please try again.")
                            return
                        render_math(response.text)
                        update_progress(st.session_state.user, concept)  
                    except Exception as e:
                        st.error(f"An error occurred: {e}")
                else:
                    st.warning("Please enter a math concept.")
                
        elif option == "Formula Generator":
            formula_topic = st.text_input("Enter a topic to generate relevant formulas:")
            if st.button("Generate Formulas"):
                if formula_topic.strip():
                    prompt = f"""Generate a comprehensive list of {skill_level.lower()} level formulas related to '{formula_topic}'.
                    For each formula, provide:
                    1. Formula name
                    2. The formula itself
                    3. A brief explanation of its use
                    4. Key variables explained
                    5. Any important conditions or limitations"""
                    
                    try:
                        response = model.generate_content(prompt)
                        if not response or not hasattr(response, 'text'):
                            st.error("API response blocked or invalid. Please try again.")
                            return
                        render_math(response.text)
                        update_progress(st.session_state.user, formula_topic)  
                    except Exception as e:
                        st.error(f"An error occurred: {e}")
                else:
                    st.warning("Please enter a topic for formula generation.")

        elif option == "Quiz":
            if "quiz_data" not in st.session_state:
                st.session_state.quiz_data = None 

            if st.button("Generate Quiz"):
                if st.session_state.quiz_data is None:
                    prompt = f"""
                    Create a multiple-choice quiz with exactly 5 unique questions on {topic}, suitable for a {skill_level.lower()} level student.
                    Each question must have:
                    - A unique math-related question
                    - 4 answer choices (A, B, C, D)
                    - The correct answer
                    - A brief explanation of the correct answer

                    **Format:**
                    Q: [Question]
                    A) [Option A]
                    B) [Option B]
                    C) [Option C]
                    D) [Option D]
                    Correct: [Correct option letter]
                    Explanation: [Brief explanation]

                    Separate each question with a blank line.
                    """
                    response = model.generate_content(prompt)
                    quiz_text = response.text.strip()

                    try:
                        question_pattern = re.findall(
                            r"Q:\s*(.*?)\s*A\)\s*(.*?)\s*B\)\s*(.*?)\s*C\)\s*(.*?)\s*D\)\s*(.*?)\s*Correct:\s*([A-D])\s*Explanation:\s*(.*?)\s*(?=Q:|$)", 
                            quiz_text, 
                            re.DOTALL
                        )

                        if len(question_pattern) != 5:
                            raise ValueError(f"Expected 5 questions, but found {len(question_pattern)}. Check AI formatting.")

                        st.session_state.quiz_data = []
                        for q in question_pattern:
                            question_text = q[0]
                            options = [f"A) {q[1]}", f"B) {q[2]}", f"C) {q[3]}", f"D) {q[4]}"]
                            correct_answer = q[5].strip().upper()
                            explanation = q[6]

                            st.session_state.quiz_data.append({
                                "question": question_text,
                                "options": options,
                                "correct_answer": correct_answer,
                                "explanation": explanation,
                                "user_answer": None,
                                "answered": False,
                            })

                    except (IndexError, ValueError) as e:
                        st.error(f"Error generating quiz: {e}")
                        st.write("Raw AI Response (for debugging):")
                        st.write(quiz_text)
                    except Exception as e:
                        st.error(f"Unexpected error: {e}")
                        st.write("Raw AI Response:")
                        st.write(quiz_text)

            if st.session_state.quiz_data:
                if "correct_answers" not in st.session_state:
                    st.session_state.correct_answers = 0

                st.subheader("Quiz Time! Select your answers:")
                
                for i, question_data in enumerate(st.session_state.quiz_data):
                    st.write(f"**Q{i+1}: {question_data['question']}**")
                    
                    user_answer = st.radio(
                        "Select your answer:",
                        question_data["options"],
                        key=f"q{i}",
                        index=None  
                    )

                    st.session_state.quiz_data[i]["user_answer"] = user_answer
                st.markdown("""<br><br>""", unsafe_allow_html=True)
                if st.button("Submit Quiz"):
                    correct_count = 0
                    
                    for i, question_data in enumerate(st.session_state.quiz_data):
                        if question_data["user_answer"]:
                            if question_data["user_answer"].startswith(question_data["correct_answer"]):
                                st.success(f"Q{i+1}: Correct!")
                                correct_count += 1
                            else:
                                st.error(f"Q{i+1}: Incorrect. The correct answer is {question_data['correct_answer']}.")
                            st.write(f"**Explanation:** {question_data['explanation']}")

                    score = (correct_count / len(st.session_state.quiz_data)) * 100
                    st.write(f"**Your Score: {score}%**")
                    update_progress(st.session_state.user, topic, score)

                if st.button("Retake Quiz"):
                    for q in st.session_state.quiz_data:
                        q["user_answer"] = None
                    st.session_state.correct_answers = 0
                    st.rerun()

                if st.button("Generate New Quiz"):
                    del st.session_state.quiz_data
                    del st.session_state.correct_answers
                    st.rerun()

        elif option == "Virtual Math Manipulatives":
            manipulative_type = st.selectbox("Choose a manipulative:", ["Fraction Visualizer", "Geometry Explorer", "Algebra Tiles"])
            
            if manipulative_type == "Fraction Visualizer":
                numerator = st.slider("Numerator", 1, 10, 3)
                denominator = st.slider("Denominator", 1, 10, 5)
                fig = go.Figure(go.Pie(values=[numerator, denominator - numerator], labels=["Filled", "Remaining"], hole=0.4))
                fig.update_layout(title=f"Fraction Representation: {numerator}/{denominator}")
                st.plotly_chart(fig)
                st.write(f"Decimal Equivalent: {numerator/denominator:.2f}")
            
            elif manipulative_type == "Geometry Explorer":
                shape = st.selectbox("Choose a shape:", ["Circle", "Square", "Triangle"])
                if shape == "Circle":
                    radius = st.slider("Radius", 1, 10, 5)
                    fig = go.Figure()
                    fig.add_shape(type="circle", xref="x", yref="y", x0=-radius, y0=-radius, x1=radius, y1=radius, line=dict(color="blue"))
                    fig.update_layout(title=f"Circle (Radius: {radius})", xaxis_range=[-radius-1, radius+1], yaxis_range=[-radius-1, radius+1])
                    st.plotly_chart(fig)
                    st.write(f"Area: {math.pi * radius**2:.2f}")
                    st.write(f"Circumference: {2 * math.pi * radius:.2f}")
                elif shape == "Square":
                    side = st.slider("Side length", 1, 10, 5)
                    fig = go.Figure()
                    fig.add_shape(type="rect", x0=0, y0=0, x1=side, y1=side, line=dict(color="red"))
                    fig.update_layout(title=f"Square (Side: {side})", xaxis_range=[-1, side+1], yaxis_range=[-1, side+1])
                    st.plotly_chart(fig)
                    st.write(f"Area: {side**2}")
                    st.write(f"Perimeter: {4*side}")
                elif shape == "Triangle":
                    base = st.slider("Base", 1, 10, 5)
                    height = st.slider("Height", 1, 10, 5)
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(x=[0, base, base/2, 0], y=[0, 0, height, 0], mode='lines', fill='toself'))
                    fig.update_layout(title=f"Triangle (Base: {base}, Height: {height})", xaxis_range=[-1, base+1], yaxis_range=[-1, height+1])
                    st.plotly_chart(fig)
                    st.write(f"Area: {0.5 * base * height}")
            
            elif manipulative_type == "Algebra Tiles":
                x_coeff = st.slider("Coefficient of x", -10, 10, 1)
                constant = st.slider("Constant term", -10, 10, 0)
                fig = go.Figure()
                
                for i in range(x_coeff if x_coeff > 0 else 0):
                    fig.add_shape(type="rect", x0=i, y0=0, x1=i+1, y1=1, line=dict(color="Blue"), fillcolor="LightBlue")
                for i in range(abs(x_coeff) if x_coeff < 0 else 0):
                    fig.add_shape(type="rect", x0=-i-1, y0=0, x1=-i, y1=1, line=dict(color="Red"), fillcolor="Pink")
                for i in range(constant if constant > 0 else 0):
                    fig.add_shape(type="rect", x0=i, y0=1, x1=i+1, y1=2, line=dict(color="Green"), fillcolor="LightGreen")
                for i in range(abs(constant) if constant < 0 else 0):
                    fig.add_shape(type="rect", x0=-i-1, y0=1, x1=-i, y1=2, line=dict(color="Orange"), fillcolor="LightSalmon")
                
                equation_value = st.number_input("Enter the equation value (e.g., for 'x + 3 = 5', enter 5)", value=0)
                fig.update_layout(title=f"Algebra Tiles: {x_coeff}x + {constant} = {equation_value}", xaxis_range=[-12, 12], yaxis_range=[-2, 4])
                st.plotly_chart(fig)
                st.write(f"Expression: {x_coeff}x + {constant} = {equation_value}")

        elif option == "Historical Math Context":
            historical_topic = st.text_input("Enter a mathematical concept or mathematician's name:")

            if st.button("Explore Historical Context"):
                prompt = f"""Provide historical context for the mathematical concept or mathematician '{historical_topic}'. Include:
                1. Key dates and events
                2. Major contributions to mathematics
                3. How this concept/person influenced the development of mathematics
                4. Interesting anecdotes or lesser-known facts"""

                try:
                    historical_context = model.generate_content(prompt)
                    if historical_context and hasattr(historical_context, 'text'):
                        st.subheader(f"📜 Historical Insights on {historical_topic}")
                        st.write(historical_context.text)

                        # Fun fact section
                        fun_fact_prompt = f"Give an unusual or fun fact about '{historical_topic}' in mathematics."
                        fun_fact = model.generate_content(fun_fact_prompt)
                        if fun_fact and hasattr(fun_fact, 'text'):
                            st.subheader("🤔 Did You Know?")
                            st.write(fun_fact.text)

                    else:
                        st.error("Failed to retrieve historical context. Please try again.")
                except Exception as e:
                    st.error(f"Error generating historical insights: {str(e)}")

        elif option == "Real-World Applications":
            application_area = st.selectbox("Choose an application area:", 
                ["Finance", "Physics", "Engineering", "Computer Science", "Biology"], key="application_area")
            
            if "generated_scenario" not in st.session_state:
                st.session_state.generated_scenario = None
            if "selected_application" not in st.session_state:
                st.session_state.selected_application = None
            if "generated_questions" not in st.session_state:
                st.session_state.generated_questions = None
            
            if True:
                if st.button("Generate Real-World Scenario"):
                    prompt = f"""Generate a unique and creative real-world scenario demonstrating the application of {topic} in {application_area} for a {skill_level.lower()} level learner. Ensure that each generated scenario is different from previous ones by exploring different perspectives, challenges, or real-life cases. 
                    Make it engaging and informative by including:
                    
                    1. A captivating real-life situation where {topic} plays a crucial role.
                    2. The core mathematical principles involved and why they matter.
                    3. A step-by-step breakdown of how the math is applied to solve the problem.
                    4. Practical takeaways for students or professionals in {application_area}.
                    5. A historical or fun fact related to {topic} in {application_area} to make learning interesting."""
                    
                    scenario = model.generate_content(prompt)
                    
                    if scenario and hasattr(scenario, 'text'):
                        st.session_state.generated_scenario = scenario.text
                        st.session_state.selected_application = application_area
                        
                        # Generate Practice Questions Immediately
                        question_prompt = f"""Generate three practice questions based on the following real-world scenario:
                        {st.session_state.generated_scenario}
                        Ensure the questions test the mathematical concepts applied in the scenario."""
                        
                        questions = model.generate_content(question_prompt)
                        
                        if questions and hasattr(questions, 'text'):
                            st.session_state.generated_questions = questions.text
                        else:
                            st.session_state.generated_questions = "Failed to retrieve practice questions. Please try again."
                    else:
                        st.error("Failed to retrieve the scenario. Please try again.")
            
            if st.session_state.generated_scenario:
                st.subheader("🌍 Real-World Math in Action:")
                st.write(st.session_state.generated_scenario)
                
                st.subheader("✅ Sample Solved Question:")
                sample_question_prompt = f"""Generate a worked-out example based on the following real-world scenario:
                {st.session_state.generated_scenario}
                Provide a step-by-step solution explaining the mathematical concepts applied."""
                sample_solution = model.generate_content(sample_question_prompt)
                
                if sample_solution and hasattr(sample_solution, 'text'):
                    st.write(sample_solution.text)
                else:
                    st.error("Failed to retrieve a sample solution. Please try again.")
                
                st.subheader("📝 Practice Questions:")
                st.write(st.session_state.generated_questions)

                st.markdown("""<br>""", unsafe_allow_html=True)
                if st.button("🔄 Reset", key="reset_scenario"):
                    st.session_state.generated_scenario = None
                    st.session_state.selected_application = None
                    st.session_state.generated_questions = None
                    st.rerun()

        elif option == "Customizable Practice Sets":
            num_questions = st.slider("Number of questions", 1, 10, 5)
            if st.button("Generate Practice Set"):
                unique_id = random.randint(1000, 9999)  # Add randomness to force unique questions
                prompt = f"""Generate a unique and fresh practice set of {num_questions} {skill_level.lower()} level {topic.lower()} questions. Include a mix of question types such as multiple-choice questions (MCQs), fill-in-the-blanks, and problem-solving exercises. Ensure each question covers a different concept or subtopic within {topic}, avoiding repetition. Ensure that each question covers a different concept or subtopic within {topic}. Avoid repeating similar types of problems and ensure each question has a distinct approach. 
                                        Format each question as 'Q[number]: [question]'""" 
                
                practice_set = model.generate_content(prompt)
                
                if practice_set and hasattr(practice_set, 'text'):
                    st.session_state.current_practice_set = practice_set.text.split('\n')
                else:
                    st.error("Failed to generate practice set. Please try again.")
            
            if st.session_state.current_practice_set:
                st.subheader("📚 Practice Set:")
                for q in st.session_state.current_practice_set:
                    st.write(q)
            
            if st.button("Save Practice Set as PDF"):
                if st.session_state.current_practice_set:
                    pdf_buffer = save_practice_set_as_pdf(st.session_state.current_practice_set)
                    st.download_button(label="Download PDF", data=pdf_buffer, file_name="practice_set.pdf", mime="application/pdf")
                    st.success("Practice set saved and ready for download!")
                else:
                    st.warning("Please generate a practice set first.")
        
        elif option == "AI Tutor Chat":
            if "messages" not in st.session_state:
                st.session_state.messages = []

            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

            if prompt := st.chat_input("Ask your question here:"):
                st.session_state.messages.append({"role": "user", "content": prompt})
                with st.chat_message("user"):
                    st.markdown(prompt)

                with st.chat_message("assistant"):
                    full_prompt = f"""You are an AI math tutor. The student's skill level is {skill_level} and they are studying {topic}. 
                    Answer the following question: {prompt}"""
                    response = model.generate_content(full_prompt)
                    st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})

        elif option == "Study Plan Generator":
            study_goal = st.text_input("Enter your study goal:")
            study_time = st.number_input("How many hours can you dedicate to studying per week?", min_value=1, max_value=40, value=10)
            if st.button("Generate Study Plan"):
                prompt = f"""Create a detailed, structured study plan for a {skill_level} level student focusing on {study_goal}. 
                They can dedicate {study_time} hours per week to studying. 
                Provide a well-structured week-by-week breakdown including:
                
                ## 📌 Topics to Cover
                - List the essential topics covered each week, ensuring a logical progression.
                
                ## 📚 Recommended Resources
                - Suggest textbooks, online courses, videos, and practice platforms.
                
                ## ✏️ Practice Exercises
                - Include sample problem sets, quizzes, and interactive exercises.
                
                ## 🎯 Milestones & Assessments
                - Define clear checkpoints to measure progress, with mini-tests or self-assessments."""
                study_plan = model.generate_content(prompt)
                formatted_text = study_plan.text.replace('Week ', '### Week ')
                st.markdown(formatted_text, unsafe_allow_html=True)

        elif option == "Performance Analytics":
            progress = get_progress(st.session_state.user)
            
            if progress['completed_topics']:
                topic_completion = pd.DataFrame({
                    'Topic': progress['completed_topics'],
                    'Completed': [1] * len(progress['completed_topics'])
                })
                if not topic_completion.empty:
                    fig_completion = px.bar(topic_completion, x='Topic', y='Completed', title='Completed Topics', text='Topic')
                    fig_completion.update_traces(
                        texttemplate='%{text}', 
                        textposition='inside',
                        insidetextanchor='middle',
                        textangle=90
                    )
                    fig_completion.update_layout(
                        xaxis_visible=False, 
                        yaxis_visible=False, 
                        showlegend=False,
                        uniformtext_minsize=12, 
                        uniformtext_mode='hide',
                        font=dict(color='white', size=14, family='Arial Black'),
                        bargap=0.2
                    )
                    st.plotly_chart(fig_completion)
                else:
                    st.write("No completed topics yet.")
            
            if progress['quiz_scores']:
                quiz_scores = pd.DataFrame({
                    'Topic': list(progress['quiz_scores'].keys()),
                    'Score': list(progress['quiz_scores'].values())
                })
                if not quiz_scores.empty:
                    fig_scores = px.line(quiz_scores, x='Topic', y='Score', title='Quiz Scores Over Time', markers=True)
                    st.plotly_chart(fig_scores)
                    
                    strength_threshold = 50
                    weaknesses = quiz_scores[quiz_scores['Score'] < strength_threshold]['Topic'].tolist()
                    strengths = quiz_scores[quiz_scores['Score'] >= strength_threshold]['Topic'].tolist()
                    
                    st.write(f"Your top strengths: {', '.join(strengths) if strengths else 'None'}")
                    st.write(f"Areas for improvement: {', '.join(weaknesses) if weaknesses else 'None (Great performance overall!)'}")
                else:
                    st.write("Not enough data to determine strengths and areas for improvement.")

        elif option == "Handwritten Problem Solver":
            uploaded_file = st.file_uploader("Upload an image of a handwritten math problem", type=["jpg", "jpeg", "png"])
            if uploaded_file is not None:
                extracted_text = extract_text_from_image(uploaded_file)
                st.write("Extracted Text:")
                st.write(extracted_text if extracted_text else "No text could be extracted from the image.")
                
                if extracted_text:
                    prompt = f"""Solve this {skill_level.lower()} level {topic.lower()} problem step by step, providing detailed explanations for each step. Problem: {extracted_text}"""
                    response = model.generate_content(prompt)
                    
                    st.write("Step-by-Step Solution:")
                    render_math(response.text)
                    update_progress(st.session_state.user, topic)

    st.markdown("<div class='main-content'>", unsafe_allow_html=True)
    if st.session_state.selected_menu:
        st.title(st.session_state.selected_menu)
        execute_function(st.session_state.selected_menu)    
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("Advanced Math Tutor")

else:
    st.warning("Please log in or sign up to access the Math Tutor.")

# Close the database connection when the app is done
conn.close()
