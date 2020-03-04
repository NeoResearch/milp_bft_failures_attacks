class Drawer(object):
	def __init__(self):
		pass

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
	def __init__(self):
		super().__init__()

	def __enter__(self) -> Drawer:
		print("\\begin{tikzpicture}[yscale=-1]")
		return self

	def __exit__(self, type, value, traceback) -> bool:
		if value:
			raise value
		print("\\end{tikzpicture}")
		return True

	def node(self, name: str, pos: (int, int), d_options: list = ['draw']):
		print(f"\\node{self.gen_options(d_options)} at ({pos[0]},{pos[1]}) {{{name}}};")

	def draw(self, command: str, pos: list, d_options: list, cmd_options: list, tail_options: list):
		tail_command = f' -- {self.gen_options(tail_options)}' if len(tail_options) > 0 else ''
		print(
			f"\\draw{self.gen_options(d_options)} ({pos[0][0]},{pos[0][1]}) {command}{self.gen_options(cmd_options)}"
			f"{f'({pos[1][0]},{pos[1][1]})' if len(pos) > 1 else ''}{tail_command};"
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
