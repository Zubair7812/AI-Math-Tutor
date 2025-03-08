from manim import *

config.background_color = "#1f1f1f"

class CayleyTheorem(Scene):
    def construct(self):
        # Define colors
        BLUE = BLUE_B
        GREEN = GREEN_B
        RED = RED_B

        # Title
        title = Tex("Cayley's Theorem").scale(1.5).set_color(YELLOW)
        self.play(Write(title))
        self.wait(1)
        self.play(FadeOut(title))

        # Group elements
        G = VGroup(
            Tex("G", font_size=72).set_color(BLUE),
            Tex("=", font_size=72),
            Tex("Group", font_size=72).set_color(BLUE)
        ).arrange(RIGHT, buff=0.5)
        self.play(Write(G))
        self.wait(1)

        # Introduce a group action
        action = Tex("G \\times G \\to G", font_size=64).set_color(BLUE)
        self.play(Write(action))
        self.wait(1)


        #Permutation representation
        perm_rep = Tex("\\phi: G \\to S_G", font_size=64).set_color(BLUE)
        self.play(TransformMatchingTex(action, perm_rep))
        self.wait(1)

        #Explain the map
        explanation = Tex("where $\\phi(g)(x) = gx$ for all $x \\in G$", font_size=48).set_color(WHITE)
        self.play(Write(explanation))
        self.wait(2)

        #Illustrate homomorphism
        homomorphism = Tex("\\phi(gh) = \\phi(g)\\phi(h)", font_size=64).set_color(BLUE)
        self.play(Write(homomorphism))
        self.wait(1)

        #Conclusion
        conclusion = Tex("G is isomorphic to a subgroup of $S_G$", font_size=64).set_color(GREEN)
        self.play(Write(conclusion))
        self.wait(3)

        self.wait(3)

