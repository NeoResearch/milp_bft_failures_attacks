import sys
import random
import subprocess
import os
import pickle
from enum import Enum
from typing import Dict, List, Iterable, NoReturn, Tuple, Optional, Set, TextIO

from dbft_draw.drawer import TikzDrawer


class ArrowMessageType(Enum):
    PrepReq = 1
    PrepRes = 2
    PreCommit = 3
    Commit = 4
    CV = 5

    def has_priority(self):
        return self != ArrowMessageType.CV


class ArrowMessage(object):
    def __init__(
            self, arrow_message_type: ArrowMessageType, t: int, node: int, view: int,
            t_destination: int, destination: int
    ):
        self.arrow_message_type = arrow_message_type
        self.node = node
        self.view = view
        self.start_time = t
        self.end_time = t_destination
        self.destination = destination

    def __str__(self):
        return f"{self.arrow_message_type.name}({self.start_time}, {self.node}, " \
               f"{self.end_time}, {self.destination}, {self.view})"

    def is_loop(self) -> bool:
        return self.node == self.destination and self.start_time == self.end_time


class PackMessage(object):
    def __init__(self, arrow_message_type: ArrowMessageType, t: int, node: int, view: int):
        self.arrow_message_type = arrow_message_type
        self.node = node
        self.view = view
        self.t = t
        self.__destinations: Dict[int, int] = {}

    def add_destination(self, destination: int, t: int) -> NoReturn:
        self.__destinations[destination] = t

    def arrows(self) -> Iterable[ArrowMessage]:
        for to, time_deliver in self.__destinations.items():
            yield ArrowMessage(
                arrow_message_type=self.arrow_message_type, t=self.t, node=self.node, view=self.view,
                t_destination=time_deliver, destination=to,
            )


class BlockRelay(object):
    def __init__(self, t: int, node: int, view: int):
        self.time = t
        self.node = node
        self.view = view


class View(object):
    def __init__(self, number: int, primary: Optional[int]):
        self.number = number
        self.primary = primary
        self.packs: Dict[Tuple[ArrowMessageType, int], PackMessage] = {}
        self.block_relay: List[BlockRelay] = []


def is_selected(the_var: object) -> bool:
    return the_var.x >= 0.999


