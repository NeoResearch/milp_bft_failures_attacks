from enum import Enum
from drawer import TikzDrawer


class ArrowMessageType(Enum):
    PrepReq = 1
    PrepRes = 2
    Commit = 3
    CV = 4


class ArrowMessage(object):
    def __init__(self, arrow_message_type: ArrowMessageType, t: int, node: int, view: int):
        self.arrow_message_type = arrow_message_type
        self.node = node
        self.view = view
        self.t = t
        self.destinations = {}

    def add_destination(self, destination: int, t: int):
        self.destinations[destination] = t


def is_selected(the_var: object):
    return the_var.x >= 0.999


class ExecutionDraw(object):
    def __init__(
            self, view_size: int, n: int, f: int, m: int,
            send_prep_req: dict, send_prep_res: dict, send_commit: dict, send_cv: dict,
            recv_prep_req: dict, recv_prep_res: dict, recv_commit: dict, recv_cv: dict
    ):
        self.view_size = view_size
        self.n = n
        self.f = f
        self.m = m
        self.view = {}

        def add_send_msg(view: dict, view_size: int, message_type: ArrowMessageType, values: dict):
            for it, variable in values.items():
                if is_selected(variable):
                    t, i, v = it
                    the_view = view.get(v, {})
                    arrow_message = the_view.get(
                        (message_type, i), ArrowMessage(message_type, t + (v - 1) * view_size, i, v)
                    )

                    the_view[(message_type, i)] = arrow_message
                    view[v] = the_view

        def add_recv_msg(view: dict, view_size: int, message_type: ArrowMessageType, values: dict):
            for it, variable in values.items():
                if is_selected(variable):
                    t, i, j, v = it
                    if v not in view:
                        raise Exception(f"View {v} not found")

                    the_view = view[v]
                    if (message_type, j) not in the_view:
                        raise Exception(f"{(message_type, j)} not in view {v}")

                    arrow_message = the_view[(message_type, j)]
                    arrow_message.add_destination(i, t + (v - 1) * view_size)

        add_send_msg(self.view, view_size, ArrowMessageType.PrepReq, send_prep_req)
        add_send_msg(self.view, view_size, ArrowMessageType.PrepRes, send_prep_res)
        add_send_msg(self.view, view_size, ArrowMessageType.Commit, send_commit)
        add_send_msg(self.view, view_size, ArrowMessageType.CV, send_cv)

        add_recv_msg(self.view, view_size, ArrowMessageType.PrepReq, recv_prep_req)
        add_recv_msg(self.view, view_size, ArrowMessageType.PrepRes, recv_prep_res)
        add_recv_msg(self.view, view_size, ArrowMessageType.Commit, recv_commit)
        add_recv_msg(self.view, view_size, ArrowMessageType.CV, recv_cv)

    def draw_tikzpicture(self):
        send_receive_variables_options = {
            ArrowMessageType.PrepReq: ['thick', '->', 'color=blue'],
            ArrowMessageType.PrepRes: ['thick', '->', 'color=green'],
            ArrowMessageType.Commit: ['thick', '->', 'color=yellow'],
            ArrowMessageType.CV: ['thick', '->', 'color=cyan'],
        }
        with TikzDrawer() as my_drawer:
            for node in range(1, self.n + 1):
                my_drawer.line((1, node), (len(self.view) * self.view_size, node), ["thick", "dashed"])

            for view_num, the_view in self.view.items():
                for _, arrow in the_view.items():
                    for arrow_to, arrow_time in arrow.destinations.items():
                        my_drawer.line(
                            (arrow.t, arrow.node), (arrow_time, arrow_to),
                            send_receive_variables_options[arrow.arrow_message_type]
                        )
