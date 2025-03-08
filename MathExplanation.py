from manim import *

class OnePlusTwo(Scene):
    def construct(self):
        # Title
        title = Text("1 + 2 = ?").scale(1.5)
        self.play(Write(title))
        self.wait(1)

        #Represent 1 with a single dot
        one_dot = Dot(color=BLUE).scale(1.5)
        one_label = Tex("1").next_to(one_dot, RIGHT, buff=0.5)
        one_group = VGroup(one_dot, one_label)
        one_group.to_edge(LEFT)
        self.play(DrawBorderThenFill(one_dot), Write(one_label))
        self.wait(0.5)


        #Represent 2 with two dots
        two_dots = VGroup(Dot(color=RED).scale(1.5), Dot(color=RED).scale(1.5))
        two_dots.arrange(RIGHT, buff=0.5)
        two_dots.next_to(one_group, RIGHT, buff=1)
        two_label = Tex("2").next_to(two_dots, RIGHT, buff=0.5)
        two_group = VGroup(two_dots, two_label)
        self.play(DrawBorderThenFill(two_dots[0]), DrawBorderThenFill(two_dots[1]), Write(two_label))
        self.wait(0.5)


        #Plus sign
        plus_sign = Tex("+").move_to(np.mean([one_group.get_center(), two_group.get_center()], axis=0))
        self.play(Write(plus_sign))
        self.wait(0.5)


        # Combining the dots
        combined_dots = VGroup(one_dot, two_dots)
        combined_dots.arrange(RIGHT, buff=0.5)
        combined_dots.to_edge(LEFT)
        combined_dots.shift(DOWN*0.5)

        #Equals sign
        equals_sign = Tex("=").next_to(combined_dots, RIGHT, buff=0.5)

        #Result
        result = Tex("3").next_to(equals_sign, RIGHT, buff=0.5)
        self.play(Transform(one_group, combined_dots), Transform(two_group, [combined_dots[1], combined_dots[2]]), Write(equals_sign), Write(result))

        self.wait(1)

        # Final Equation
        final_equation = Tex("1 + 2 = 3").scale(1.5).to_edge(UP)
        self.play(Transform(title, final_equation))
        self.wait(2)
