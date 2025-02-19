import streamlit as st
import google.generativeai as genai
import random
import math
import plotly.graph_objects as go
import plotly.express as px
import networkx as nx
import numpy as np
import hashlib
import sqlite3
import json
from datetime import datetime
import pandas as pd

# Configure the Google Gemini API
genai.configure(api_key="AIzaSyBJFPgfKibzvITEATEwXtzNPMO--chg5GU")
model = genai.GenerativeModel('gemini-1.5-flash-latest')

# Set up the Streamlit app
st.set_page_config(page_title="Advanced AI Math Tutor", layout="wide", initial_sidebar_state="expanded")

# Custom CSS for a vibrant dark theme and restructured layout
st.markdown("""
<style>
.stApp {
    background-color: #1a1a1a; /* Dark background */
    color: #e0e0e0; /* Light text color */
}
/* Sidebar styling */
.stSidebar {
    background-color: #282828; /* Darker sidebar */
    padding: 20px;
}
.stSidebar .stRadio { /* Style radio buttons */
    color: #a0a0a0;
}
.stSidebar .stSelectbox { /* Style select boxes */
    background-color: #383838;
}

/* Main content area */
.main-content {
    padding: 20px;
    margin-left: 250px; /* Adjust for sidebar width */
}

/* Buttons */
.stButton>button {
    background-color: #673ab7; /* Deep purple */
    color: white;
    border-radius: 8px;
    padding: 0.75rem 1.5rem;
    font-size: 1.1rem;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
    transition: background-color 0.3s ease;
}
.stButton>button:hover {
    background-color: #512da8; /* Darker purple on hover */
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.35);
}

/* Inputs, Text Areas, Select Boxes */
.stTextInput>div>div>input, .stTextArea textarea, .stSelectbox>div>div>select {
    background-color: #383838; /* Darker input background */
    color: #e0e0e0;
    border-radius: 8px;
    border: 1px solid #555; /* Slightly lighter border */
}

/* Headings */
h1, h2, h3 {
    color: #9575cd; /* Lighter purple for headings */
}

/* Code blocks */
code {
    background-color: #333;
    color: #eee;
    padding: 0.2rem 0.4rem;
    border-radius: 4px;
}

/* Tables */
table {
    background-color: #333;
}
th, td {
    border: 1px solid #555;
    padding: 8px;
}

/* Links */
a {
    color: #4fc3f7; /* Light blue for links */
}

/* Progress bar */
.stProgress > div > div {
    background-color: #673ab7 !important;
}

/* Alerts (Success, Info, Warning, Error) */
.stAlert {
    background-color: #424242;
    color: #e0e0e0;
    border-radius: 8px;
    padding: 1rem;
    margin-bottom: 1rem;
}
.stAlert-success { border-left: 5px solid #4caf50; } /* Green */
.stAlert-info { border-left: 5px solid #2196f3; }    /* Blue */
.stAlert-warning { border-left: 5px solid #ff9800; } /* Orange */
.stAlert-error { border-left: 5px solid #f44336; }  /* Red */


</style>
""", unsafe_allow_html=True)

# Helper function to render mathematical expressions
def render_math(text):
    st.write(text)

# Database setup
conn = sqlite3.connect('math_tutor.db')
c = conn.cursor()

# Create the users table if it doesn't exist.  This is the crucial change.
c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password TEXT,
        progress TEXT
    )
