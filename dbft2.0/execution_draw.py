import sys
import random
from enum import Enum
from drawer import TikzDrawer


class ArrowMessageType(Enum):
    PrepReq = 1
    PrepRes = 2
    Commit = 3
    CV = 4


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

    def is_loop(self):
        return self.node == self.destination and self.start_time == self.end_time


class PackMessage(object):
    def __init__(self, arrow_message_type: ArrowMessageType, t: int, node: int, view: int):
        self.arrow_message_type = arrow_message_type
        self.node = node
        self.view = view
        self.t = t
        self.__destinations = {}

    def add_destination(self, destination: int, t: int):
        self.__destinations[destination] = t

    def arrows(self):
        for to, time_deliver in self.__destinations.items():
            yield ArrowMessage(self.arrow_message_type, self.t, self.node, self.view, time_deliver, to)


class BlockRelay(object):
    def __init__(self, t, node, view):
        self.time = t
        self.node = node
        self.view = view


class View(object):
    def __init__(self, number, primary):
        self.number = number
        self.primary = primary
        self.packs = {}
        self.block_relay = []


def is_selected(the_var: object):
    return the_var.x >= 0.999


class ExecutionDraw(object):
    def __init__(
            self, view_size: int, n: int, f: int, m: int,
            send_prep_req: dict, send_prep_res: dict, send_commit: dict, send_cv: dict,
            recv_prep_req: dict, recv_prep_res: dict, recv_commit: dict, recv_cv: dict,
            primary: dict, block_relays: dict
    ):
        self.view_size = view_size
        self.n = n
        self.f = f
        self.m = m
        self.views = {}

        for it, variable in primary.items():
            if is_selected(variable):
                node, view = it
                self.views[view] = View(view, node)

        for it, variable in block_relays.items():
            if is_selected(variable):
                t, node, view = it
                self.views[view].block_relay.append(BlockRelay(t, node, view))

        def add_send_msg(view: dict, view_size: int, message_type: ArrowMessageType, values: dict):
            for it, variable in values.items():
                if is_selected(variable):
                    t, i, v = it
                    the_view = view[v]
                    arrow_message = the_view.packs.get(
                        (message_type, i), PackMessage(message_type, t + (v - 1) * view_size, i, v)
                    )

                    the_view.packs[(message_type, i)] = arrow_message
                    view[v] = the_view

        def add_recv_msg(view: dict, view_size: int, message_type: ArrowMessageType, values: dict):
            for it, variable in values.items():
                if is_selected(variable):
                    t, i, j, v = it
                    if v not in view:
                        raise Exception(f"View {v} not found")

                    the_view = view[v].packs
                    if (message_type, j) not in the_view:
                        raise Exception(f"{(message_type, j)} not in view {v}")

                    arrow_message = the_view[(message_type, j)]
                    arrow_message.add_destination(i, t + (v - 1) * view_size)

        add_send_msg(self.views, view_size, ArrowMessageType.PrepReq, send_prep_req)
        add_send_msg(self.views, view_size, ArrowMessageType.PrepRes, send_prep_res)
        add_send_msg(self.views, view_size, ArrowMessageType.Commit, send_commit)
        add_send_msg(self.views, view_size, ArrowMessageType.CV, send_cv)

        add_recv_msg(self.views, view_size, ArrowMessageType.PrepReq, recv_prep_req)
        add_recv_msg(self.views, view_size, ArrowMessageType.PrepRes, recv_prep_res)
        add_recv_msg(self.views, view_size, ArrowMessageType.Commit, recv_commit)
        add_recv_msg(self.views, view_size, ArrowMessageType.CV, recv_cv)

    def draw_tikzpicture(
            self, view_title: bool = True, subtitle: bool = True, first_block: int = 1, rand_pos: bool = False,
            primary_ignore_messages=set([ArrowMessageType.PrepRes]), ignore_messages=set([]), out=sys.stdout,
    ):
        random.seed(0)
        send_receive_variables_options = {
            ArrowMessageType.PrepReq: ['thick', '->', 'color=blue'],
            ArrowMessageType.PrepRes: ['thick', '->', 'color=green'],
            ArrowMessageType.Commit: ['thick', '->', 'color=yellow'],
            ArrowMessageType.CV: ['thick', '->', 'color=red,dashed'],
        }
        with TikzDrawer(out) as my_drawer:
            if view_title:
                for view in range(len(self.views)):
                    my_drawer.node(f"View {view}", (self.view_size / 2 + view * self.view_size, 0))

            for node in range(1, self.n + 1):
                my_drawer.node(f"{node}", (0, node))
                my_drawer.line((1, node), (len(self.views) * self.view_size, node), ["thick", "dashed"])

            block_num = first_block

            for view_num in sorted(self.views.keys()):
                view = self.views[view_num]
                my_drawer.node(f"$Pr.^{view.primary}$", ((view.number - 1) * self.view_size + 1.5, view.primary + 0.5))

                inc_block = False
                for relay in view.block_relay:
                    inc_block = True
                    my_drawer.node(
                        f"relay #{block_num}",
                        ((relay.view - 1) * self.view_size + relay.time, relay.node + 0.5),
                        []
                    )
                if inc_block:
                    block_num += 1

                for _, arrow in view.packs.items():
                    for arrow in arrow.arrows():
                        if (not arrow.is_loop() and arrow.arrow_message_type not in ignore_messages) \
                                and not (arrow.node == self.views[arrow.view].primary and
                                        arrow.arrow_message_type in primary_ignore_messages):
                            first_val = random.uniform(-.1, .1) if rand_pos else 0
                            second_val = random.uniform(-.1, .1) if rand_pos else 0
                            my_drawer.line(
                                (arrow.start_time, arrow.node),
                                (arrow.end_time + first_val, arrow.destination + second_val),
                                send_receive_variables_options[arrow.arrow_message_type]
                            )

            if subtitle:
                it = 2
                for arrow_type, arrow_opt in send_receive_variables_options.items():
                    if arrow_type not in ignore_messages:
                        my_drawer.line((0, self.n + it), (.5, self.n + it), arrow_opt)
                        my_drawer.node(f"{arrow_type.name}", (1.5, self.n + it))
                        it += 1
