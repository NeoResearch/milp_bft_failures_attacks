import sys


class Drawer(object):
    def __init__(self, out=sys.stdout, generate_full_latex: bool = True, border: str = "5pt"):
        self.out = out
        self.generate_full_latex = generate_full_latex
        self.border = border

    def __enter__(self) -> object:
        return self

    def __exit__(self, type, value, traceback) -> bool:
        return True

    def node(self, name: str, pos: (int, int), options: list = []):
        pass

    def arc(self, pos: (int, int), d_options: list = [], cmd_options: list = []):
        pass

    def circle(self, pos: (int, int), d_options: list = [], cmd_options: list = []):
        pass

    def ellipse(self, pos: (int, int), d_options: list = [], cmd_options: list = []):
        pass

    def grid(self, line_from: (int, int), line_to: (int, int), d_options: list = []):
        pass

    def line(self, line_from: (int, int), line_to: (int, int), d_options: list = []):
        pass

    def line_hv(self, line_from: (int, int), line_to: (int, int), d_options: list = []):
        pass

    def line_vh(self, line_from: (int, int), line_to: (int, int), d_options: list = []):
        pass

    def rectangle(self, line_from: (int, int), line_to: (int, int), d_options: list = []):
        pass

    def escape(self, text: str) -> str:
        return text

    def gen_options(self, options: list):
        return options


class TikzDrawer(Drawer):
    def __init__(self, out=sys.stdout):
        super().__init__(out)

    def __enter__(self) -> Drawer:
        if self.generate_full_latex:
            self.out.write(f"\\documentclass[tikz,border={self.border}]{{standalone}}\n")
            self.out.write("\\usetikzlibrary{backgrounds}\n")
            self.out.write("\\begin{document}\n")
        self.out.write("\\begin{tikzpicture}[yscale=-1]\n")
        return self

    def __exit__(self, type, value, traceback) -> bool:
        if value:
            raise value
        self.out.write("\\end{tikzpicture}\n")
        if self.generate_full_latex:
            self.out.write("\\end{document}\n")

        return True

    def node(self, name: str, pos: (int, int), d_options: list = ['draw']):
        self.out.write(f"\\node{self.gen_options(d_options)} at ({pos[0]},{pos[1]}) {{{name}}};\n")

    def draw(self, command: str, pos: list, d_options: list, cmd_options: list, tail_options: list):
        tail_command = f' -- {self.gen_options(tail_options)}' if len(tail_options) > 0 else ''
        self.out.write(
            f"\\draw{self.gen_options(d_options)} ({pos[0][0]},{pos[0][1]}) {command}{self.gen_options(cmd_options)}"
            f"{f'({pos[1][0]},{pos[1][1]})' if len(pos) > 1 else ''}{tail_command};\n"
        )

    def arc(self, pos: (int, int), d_options: list = [], cmd_options: list = []):
        self.draw('arc', [pos], d_options, cmd_options, [])

    def circle(self, pos: (int, int), d_options: list = [], cmd_options: list = []):
        self.draw('circle', [pos], d_options, cmd_options, [])

    def ellipse(self, pos: (int, int), d_options: list = [], cmd_options: list = []):
        self.draw('ellipse', [pos], d_options, cmd_options, [])

    def grid(self, line_from: (int, int), line_to: (int, int), d_options: list = []):
        self.draw('grid', [line_from] + [line_to], d_options, [], [])

    def line(self, line_from: (int, int), line_to: (int, int), d_options: list = []):
        self.draw('--', [line_from] + [line_to], d_options, [], [])

    def line_hv(self, line_from: (int, int), line_to: (int, int), d_options: list = []):
        self.draw('-|', [line_from] + [line_to], d_options, [], [])

    def line_vh(self, line_from: (int, int), line_to: (int, int), d_options: list = []):
        self.draw('|-', [line_from] + [line_to], d_options, [], [])

    def rectangle(self, line_from: (int, int), line_to: (int, int), d_options: list = []):
        self.draw('rectangle', [line_from] + [line_to], d_options, [], [])

    def escape(self, text: str) -> str:
        return text.replace(' ', '\\; ').replace('#', '\\#')

    def gen_options(self, options: list):
        return f"[{','.join(options)}]" if len(options) > 0 else ''
