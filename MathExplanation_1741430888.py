from manim import *

config.background_color = "#1f1f1f"

class CayleyTheorem(Scene):
    def construct(self):
        # Title
        title = Tex("Cayley's Theorem").set_color(YELLOW).scale(1.5)
        self.play(Write(title))
        self.wait(1)
        self.play(FadeOut(title))

        # Group Setup
        group_setup = VGroup()

        # Define a group G
        G = ["e", "a", "b", "c"]
        G_text = Tex("G = \\{e, a, b, c\\}").set_color(BLUE)
        group_setup.add(G_text)

        # Cayley table
        cayley_table = MathTable(
            [[r"\cdot", "e", "a", "b", "c"],
             ["e", "e", "a", "b", "c"],
             ["a", "a", "e", "c", "b"],
             ["b", "b", "c", "e", "a"],
             ["c", "c", "b", "a", "e"]],
            include_outer_lines=True
        ).set_color(WHITE)
        group_setup.add(cayley_table)

        # Animation of Group Setup
        self.play(DrawBorderThenFill(group_setup), run_time=2, progress_bar=True)
        self.wait(1)

        # Explanation of the Theorem
        theorem_explanation = Tex("Cayley's Theorem: Every group is isomorphic to a subgroup of a symmetric group").set_color(GREEN).scale(0.8)
        self.play(Write(theorem_explanation))
        self.wait(2)
        self.play(FadeOut(theorem_explanation))

        #Action on G (Left regular representation)
        action_explanation = Tex("Left regular representation: Each group element acts on G by left multiplication.").set_color(YELLOW).scale(0.8)
        self.play(Write(action_explanation))
        self.wait(2)
        self.play(FadeOut(action_explanation))


        # Show the action
        action_example = MathTex("a \cdot G = \\{a \cdot e, a \cdot a, a \cdot b, a \cdot c\\} = \\{a, e, c, b\\}").set_color(BLUE).scale(0.8)
        self.play(Write(action_example))
        self.wait(2)
        self.play(FadeOut(action_example))

        # Symmetric group
        symmetric_group = Tex("S_4").set_color(WHITE).scale(1.2)
        self.play(Write(symmetric_group))
        self.wait(1)
        self.play(FadeOut(symmetric_group))

        # Conclusion
        conclusion = Tex("G is isomorphic to a subgroup of S_4").set_color(GREEN).scale(1)
        self.play(Write(conclusion))
        self.wait(3)
        self.play(FadeOut(conclusion))


        self.wait(3)