""")
conn.commit()  # Commit the table creation

# Now that the table definitely exists, you can safely alter it
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

# Login/Signup
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
        # Main Navigation
        main_options = ["Problem Solver", "Practice Questions", "Concept Explorer", "Formula Generator", "Graph Visualizer", "Quiz"]
        selected_main = st.sidebar.radio("Basic Features", main_options,key="main_menu_radio")
        if selected_main and selected_main != st.session_state.selected_menu:
            st.session_state.selected_menu = selected_main

    elif menu_choice=="Advanced Features":
        # Advanced Features
        advanced_options = ["Interactive Whiteboard", "Virtual Math Manipulatives", "Historical Math Context", "Real-World Applications", "Customizable Practice Sets", "AI Tutor Chat", "Math Game Center"]
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

    # Skill/Topic Selection
    skill_level = st.sidebar.selectbox("Select your skill level:", ["Beginner", "Intermediate", "Advanced", "Expert"])
    topic = st.sidebar.selectbox("Choose a math topic:", ["Arithmetic", "Algebra", "Geometry", "Trigonometry", "Calculus", "Linear Algebra", "Statistics", "Number Theory", "Complex Analysis", "Differential Equations"])

    st.sidebar.markdown("---")

    # Progress Tracking
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
                prompt = f"""Generate 5 {skill_level.lower()} level {topic.lower()} math questions with detailed solutions. 
                Format each question and solution as 'Q: [question] S: [step-by-step solution]'"""
                response = model.generate_content(prompt)
                questions = response.text.split('\n\n')
                
                for i, qs in enumerate(questions, 1):
                    parts = qs.split('S:')
                    if len(parts) == 2:
                        q, s = parts
                    else:
                        q, s = qs, "Solution not provided in the expected format."
                    st.subheader(f"Question {i}")
                    st.write(q.replace('Q:', '').strip())
                    user_solution = st.text_area(f"Your solution for Question {i}", key=f"solution_{i}")
                    if st.button(f"Check Solution {i}", key=f"check_{i}"):
                        st.write("Correct solution:")
                        render_math(s)
                        if user_solution:
                            prompt = f"""Compare the following two solutions and provide feedback:
                            Correct solution: {s.strip()}
                            User's solution: {user_solution}
                            Provide constructive feedback and suggestions for improvement."""
                            feedback = model.generate_content(prompt)
                            st.write("Feedback:")
                            st.write(feedback.text)
                        else:
                            st.warning("Please provide your solution before checking.")
                update_progress(st.session_state.user, topic)

        elif option == "Concept Explorer":
            concept = st.text_input("Enter a math concept you'd like explored:")
            if st.button("Explore Concept"):
                if concept:
                    prompt = f"""Provide a comprehensive explanation of the {topic.lower()} concept '{concept}' suitable for a {skill_level.lower()} level student. Include:
                    1. Definition
                    2. Historical context
                    3. Key principles
                    4. Real-world applications
                    5. Related concepts
                    6. Common misconceptions
                    7. Advanced implications (if applicable)"""
                    response = model.generate_content(prompt)
                    render_math(response.text)
                    update_progress(st.session_state.user, topic)
                else:
                    st.warning("Please enter a math concept.")

        elif option == "Formula Generator":
            formula_topic = st.text_input("Enter a topic to generate relevant formulas:")
            if st.button("Generate Formulas"):
                if formula_topic:
                    prompt = f"""Generate a comprehensive list of {skill_level.lower()} level formulas related to {formula_topic} in {topic}. For each formula, provide:
                    1. Formula name
                    2. The formula itself
                    3. A brief explanation of its use
                    4. Key variables explained
                    5. Any important conditions or limitations"""
                    response = model.generate_content(prompt)
                    render_math(response.text)
                    update_progress(st.session_state.user, topic)
                else:
                    st.warning("Please enter a topic for formula generation.")

        elif option == "Graph Visualizer":
            function = st.text_input("Enter a mathematical function to visualize (e.g., sin(x), x^2, exp(-x)):")
            if st.button("Visualize"):
                if function:
                    function = function.replace("^", "**").replace("sin", "np.sin").replace("cos", "np.cos").replace("tan", "np.tan").replace("exp", "np.exp").replace("log", "np.log").replace("sqrt", "np.sqrt")
                    x = np.linspace(-10, 10, 1000)
                    try:
                        y = eval(function)
                        fig = go.Figure(data=go.Scatter(x=x, y=y, mode='lines'))
                        fig.update_layout(title=f'Graph of {function}', xaxis_title='x', yaxis_title='y', template="plotly_dark")
                        st.plotly_chart(fig)
                        
                        prompt = f"""Analyze the function f(x) = {function}. Provide insights on:
                        1. Domain and range
                        2. Intercepts (if easily determined)
                        3. Behavior as x approaches infinity and negative infinity
                        4. Any notable features (e.g., periodicity, symmetry)
                        5. Applications of this function in {topic.lower()}"""
                        insights = model.generate_content(prompt)
                        st.subheader("Function Insights:")
                        render_math(insights.text)
                        update_progress(st.session_state.user, topic)
                    except Exception as e:
                        st.error(f"Error: {str(e)}. Please enter a valid mathematical expression.")
                else:
                    st.warning("Please enter a function to visualize.")

        elif option == "Quiz":
            if st.button("Generate Quiz"):
                st.session_state.quiz_data = None  # Reset quiz data
                prompt = f"""Create a multiple choice quiz with 5 questions on {topic} suitable for a {skill_level.lower()} level student. 
                For each question, provide 4 options (A, B, C, D) and indicate the correct answer. 
                Format as follows:

                Q1: [Question 1]
                A. [Option A]
                B. [Option B]
                C. [Option C]
                D. [Option D]
                Correct: [Correct option letter]
                Explanation: [Brief explanation of the correct answer]

                Q2: [Question 2]
                ... (and so on for 5 questions)

                Do NOT include any extra newlines or blank lines at the beginning or end of your response.
                """

                response = model.generate_content(prompt)
                quiz_text = response.text.strip()

                try:
                    questions = quiz_text.split('\n\n')

                    if len(questions) != 5:
                        raise ValueError(f"Expected 5 questions, got {len(questions)}. API response format is incorrect. Raw text: {quiz_text}")

                    st.session_state.quiz_data = []
                    for i, q in enumerate(questions):
                        parts = q.split('\n')

                        if len(parts) < 7:
                            raise ValueError(f"Question {i+1} format is incorrect. Expected at least 7 lines, got {len(parts)}. Raw question: {q}")

                        question_text = parts[0].split(': ')[1]
                        options = parts[1:5]
                        correct_answer = parts[5].split(': ')[1].strip().upper()
                        explanation = parts[6].split(': ')[1]

                        st.session_state.quiz_data.append({
                            "question": question_text,
                            "options": options,
                            "correct_answer": correct_answer,
                            "explanation": explanation,
                            "user_answer": None,
                            "show_result": False,
                            "answered": False,  # Initialize answered flag
                        })

                except (IndexError, ValueError) as e:
                    st.error(f"Error generating or processing quiz: {e}")
                    st.write("Raw API Response (for debugging):")
                    st.write(quiz_text)
                except Exception as e:
                    st.error(f"An unexpected error occurred: {e}")
                    st.write("Raw API Response (for debugging):")
                    st.write(quiz_text)

            if "quiz_data" in st.session_state and st.session_state.quiz_data is not None:
                if "correct_answers" not in st.session_state:
                    st.session_state.correct_answers = 0

                for i, question_data in enumerate(st.session_state.quiz_data):
                    st.subheader(question_data["question"])
                    user_answer = st.radio("Select your answer:", question_data["options"], key=f"q{i}")

                    if st.button("Check", key=f"check_{i}"):
                        question_data["user_answer"] = user_answer
                        question_data["show_result"] = True

                        if user_answer.startswith(question_data["correct_answer"]):
                            st.success("Correct!")
                            if not question_data["answered"]:
                                st.session_state.correct_answers += 1
                                question_data["answered"] = True
                        else:
                            st.error(f"Incorrect. The correct answer is {question_data['correct_answer']}.")
                            question_data["answered"] = True

                        st.write("Explanation:")
                        render_math(question_data["explanation"])

                score = (st.session_state.correct_answers / len(st.session_state.quiz_data)) * 100
                st.write(f"Your score: {score}%")
                update_progress(st.session_state.user, topic, score)

                if st.button("Reset Quiz"):
                    del st.session_state.quiz_data
                    del st.session_state.correct_answers
                    st.rerun()
        
        elif option == "Interactive Whiteboard":
            drawing = st.text_area("Draw your mathematical expressions here (use ASCII art):")
            if st.button("Interpret Drawing"):
                prompt = f"Interpret the following ASCII art representation of a mathematical expression: {drawing}"
                interpretation = model.generate_content(prompt)
                st.write("Interpretation:")
                st.write(interpretation.text)

        elif option  == "Virtual Math Manipulatives":
            manipulative_type = st.selectbox("Choose a manipulative:", ["Fraction Visualizer", "Geometry Explorer", "Algebra Tiles"])
            
            if manipulative_type == "Fraction Visualizer":
                numerator = st.number_input("Numerator", min_value=0, max_value=10, value=1)
                denominator = st.number_input("Denominator", min_value=1, max_value=10, value=2)
                fig = go.Figure(go.Pie(values=[numerator, denominator-numerator], labels=["Numerator", "Remainder"], hole=.3))
                fig.update_layout(title=f"Fraction: {numerator}/{denominator}")
                st.plotly_chart(fig)
            
            elif manipulative_type == "Geometry Explorer":
                shape = st.selectbox("Choose a shape:", ["Circle", "Square", "Triangle"])
                if shape == "Circle":
                    radius = st.slider("Radius", 1, 10, 5)
                    fig = go.Figure(go.Scatter(x=[0], y=[0], mode='markers', marker=dict(size=radius*20, color='blue')))
                    fig.update_layout(title=f"Circle with radius {radius}", xaxis_range=[-10, 10], yaxis_range=[-10, 10])
                    st.plotly_chart(fig)
                    st.write(f"Area: {math.pi * radius**2:.2f}")
                    st.write(f"Circumference: {2 * math.pi * radius:.2f}")
                elif shape == "Square":
                    side = st.slider("Side length", 1, 10, 5)
                    fig = go.Figure(go.Scatter(x=[0,side,side,0,0], y=[0,0,side,side,0], mode='lines', fill="toself"))
                    fig.update_layout(title=f"Square with side {side}", xaxis_range=[-1, 11], yaxis_range=[-1, 11])
                    st.plotly_chart(fig)
                    st.write(f"Area: {side**2}")
                    st.write(f"Perimeter: {4*side}")
                elif shape == "Triangle":
                    base = st.slider("Base", 1, 10, 5)
                    height = st.slider("Height", 1, 10, 5)
                    fig = go.Figure(go.Scatter(x=[0,base,base/2,0], y=[0,0,height,0], mode='lines', fill="toself"))
                    fig.update_layout(title=f"Triangle with base {base} and height {height}", xaxis_range=[-1, 11], yaxis_range=[-1, 11])
                    st.plotly_chart(fig)
                    st.write(f"Area: {0.5 * base * height}")
                    st.write(f"Perimeter: {base + 2 * math.sqrt((base/2)**2 + height**2):.2f}")

            elif manipulative_type == "Algebra Tiles":
                x_coeff = st.slider("Coefficient of x", -5, 5, 1)
                constant = st.slider("Constant term", -5, 5, 0)
                fig = go.Figure()
                for i in range(abs(x_coeff)):
                    fig.add_shape(type="rect", x0=i, y0=0, x1=i+1, y1=1, line=dict(color="Blue"), fillcolor="LightBlue")
                for i in range(abs(constant)):
                    fig.add_shape(type="rect", x0=i, y0=1, x1=i+1, y1=2, line=dict(color="Red"), fillcolor="LightPink")
                fig.update_layout(title=f"Algebra Tiles: {x_coeff}x + {constant}", xaxis_range=[-1, 6], yaxis_range=[-1, 3])
                st.plotly_chart(fig)
                st.write(f"Expression: {x_coeff}x + {constant}")

        elif option == "Historical Math Context":
            historical_topic = st.text_input("Enter a mathematical concept or mathematician's name:")
            if st.button("Explore Historical Context"):
                prompt = f"""Provide historical context for the mathematical concept or mathematician '{historical_topic}'. Include:
                1. Key dates and events
                2. Major contributions to mathematics
                3. How this concept/person influenced the development of mathematics
                4. Interesting anecdotes or lesser-known facts"""
                historical_context = model.generate_content(prompt)
                st.write(historical_context.text)

        elif option == "Real-World Applications":
            application_area = st.selectbox("Choose an application area:", 
                ["Finance", "Physics", "Engineering", "Computer Science", "Biology"])
            if st.button("Generate Real-World Scenario"):
                prompt = f"""Create a real-world scenario that demonstrates the application of {topic} in {application_area}. Include:
                1. A brief description of the scenario
                2. The specific mathematical concept being applied
                3. How the math is used to solve a problem or make a decision in this scenario
                4. A simple simulation or calculation that the user can interact with"""
                scenario = model.generate_content(prompt)
                st.write(scenario.text)
                
                st.write("Interactive Simulation:")
                user_input = st.number_input("Enter a value for the simulation:")
                if st.button("Run Simulation"):
                    result = user_input * 2  # This is just a placeholder calculation
                    st.write(f"Simulation result: {result}")

        elif option == "Customizable Practice Sets":
            practice_type = st.radio("Choose practice set type:", ["AI-Generated", "Custom"])
            
            if practice_type == "AI-Generated":
                num_questions = st.slider("Number of questions", 1, 10, 5)
                if st.button("Generate Practice Set"):
                    prompt = f"""Generate a practice set of {num_questions} {skill_level.lower()} level {topic.lower()} questions. 
                    Format each question as 'Q[number]: [question]'"""
                    practice_set = model.generate_content(prompt)
                    st.session_state.current_practice_set = practice_set.text.split('\n')
                    for q in st.session_state.current_practice_set:
                        st.write(q)
            else:
                custom_questions = st.text_area("Enter your custom questions (one per line):")
                if st.button("Create Custom Practice Set"):
                    st.session_state.current_practice_set = custom_questions.split('\n')
                    for q in st.session_state.current_practice_set:
                        st.write(q)
            
            if st.button("Save Practice Set"):
                if hasattr(st.session_state, 'current_practice_set'):
                    update_progress(st.session_state.user, topic, practice_set=st.session_state.current_practice_set)
                    st.success("Practice set saved successfully!")
                else:
                    st.warning("Please generate or create a practice set first.")

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

        elif option == "Math Game Center":
            game_type = st.selectbox("Choose a game:", ["Number Guessing", "Math Trivia"])
            
            if game_type == "Number Guessing":
                st.subheader("Number Guessing Game")

                if 'number' not in st.session_state:
                    st.session_state.number = random.randint(1, 100)
                    st.session_state.guesses = 0
                    st.session_state.lower_bound = 1
                    st.session_state.upper_bound = 100
                    st.session_state.hint_range = 10
                    st.session_state.max_guesses = 5  # Set maximum guesses

                guess = st.number_input(
                    f"Guess a number between {st.session_state.lower_bound} and {st.session_state.upper_bound}:",
                    min_value=st.session_state.lower_bound,
                    max_value=st.session_state.upper_bound,
                )

                if st.button("Submit Guess"):
                    st.session_state.guesses += 1

                    if guess == st.session_state.number:
                        st.success(f"Congratulations! You guessed the number in {st.session_state.guesses} tries.")
                        if st.button("Play Again"):
                            del st.session_state.number
                            del st.session_state.guesses
                            del st.session_state.lower_bound
                            del st.session_state.upper_bound
                            del st.session_state.hint_range
                            del st.session_state.max_guesses  #Reset max guesses
                            st.rerun()

                    elif st.session_state.guesses >= st.session_state.max_guesses:  # Check for max guesses
                        st.error(f"You've reached the maximum number of guesses ({st.session_state.max_guesses}). The number was {st.session_state.number}.")
                        if st.button("Play Again"):  # Offer "Play Again"
                            del st.session_state.number
                            del st.session_state.guesses
                            del st.session_state.lower_bound
                            del st.session_state.upper_bound
                            del st.session_state.hint_range
                            del st.session_state.max_guesses #Reset max guesses
                            st.rerun()

                    else:  # Handle incorrect guesses (same logic as before)
                        if guess < st.session_state.number:
                            new_lower = max(st.session_state.lower_bound, guess + 1)
                            new_upper = min(st.session_state.upper_bound, guess + st.session_state.hint_range)
                            st.warning(f"Too low! Try a number between {new_lower} and {new_upper}.")
                            st.session_state.lower_bound = new_lower
                            st.session_state.upper_bound = new_upper

                        else:  # Too high
                            new_lower = max(st.session_state.lower_bound, guess - st.session_state.hint_range)
                            new_upper = min(st.session_state.upper_bound, guess - 1)
                            st.warning(f"Too high! Try a number between {new_lower} and {new_upper}.")
                            st.session_state.lower_bound = new_lower
                            st.session_state.upper_bound = new_upper

                    st.write(f"Guesses so far: {st.session_state.guesses}")
            
            elif game_type == "Math Trivia":
                st.subheader("Math Trivia")

                if "trivia_question" not in st.session_state or st.button("Generate Trivia Question"):  # Check if trivia exists or the button is clicked
                    prompt = f"Generate a {skill_level} level math trivia question related to {topic} with 4 multiple choice answers. Indicate the correct answer. Format the response STRICTLY as follows:\n\nQuestion: [The question]\nA: [Option A]\nB: [Option B]\nC: [Option C]\nD: [Option D]\nCorrect: [Correct option letter]"

                    response = model.generate_content(prompt)

                    try:
                        lines = response.text.split('\n')
                        if len(lines) < 6:
                            raise ValueError("API response format is incorrect. Expected at least 6 lines.")

                        st.session_state.trivia_question = {  # Store the trivia in session state
                            "question": lines[0].split(': ')[1],
                            "options": lines[1:5],
                            "correct_answer": lines[5].split(': ')[1].strip()
                        }
                        st.session_state.show_solution = False # Initialize show_solution


                    except (IndexError, ValueError) as e:
                        st.error(f"Error generating trivia question: {e}")
                        st.write("Raw API Response (for debugging):")
                        st.write(response.text)
                    except Exception as e:
                        st.error(f"An unexpected error occurred: {e}")
                        st.write("Raw API Response (for debugging):")
                        st.write(response.text)


                if "trivia_question" in st.session_state:  # Display the trivia if it exists in session state
                    st.write(st.session_state.trivia_question["question"])
                    user_answer = st.radio("Choose your answer:", st.session_state.trivia_question["options"])

                    if st.button("Check Answer"):
                        st.session_state.show_solution = True # Set show_solution to True
                        if user_answer.startswith(st.session_state.trivia_question["correct_answer"]):
                            st.success("Correct!")
                        else:
                            st.error(f"Incorrect. The correct answer is {st.session_state.trivia_question['correct_answer']}.")

                    if st.session_state.show_solution: # Show solution only after checking
                        st.write(f"Solution: {st.session_state.trivia_question['correct_answer']}")

        elif option == "Study Plan Generator":
            study_goal = st.text_input("Enter your study goal:")
            study_time = st.number_input("How many hours can you dedicate to studying per week?", min_value=1, max_value=40, value=10)
            if st.button("Generate Study Plan"):
                prompt = f"""Create a personalized study plan for a {skill_level} level student focusing on {topic}. 
                Their goal is: {study_goal}. They can dedicate {study_time} hours per week to studying. 
                Provide a week-by-week plan including:
                1. Topics to cover
                2. Recommended resources (textbooks, online courses, etc.)
                3. Practice exercises
                4. Milestones to track progress"""
                study_plan = model.generate_content(prompt)
                st.write(study_plan.text)

        elif option  == "Performance Analytics":
            progress = get_progress(st.session_state.user)
            
            topic_completion = pd.DataFrame({
                'Topic': progress['completed_topics'],
                'Completed': [1] * len(progress['completed_topics'])
            })
            fig_completion = px.bar(topic_completion, x='Topic', y='Completed', title='Completed Topics')
            st.plotly_chart(fig_completion)

            quiz_scores = pd.DataFrame({
                'Topic': list(progress['quiz_scores'].keys()),
                'Score': list(progress['quiz_scores'].values())
            })
            fig_scores = px.line(quiz_scores, x='Topic', y='Score', title='Quiz Scores Over Time')
            st.plotly_chart(fig_scores)

            if quiz_scores.empty:
                st.write("Not enough data to determine strengths and areas for improvement.")
            else:
                strength = quiz_scores.loc[quiz_scores['Score'].idxmax(), 'Topic']
                weakness = quiz_scores.loc[quiz_scores['Score'].idxmin(), 'Topic']
                st.write(f"Your strength: {strength}")
                st.write(f"Area for improvement: {weakness}")


    # Main content based on selected page
    st.markdown("<div class='main-content'>", unsafe_allow_html=True)
    if st.session_state.selected_menu:
        st.title(st.session_state.selected_menu)
        execute_function(st.session_state.selected_menu)  # Call the relevant function       
    st.markdown("</div>", unsafe_allow_html=True)
    # Footer
    st.markdown("---")
    st.markdown("Advanced Math Tutor")

else:
    st.warning("Please log in or sign up to access the Math Tutor.")

# Close the database connection when the app is done
conn.close()
