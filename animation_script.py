
from manim import *

class MathAnimation(Scene):
    def construct(self):
        text = MathTex(r"\text{Prove that } a^2 + b^2 = c^2")
        self.play(Write(text))
        self.wait(2)
