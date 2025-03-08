from manim import *

class OnePlusTwo(Scene):
    def construct(self):
        #Create numbers
        one = Tex("1").scale(2)
        two = Tex("2").scale(2)
        plus = Tex("+").scale(2)
        equals = Tex("=").scale(2)
        three = Tex("3").scale(2)

        #Arrange initial equation
        equation = VGroup(one,plus,two)
        equation.arrange(RIGHT,buff=0.5)
        self.play(Write(equation))

        #Highlighting the numbers
        self.play(
            one.animate.set_color(YELLOW),
            two.animate.set_color(YELLOW)
        )

        #Adding transition and explanation
        explanation = Tex("Adding 1 and 2").to_edge(UP)
        self.play(Write(explanation))

        #Animate the addition process
        self.play(
            Transform(equation[0],three),
            FadeOut(equation[1:]), #Removing plus and two
            run_time=1
        )


        #Show the result
        self.play(
            Write(equals),
            Write(three),
            three.animate.next_to(equals,RIGHT,buff=0.5),
        )
        self.wait(1)


        #Clean up
        self.play(FadeOut(explanation))
        self.wait(1)

