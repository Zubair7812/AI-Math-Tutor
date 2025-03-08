# import os
# import subprocess
# from manim import *
# from elevenlabs import generate, set_api_key
# from moviepy.editor import VideoFileClip, AudioFileClip
# import streamlit as st

# # Set ElevenLabs API Key
# set_api_key("sk_c06689b5f6b3ea65094dba8f2fcf8ccebba44cf84b9939f4")

# # Function to generate Manim video
# def generate_manim_video(script_content, video_class_name="MathExplanation"):
#     # Write the script to a temporary file
    # script_path = f"{video_class_name}_manim.py"
    # with open(script_path, "w") as f:
    #     f.write(script_content)
    
    # # Run Manim to generate the video
    # subprocess.run(["manim", "-ql", script_path, video_class_name])
    
    # # Return the path to the generated video
    # return f"media/videos/{video_class_name}_manim/480p15/{video_class_name}.mp4"

# # Function to generate audio using ElevenLabs
# def generate_audio(text, audio_path="explanation_audio.mp3"):
#     audio_data = generate(text=text, voice="Sarah")  # Use a valid voice
#     with open(audio_path, "wb") as f:
#         f.write(audio_data)
#     return audio_path

# # Function to combine video and audio
# def combine_video_audio(video_path, audio_path, output_video="final_explanation.mp4"):
#     video = VideoFileClip(video_path)
#     audio = AudioFileClip(audio_path)
    
#     # Ensure audio duration matches the video
#     audio = audio.subclip(0, min(video.duration, audio.duration))
    
#     final_video = video.set_audio(audio)
#     final_video.write_videofile(output_video, codec="libx264")
#     return output_video

# # Function to generate the Manim script dynamically
# def create_manim_script(problem_text, explanation_text):
#     return f"""
# from manim import *

# class MathExplanation(Scene):
#     def construct(self):
#         title = Text("Mathematical Explanation", font_size=40)
#         self.play(Write(title))
#         self.wait(1)

#         problem = MathTex(r"{problem_text}", font_size=35)
#         problem.next_to(title, DOWN)
#         self.play(Write(problem))
#         self.wait(2)

#         step1 = MathTex(r"{explanation_text}", font_size=30)
#         step1.next_to(problem, DOWN)
#         self.play(Write(step1))
#         self.wait(2)
# """

# # Streamlit App Integration
# def execute_function(option):
#     if option == "Problem Solver":
#         problem = st.text_area("Enter your math problem:")
#         if st.button("Solve Step-by-Step"):
#             if problem:
#                 prompt = f"""Solve this {skill_level.lower()} level {topic.lower()} problem step by step, providing detailed explanations for each step."""
#                 response = model.generate_content(prompt + problem)
#                 render_math(response.text)
#                 update_progress(st.session_state.user, topic)
                
#                 # Generate video script dynamically
#                 problem_text = problem
#                 explanation_text = response.text  # Use the AI-generated explanation
#                 manim_script = create_manim_script(problem_text, explanation_text)
                
#                 # Generate video and audio
#                 if st.button("Generate Video Explanation"):
#                     with st.spinner("Generating video..."):
#                         try:
#                             # Generate Manim video
#                             video_path = generate_manim_video(manim_script)
                            
#                             # Generate audio
#                             audio_path = generate_audio(explanation_text)
                            
#                             # Combine video and audio
#                             final_video_path = combine_video_audio(video_path, audio_path)
                            
#                             # Display the video
#                             st.video(final_video_path)
#                             st.success("Video generated successfully!")
#                         except Exception as e:
#                             st.error(f"Error generating video: {e}")
#             else:
#                 st.warning("Please enter a math problem.")
from manim import *

class CylinderSphereProblem(Scene):
    def construct(self):
        #Scene 1: Introduce the cylinder
        cylinder = Cylinder(radius=5, height=12, fill_opacity=0.5, color=BLUE)
        cylinder_label = Text("Cylinder: r = 5 cm, h = 12 cm").next_to(cylinder, UP)
        self.play(DrawBorderThenFill(cylinder), Write(cylinder_label))
        self.wait()

        #Scene 2: Introduce the sphere
        sphere = Sphere(radius=3, fill_opacity=0.7, color=RED)
        sphere.next_to(cylinder, RIGHT, buff=1)
        sphere_label = Text("Sphere: r = 3 cm").next_to(sphere, UP)
        self.play(DrawBorderThenFill(sphere), Write(sphere_label))
        self.wait()

        #Scene 3: Show the sphere submerging
        sphere_final_pos = cylinder.get_center() + np.array([0,0,6]) #Place sphere at the bottom
        self.play(sphere.animate.move_to(sphere_final_pos))
        self.wait()


        #Scene 4: Calculate sphere volume
        sphere_volume_formula = MathTex("V_{sphere} = \frac{4}{3}\pi r^3").to_edge(UP)
        sphere_volume_calc = MathTex("V_{sphere} = \frac{4}{3}\pi (3^3) = 36\pi").next_to(sphere_volume_formula, DOWN)
        self.play(Write(sphere_volume_formula), Write(sphere_volume_calc))
        self.wait()


        #Scene 5: Calculate cylinder base area
        cylinder_base_area_formula = MathTex("A_{base} = \pi r^2").next_to(sphere_volume_calc, DOWN, buff=1)
        cylinder_base_area_calc = MathTex("A_{base} = \pi (5^2) = 25\pi").next_to(cylinder_base_area_formula, DOWN)
        self.play(Write(cylinder_base_area_formula), Write(cylinder_base_area_calc))
        self.wait()

        #Scene 6: Calculate water level rise
        water_level_rise_formula = MathTex("h_{rise} = \frac{V_{sphere}}{A_{base}} = \frac{36\pi}{25\pi}").next_to(cylinder_base_area_calc, DOWN, buff=1)
        water_level_rise_result = MathTex("h_{rise} = 1.44").next_to(water_level_rise_formula, DOWN)
        self.play(Write(water_level_rise_formula), Write(water_level_rise_result))
        self.wait()

        #Scene 7: Show visual representation of water level rise (optional but recommended)
        final_cylinder_height = 12 + 1.44
        final_cylinder = Cylinder(radius=5, height=final_cylinder_height, fill_opacity=0.5, color=BLUE)
        final_cylinder.move_to(cylinder)
        water_rise_highlight = Cylinder(radius=5, height=1.44, fill_opacity=0.8, color=GREEN)
        water_rise_highlight.move_to(final_cylinder.get_center()+ np.array([0,0,-6]))
        self.play(Transform(cylinder, final_cylinder), DrawBorderThenFill(water_rise_highlight))
        self.wait()

        #Scene 8: Final answer
        final_answer = Text("The water level rises by 1.44 cm").to_edge(DOWN)
        self.play(Write(final_answer))
        self.wait()