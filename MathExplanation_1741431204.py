from manim import *

config.background_color = "#1f1f1f"

class LagrangesTheorem(Scene):
    def construct(self):
        # Define colors
        BLUE = "#64B5F6"
        GREEN = "#81C784"
        RED = "#EF5350"

        # Title
        title = Tex("Lagrange's Theorem").scale(1.5).set_color(WHITE)
        self.play(Write(title))
        self.wait(1)
        self.play(FadeOut(title))

        # State the theorem
        theorem_statement = MathTex(r"\text{If } G \text{ is a finite group and } H \text{ is a subgroup of } G, \text{ then the order of } H \text{ divides the order of } G.").scale(0.8).set_color(WHITE)
        self.play(Write(theorem_statement))
        self.wait(2)


        #Illustrative Example (Visual Representation needed -  adapt as per your preferred visualization)
        #Example: Consider a group G of order 12 and a subgroup H of order 3.
        example = MathTex(r"\text{Example: } |G| = 12, |H| = 3").scale(0.7).set_color(WHITE)
        self.play(Write(example))
        self.wait(1)

        #Visual Representation (Replace with your visualization)
        #Consider using circles to represent groups, smaller circle within larger to show subgroup relationship, and possibly animation to show cosets partitioning the larger group.


        #Conclusion
        conclusion = MathTex(r"3 \mid 12").set_color(GREEN).scale(0.9)
        self.play(Write(conclusion))
        self.wait(2)

        self.wait(3)
