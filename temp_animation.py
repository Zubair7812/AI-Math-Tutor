
from manim import *

class MathAnimation(Scene):
    def construct(self):
        # Display the problem statement
        problem = MathTex(r"Prove that a² + b² = c²")
        self.play(Write(problem))
        self.wait(2)
        
        # Add step-by-step explanation
        explanation = MathTex(r"Step 1: Start with the Pythagorean theorem.\nStep 2: Explain why a² + b² = c².")
        self.play(Transform(problem, explanation))
        self.wait(2)
        
        # Draw a right-angled triangle
        triangle = Polygon([-2, -1, 0], [2, -1, 0], [2, 1, 0], color=BLUE)
        self.play(Create(triangle))
        self.wait(1)
        
        # Label the sides
        a_label = MathTex("a").next_to(triangle, LEFT)
        b_label = MathTex("b").next_to(triangle, DOWN)
        c_label = MathTex("c").next_to(triangle, UP)
        self.play(Write(a_label), Write(b_label), Write(c_label))
        self.wait(2)