class ExecutionDraw(object):
    def __init__(
            self, view_size: int, n: int, f: int, m: int,
            send_prep_req: dict, send_prep_res: dict, send_pre_commit: dict, send_commit: dict, send_cv: dict,
            recv_prep_req: dict, recv_prep_res: dict, recv_pre_commit: dict, recv_commit: dict, recv_cv: dict,
            primary: dict, block_relays: dict, multiple_primary: bool = False,
    ):
        self.view_size = view_size
        self.n = n
        self.f = f
        self.m = m
        self.view_arrows: Dict[int, Dict[int, View]] = {}
        self.priorities: Set[int] = set()

        for it, variable in primary.items():
            if is_selected(variable):
                if multiple_primary:
                    p, node, view = it
                else:
                    node, view = it
                    p = 1
                self.priorities.add(p)
                self.view_arrows[view] = self.view_arrows.get(view, {})
                self.view_arrows[view][p] = View(view, node)

        for it, variable in block_relays.items():
            if is_selected(variable):
                if multiple_primary:
                    p, t, node, view = it
                else:
                    t, node, view = it
                    p = 1
                self.priorities.add(p)
                self.view_arrows[view][p] = self.view_arrows[view].get(p, {})
                self.view_arrows[view][p].block_relay.append(BlockRelay(t, node, view))

        def get_or_create_view(view: Dict[int, Dict[int, View]], number: int, p: int = 1) -> View:
            the_view = view.get(number, {})
            view[number] = the_view
            the_view = the_view.get(p, View(number, None))
            view[number][p] = the_view
            if not the_view:
                print(f"The view {the_view.number} has no primary")
            return the_view

        def add_send_msg_cv(
                view: Dict[int, Dict[int, View]], view_size: int, message_type: ArrowMessageType, values: dict
        ) -> NoReturn:
            for it, variable in values.items():
                if is_selected(variable):
                    t, i, v = it
                    p = 1
                    the_view = get_or_create_view(view, v, p)
                    arrow_message = the_view.packs.get(
                        (message_type, i), PackMessage(message_type, t + (v - 1) * view_size, i, v)
                    )

                    the_view.packs[(message_type, i)] = arrow_message
                    # view[v] = the_view
                    # arrow_message.priorities.add(p)

        def add_recv_msg_cv(
                view: Dict[int, Dict[int, View]], view_size: int, message_type: ArrowMessageType, values: dict
        ) -> NoReturn:
            for it, variable in values.items():
                if is_selected(variable):
                    t, i, j, v = it
                    p = 1
                    if v not in view:
                        raise Exception(f"View {v} not found")

                    the_view = get_or_create_view(view, v, p).packs
                    if (message_type, j) not in the_view:
                        raise Exception(f"{(message_type, j)} not in view {v}")

                    arrow_message = the_view[(message_type, j)]
                    arrow_message.add_destination(i, t + (v - 1) * view_size)
                    # arrow_message.priorities.add(p)

        def add_send_msg(view: dict, view_size: int, message_type: ArrowMessageType, values: dict) -> NoReturn:
            for it, variable in values.items():
                if is_selected(variable):
                    if multiple_primary:
                        p, t, i, v = it
                    else:
                        t, i, v = it
                        p = 1
                    the_view = get_or_create_view(view, v, p)
                    arrow_message = the_view.packs.get(
                        (message_type, i), PackMessage(message_type, t + (v - 1) * view_size, i, v)
                    )
                    # arrow_message.priorities.add(p)

                    the_view.packs[(message_type, i)] = arrow_message
                    # view[p] = the_view

        def add_recv_msg(view: dict, view_size: int, message_type: ArrowMessageType, values: dict) -> NoReturn:
            for it, variable in values.items():
                if is_selected(variable):
                    if multiple_primary:
                        p, t, i, j, v = it
                    else:
                        t, i, j, v = it
                        p = 1

                    if v not in view:
                        raise Exception(f"View {v} not found")

                    the_view = get_or_create_view(view, v, p).packs
                    if (message_type, j) not in the_view:
                        raise Exception(f"{(message_type, j)} not in view {v}")

                    arrow_message = the_view[(message_type, j)]
                    # arrow_message.priorities.add(p)
                    arrow_message.add_destination(i, t + (v - 1) * view_size)

        add_send_msg(self.view_arrows, view_size, ArrowMessageType.PrepReq, send_prep_req)
        add_send_msg(self.view_arrows, view_size, ArrowMessageType.PrepRes, send_prep_res)
        if multiple_primary:
            add_send_msg(self.view_arrows, view_size, ArrowMessageType.PreCommit, send_pre_commit)
        add_send_msg(self.view_arrows, view_size, ArrowMessageType.Commit, send_commit)
        add_send_msg_cv(self.view_arrows, view_size, ArrowMessageType.CV, send_cv)

        add_recv_msg(self.view_arrows, view_size, ArrowMessageType.PrepReq, recv_prep_req)
        add_recv_msg(self.view_arrows, view_size, ArrowMessageType.PrepRes, recv_prep_res)
        if multiple_primary:
            add_recv_msg(self.view_arrows, view_size, ArrowMessageType.PreCommit, recv_pre_commit)
        add_recv_msg(self.view_arrows, view_size, ArrowMessageType.Commit, recv_commit)
        add_recv_msg_cv(self.view_arrows, view_size, ArrowMessageType.CV, recv_cv)

    def dump(self, file_name: str):
        with open(file_name, 'wb') as the_file:
            pickle.dump(self.__dict__, the_file)

    @staticmethod
    def from_file(file_name: str):
        value = ExecutionDraw(
            view_size=0, n=0, f=0, m=0,
            send_prep_req={}, send_prep_res={}, send_pre_commit={}, send_commit={}, send_cv={},
            recv_prep_req={}, recv_prep_res={}, recv_pre_commit={}, recv_commit={}, recv_cv={},
            primary={}, block_relays={},
        )
        with open(file_name, 'rb') as the_file:
            value.__dict__ = pickle.load(the_file)
        return value

    def draw_tikzpicture(
            self, view_title: bool = True, subtitle: bool = True, first_block: int = 1, rand_pos: bool = False,
            primary_ignore_messages: Set[ArrowMessageType] = set([ArrowMessageType.PrepRes]),
            ignore_messages: Set[ArrowMessageType] = set(),
            generate_full_latex: bool = True, circle_all_send: bool = False, circle_radius: float = .08,
            out: TextIO = sys.stdout, priority: int = 1, node_start_with_zero: bool = False, show_ruler: bool = True,
            view_start_with_zero: bool = True,
    ):
        random.seed(0)
        send_receive_variables_options = {
            ArrowMessageType.PrepReq: ['thick', '->', 'color=blue'],
            ArrowMessageType.PrepRes: ['thick', '->', 'color=green'],
            ArrowMessageType.PreCommit: ['thick', '->', 'color=brown'],
            ArrowMessageType.Commit: ['thick', '->', 'color=yellow'],
            ArrowMessageType.CV: ['thick', '->', 'dashed', 'color=red'],
        }

        with TikzDrawer(out, generate_full_latex) as my_drawer:
            self.draw_title_and_lines(my_drawer, view_title, view_start_with_zero)

            line_size = len(self.view_arrows) * self.view_size
            for node in range(1, self.n + 1):
                # Converting to start at zero
                my_drawer.node(f"{node - (1 if node_start_with_zero else 0)}", (0, node))
                my_drawer.line((1, node), (line_size, node), ["thick", "dashed"])

            # Drawing ruler
            if show_ruler:
                # my_drawer.line((1, 0.58), (line_size, 0.58), ["ultra thin", "dashed"])
                # my_drawer.line((1, self.n + 0.87), (line_size, self.n + 0.87), ["ultra thin", "dashed"])

                for it in range(1, line_size + 1):
                    if it % 5 == 0:
                        my_drawer.node(f"\\tiny {it}", (it, 0.58), [])
                        my_drawer.node(f"\\tiny {it}", (it, self.n + 0.85), [])
                    else:
                        my_drawer.line((it, 0.51), (it, 0.65), ["thin"])
                        my_drawer.line((it, self.n + 0.95), (it, self.n + 0.81), ["thin"])

            block_num = first_block

            circles = {}

            def add_circle(circle_pos, config=[]):
                circle_radius_val = circle_radius + .03 * circles.get(circle_pos, 0)
                my_drawer.circle(
                    circle_pos,
                    config + [f"radius={circle_radius_val}"]
                )
                circles[circle_pos] = circles.get(circle_pos, 0) + 1

            for view_num in sorted(self.view_arrows.keys()):
                if priority not in self.view_arrows[view_num]:
                    # Can we have a view that does not have all the priorities?
                    continue
                view = self.view_arrows[view_num][priority]
                if view.primary:
                    # Converting to start at zero
                    my_drawer.node(
                        f"$Pr.^{view.primary - (1 if node_start_with_zero else 0)}$",
                        ((view.number - 1) * self.view_size + 1.5, view.primary + 0.5)
                    )

                if self.draw_block_relay(add_circle, block_num, my_drawer, view):
                    block_num += 1

                for _, pack in view.packs.items():
                    p = priority
                    if not pack.arrow_message_type.has_priority():
                        # In case of a CV message all the drawings should have the arrow
                        p = 1

                    draw_circle = set()
                    for arrow in pack.arrows():
                        draw_circle.add(arrow.destination)
                        self.draw_arrow(
                            arrow, ignore_messages, my_drawer, primary_ignore_messages, p, rand_pos,
                            send_receive_variables_options
                        )

                    if pack.view in self.view_arrows:
                        if circle_all_send or (len(draw_circle) == 1 and pack.node in draw_circle):
                            add_circle(
                                (pack.t, pack.node),
                                [send_receive_variables_options[pack.arrow_message_type][-1]]
                            )

            self.draw_subtitle(ignore_messages, my_drawer, send_receive_variables_options, subtitle, priority)

    def draw_block_relay(self, add_circle, block_num, my_drawer, view):
        inc_block = False
        for relay in view.block_relay:
            inc_block = True
            my_drawer.node(
                f"relay \\#{block_num}",
                ((relay.view - 1) * self.view_size + relay.time, relay.node + 0.5),
                []
            )
            add_circle(((relay.view - 1) * self.view_size + relay.time, relay.node))
        return inc_block

    def draw_arrow(self, arrow, ignore_messages, my_drawer, primary_ignore_messages, priority, rand_pos,
                   send_receive_variables_options):
        if (not arrow.is_loop() and arrow.arrow_message_type not in ignore_messages) \
                and not (arrow.node == self.view_arrows[arrow.view][priority].primary and
                         arrow.arrow_message_type in primary_ignore_messages):
            first_val = random.uniform(-.1, .1) if rand_pos else 0
            second_val = random.uniform(-.1, .1) if rand_pos else 0
            my_drawer.line(
                (arrow.start_time, arrow.node),
                (arrow.end_time + first_val, arrow.destination + second_val),
                send_receive_variables_options[arrow.arrow_message_type]
            )

    def draw_subtitle(self, ignore_messages, my_drawer, send_receive_variables_options, subtitle, priority):
        if subtitle:
            it = 2
            for arrow_type, arrow_opt in send_receive_variables_options.items():
                if arrow_type not in ignore_messages:
                    my_drawer.line((0, self.n + it), (.5, self.n + it), arrow_opt)
                    my_drawer.node(f"{arrow_type.name}", (1.5, self.n + it), [])
                    it += 1
            my_drawer.node(f"Priority {priority}", (4, self.n + 2), [])

    def draw_title_and_lines(self, my_drawer, view_title, view_start_with_zero: bool):
        for view in range(len(self.view_arrows)):
            if view_title:
                view_delta = (1 if not view_start_with_zero else 0)
                my_drawer.node(f"View {view + view_delta}", (self.view_size / 2 + view * self.view_size, 0))
            if view > 0:
                my_drawer.line(
                    (view * self.view_size, 0), (view * self.view_size, self.n + 1),
                    ["thick", "-", "color=lightgray", "dashed"]
                )


