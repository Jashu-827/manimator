from manim import *

class TriangleProperties(Scene):
    def construct(self):
        # Title
        title = Text("Triangle Properties", font_size=48).to_edge(UP)
        self.play(Write(title))
        self.wait(1)
        
        # Create a triangle
        triangle = Polygon(
            [-3, -1, 0],  # A
            [3, -1, 0],   # B
            [0, 2, 0],    # C
            color=BLUE
        )
        triangle.shift(DOWN*0.5)
        
        # Vertices labels
        vertex_a = Tex("A", color=YELLOW).next_to(triangle.get_vertices()[0], DOWN+LEFT)
        vertex_b = Tex("B", color=YELLOW).next_to(triangle.get_vertices()[1], DOWN+RIGHT)
        vertex_c = Tex("C", color=YELLOW).next_to(triangle.get_vertices()[2], UP)
        
        # Create triangle with vertices
        self.play(Create(triangle))
        self.play(Write(vertex_a), Write(vertex_b), Write(vertex_c))
        self.wait(2)
        
        # Explanation text 1
        explanation1 = Text(
            "A triangle has 3 sides and 3 angles", 
            font_size=24
        ).to_edge(DOWN).scale_to_fit_width(config.frame_width * 0.8)
        self.play(Write(explanation1))
        self.wait(2)
        
        # Highlight sides
        side_ab = Line(triangle.get_vertices()[0], triangle.get_vertices()[1], color=RED, stroke_width=6)
        side_bc = Line(triangle.get_vertices()[1], triangle.get_vertices()[2], color=GREEN, stroke_width=6)
        side_ca = Line(triangle.get_vertices()[2], triangle.get_vertices()[0], color=ORANGE, stroke_width=6)
        
        side_label_ab = MathTex("a", color=RED).next_to(side_ab, DOWN, buff=0.2)
        side_label_bc = MathTex("b", color=GREEN).next_to(side_bc, RIGHT, buff=0.2)
        side_label_ca = MathTex("c", color=ORANGE).next_to(side_ca, LEFT, buff=0.2)
        
        self.play(Create(side_ab), Write(side_label_ab))
        self.wait(1)
        self.play(Create(side_bc), Write(side_label_bc))
        self.wait(1)
        self.play(Create(side_ca), Write(side_label_ca))
        self.wait(2)
        
        # Explanation text 2
        self.play(FadeOut(explanation1))
        explanation2 = Text(
            "The sum of interior angles equals 180°", 
            font_size=24
        ).to_edge(DOWN).scale_to_fit_width(config.frame_width * 0.8)
        self.play(Write(explanation2))
        self.wait(2)
        
        # Show angles
        angle_a = Angle(side_ab, side_ca, radius=0.5, other_angle=True, color=YELLOW)
        angle_b = Angle(side_ca, side_bc, radius=0.5, other_angle=True, color=YELLOW)
        angle_c = Angle(side_bc, side_ab, radius=0.5, other_angle=True, color=YELLOW)
        
        angle_label_a = MathTex(r"\alpha", color=YELLOW).next_to(angle_a, DOWN, buff=0.3)
        angle_label_b = MathTex(r"\beta", color=YELLOW).next_to(angle_b, RIGHT, buff=0.3)
        angle_label_c = MathTex(r"\gamma", color=YELLOW).next_to(angle_c, LEFT, buff=0.3)
        
        angle_formula = MathTex(r"\alpha + \beta + \gamma = 180^\circ", color=YELLOW, font_size=36)
        angle_formula.to_edge(DOWN).shift(UP*0.5).scale_to_fit_width(config.frame_width * 0.8)
        
        self.play(Create(angle_a), Write(angle_label_a))
        self.wait(1)
        self.play(Create(angle_b), Write(angle_label_b))
        self.wait(1)
        self.play(Create(angle_c), Write(angle_label_c))
        self.wait(2)
        
        # Show angle sum formula
        self.play(FadeOut(explanation2))
        self.play(Write(angle_formula))
        self.wait(3)
        
        # Explanation text 3
        self.play(FadeOut(angle_formula))
        explanation3 = Text(
            "Triangle inequality: Sum of any two sides > third side", 
            font_size=24
        ).to_edge(DOWN).scale_to_fit_width(config.frame_width * 0.8)
        self.play(Write(explanation3))
        self.wait(2)
        
        # Show triangle inequality
        inequality = MathTex(
            r"a + b > c \\",
            r"b + c > a \\",
            r"a + c > b",
            font_size=36
        )
        inequality.to_edge(DOWN).shift(UP*0.7).scale_to_fit_width(config.frame_width * 0.8)
        
        self.play(Write(inequality))
        self.wait(3)
        
        # Explanation text 4
        self.play(FadeOut(explanation3), FadeOut(inequality))
        explanation4 = Text(
            "Area = ½ × base × height", 
            font_size=24
        ).to_edge(DOWN).scale_to_fit_width(config.frame_width * 0.8)
        self.play(Write(explanation4))
        self.wait(2)
        
        # Show height
        base_line = side_ab.copy().set_color(WHITE)
        height_line = DashedLine(
            triangle.get_vertices()[2],  # C
            [0, -1, 0],  # Foot of height
            color=PURPLE
        )
        height_brace = Brace(height_line, RIGHT, color=PURPLE)
        height_label = MathTex("h", color=PURPLE).next_to(height_brace, RIGHT, buff=0.1)
        
        area_formula = MathTex(r"\text{Area} = \frac{1}{2} \times \text{base} \times h", color=PURPLE, font_size=36)
        area_formula.to_edge(DOWN).shift(UP*0.5).scale_to_fit_width(config.frame_width * 0.8)
        
        self.play(Create(height_line), Create(height_brace), Write(height_label))
        self.wait(2)
        self.play(Write(area_formula))
        self.wait(3)
        
        # Final conclusion
        self.play(FadeOut(explanation4), FadeOut(area_formula))
        conclusion = Text(
            "These properties apply to all triangles regardless of type!", 
            font_size=24
        ).to_edge(DOWN).scale_to_fit_width(config.frame_width * 0.8)
        self.play(Write(conclusion))
        self.wait(3)
        
        # Final animation - rotate triangle
        self.play(Rotate(triangle, angle=PI, axis=OUT), run_time=2)
        self.wait(2)
        
        self.play(FadeOut(title), FadeOut(triangle), FadeOut(vertex_a), FadeOut(vertex_b), 
                  FadeOut(vertex_c), FadeOut(side_label_ab), FadeOut(side_label_bc), 
                  FadeOut(side_label_ca), FadeOut(angle_label_a), FadeOut(angle_label_b), 
                  FadeOut(angle_label_c), FadeOut(height_label), FadeOut(height_brace),
                  FadeOut(base_line), FadeOut(height_line), FadeOut(conclusion),
                  FadeOut(angle_a), FadeOut(angle_b), FadeOut(angle_c),
                  FadeOut(side_ab), FadeOut(side_bc), FadeOut(side_ca))
        self.wait(1)