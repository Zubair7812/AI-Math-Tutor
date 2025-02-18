# AI Math Tutor

An interactive AI-powered math tutor web application built with Streamlit and Gemini API. This application offers a range of features to help students learn and practice mathematics, from basic arithmetic to advanced calculus, with AI-powered assistance.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgements](#acknowledgements)

## Features

- **Problem Solver:** Enter any math problem, and the AI will provide a step-by-step solution with detailed explanations, tailored to your chosen skill level (Beginner, Intermediate, Advanced, Expert) and topic.
- **Practice Questions:** Generate practice questions on various topics (Arithmetic, Algebra, Geometry, Trigonometry, Calculus, Linear Algebra, Statistics, Number Theory, Complex Analysis, Differential Equations) and skill levels.  Get feedback on your solutions.
- **Concept Explorer:** Explore mathematical concepts in depth. The AI provides comprehensive explanations, historical context, key principles, real-world applications, related concepts, common misconceptions, and advanced implications.
- **Formula Generator:** Generate relevant formulas for a given topic and skill level. The AI provides the formula name, the formula itself, an explanation of its use, key variables, and any important conditions or limitations.
- **Graph Visualizer:** Visualize mathematical functions by entering the function (e.g., sin(x), x^2, exp(-x)). The app plots the graph and provides insights on domain, range, intercepts, behavior at infinity, and notable features.
- **Quiz:** Test your knowledge with AI-generated quizzes.  Get immediate feedback and explanations for each question.  Track your scores over time.
- **Interactive Whiteboard:** Draw mathematical expressions using ASCII art, and the AI will interpret and display the mathematical notation.
- **Virtual Math Manipulatives:** Use interactive tools like Fraction Visualizers, Geometry Explorers, and Algebra Tiles to visualize and manipulate mathematical concepts.
- **Study Plan Generator:** Create personalized study plans based on your study goals, available time, skill level, and chosen topic. The AI provides a week-by-week plan with topics, resources, exercises, and milestones.
- **Historical Math Context:** Explore the history of mathematical concepts and mathematicians. Learn about key dates, events, major contributions, and how these concepts/people influenced mathematics.
- **Real-World Applications:** Discover real-world applications of math in various fields (Finance, Physics, Engineering, Computer Science, Biology). The AI provides scenarios and interactive simulations.
- **Customizable Practice Sets:** Create custom practice sets using AI-generated questions or by entering your own questions. Save and track your progress on these sets.
- **Performance Analytics:** Track your progress with visualizations of completed topics and quiz scores over time. Identify your strengths and areas for improvement.
- **Math Notation Guide:**  A quick reference guide for common mathematical symbols and notation, including Greek letters, operators, set theory symbols, and calculus notation.
- **AI Tutor Chat:** Get personalized help from an AI tutor. Ask questions and receive detailed explanations and guidance.
- **Math Game Center:** Play math-related games like Number Guessing and Math Trivia to make learning fun and engaging.

## Installation

1. Clone the repository: `git clone https://github.com/Zubair7812/AI-Math-Tutor.git`
2. Navigate to the project directory: `cd AI-Math-Tutor`
3. Create a virtual environment: `python -m venv .venv` (or `python3 -m venv .venv`)
4. Activate the virtual environment:
    - Windows: `.venv\Scripts\activate`
    - macOS/Linux: `source .venv/bin/activate`
5. Install dependencies: `pip install -r requirements.txt`
6. Create a `.env` file in the project root and add your Gemini API key: `GEMINI_API_KEY="YOUR_ACTUAL_API_KEY"`

## Usage

1. Run: `streamlit run app.py`
2. Open in your browser: Streamlit will provide the URL.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## License

MIT

## Acknowledgements

- Powered by Google Gemini.
- Built with Streamlit.