def generate_pdf_file(drawing_file_name: str, remove_logs: bool = True):
    pdflatex_call = ["pdflatex", "-interaction", "nonstopmode"]
    try:
        with subprocess.Popen(
                pdflatex_call + [f"{drawing_file_name}.tex"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
        ) as proc:
            proc.wait()
            if proc.returncode == 0:
                if remove_logs:
                    os.remove(f"./{drawing_file_name}.aux")
                    os.remove(f"./{drawing_file_name}.log")
                return True
            else:
                print(f"There was a problem processing the file {drawing_file_name}.tex")
                stdout = proc.stdout.read()
                if stdout:
                    print("Standard output")
                    stdout = stdout.decode()
                    print(stdout)
                    if "LaTeX Error: File `standalone.cls' not found" in stdout:
                        print("You are missing the 'standalone' package.")
                        print(
                            "You may need to install 'texlive-latex-extra' with "
                            "'sudo apt-get install texlive-latex-extra'"
                        )
                stderr = proc.stderr.read()
                if stderr:
                    print("Standard error output")
                    stderr = stderr.decode()
                    print(stderr)
    except FileNotFoundError as fnf:
        if 'pdflatex' in f"{fnf}":
            print("You are missing the 'latex' package.")
            print(
                "You may need to install 'latex' with "
                "'sudo apt-get install texlive-latex-base texlive-latex-extra'"
            )
    return False
