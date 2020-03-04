from lxml import objectify
from drawer import TikzDrawer
import re

if __name__ == '__main__':
	file_name = 'example/simple.sol'
	file_name = 'example/soln4.sol'
	verbose = True
	sol = None
	with open(file_name) as file:
		file_content = file.read().encode('utf-8')
		sol = objectify.fromstring(file_content)

		primary = 'primary'
		prep_req = 'PrepReq'
		prep_resp = 'PrepResp'
		cv = 'CV'
		send_prep_req = 'SendPrepReq'
		send_prep_resp = 'SendPrepResp'
		send_cv = 'SendCV'
		recv_prep_req = 'RecvPrepReq'
		recv_prep_resp = 'RecvPrepResp'
		recv_cv = 'RecvCV'
		block_relay = 'BlockRelay'
		send_receive_variables = {
			send_prep_req, recv_prep_req,
			send_prep_resp, recv_prep_resp,
			send_cv, recv_cv,
		}
		send_receive_variables_options = {
			prep_req: ['thick', '->', 'color=blue'],
			prep_resp: ['thick', '->', 'color=green'],
			cv: ['thick', '->', 'color=cyan'],
		}

		patterns = {
			primary: (re.compile(r"primary\((\d+),(\d+)\)"), 2, False),
			send_prep_req: (re.compile(r"SendPrepReq\((\d+),(\d+),(\d+)\)"), 3, True),
			send_prep_resp: (re.compile(r"SendPrepResp\((\d+),(\d+),(\d+)\)"), 3, True),
			send_cv: (re.compile(r"SendCV\((\d+),(\d+),(\d+)\)"), 3, True),
			recv_prep_req: (re.compile(r"RecvPrepReq\((\d+),(\d+),(\d+),(\d+)\)"), 4, True),
			recv_prep_resp: (re.compile(r"RecvPrepResp\((\d+),(\d+),(\d+),(\d+)\)"), 4, True),
			recv_cv: (re.compile(r"RecvCV\((\d+),(\d+),(\d+),(\d+)\)"), 4, True),
			block_relay: (re.compile(r"BlockRelay\((\d+),(\d+),(\d+)\)"), 3, True),
		}

		count_variables = {}
		variables = []
		time_range = [int(1e20), int(-1e20)]
		nodes_range = [int(1e10), int(-1e10)]
		views_range = [int(1e10), int(-1e10)]

		for variable in sol.variables.variable:
			call_var = variable.get('name')
			name = call_var[:call_var.index('(')] if '(' in call_var else call_var

			if name in count_variables:
				count_variables[name] += 1
			else:
				count_variables[name] = 1

			if name in patterns:
				pattern, n_params, start_with_time = patterns[name]
				variable_params = re.search(pattern, call_var)
				variable_params = [int(variable_params.group(x)) for x in range(1, n_params + 1)]
				variables += [(name, variable_params)]

				if start_with_time:
					time_range[0] = min(time_range[0], variable_params[0])
					time_range[1] = max(time_range[1], variable_params[0])

				nodes_range[0] = min(nodes_range[0], variable_params[1])
				nodes_range[1] = max(nodes_range[1], variable_params[1])
				if len(variable_params) == 4:
					nodes_range[0] = min(nodes_range[0], variable_params[2])
					nodes_range[1] = max(nodes_range[1], variable_params[2])

				views_range[0] = min(views_range[0], variable_params[-1])
				views_range[1] = max(views_range[1], variable_params[-1])

		# Sorting by the first parameter
		# temp_variables = sorted(variables, key=lambda x: x[1][0])
		temp_variables = sorted(variables, key=lambda x: x[0], reverse=True)

		variables = []
		send_message = {}
		for variable in temp_variables:
			name, variable_params = variable
			message_direction = name[:4]
			message_name = name[4:]
			if name in send_receive_variables:
				if message_direction == 'Send':
					if message_name not in send_message:
						send_message[message_name] = {}
					_, node, _ = variable_params
					if node not in send_message[message_name]:
						send_message[message_name][node] = []

					for node_i in range(nodes_range[0], nodes_range[1] + 1):
						send_message[message_name][node] += [variable_params]
				elif message_direction == 'Recv':
					time, node, node_from, _ = variable_params
					if node != node_from:
						assert message_name in send_message, f"There is no previous {message_name} for {variable}"
						assert \
							node_from in send_message[message_name], \
							f"There is no previous {message_name} for the node {node_from}"
						try:
							send_time, _, _ = send_message[message_name][node_from][-1]
						except:
							print("oi")
						send_message[message_name][node_from].pop()
						variables += [(message_name, [send_time, node_from, time, node])]
					else:
						# It is not drawing a message to the node itself
						pass

		with TikzDrawer() as my_drawer:
			last_time = 1
			for variable in variables:
				name, variable_params = variable
				if name == primary:
					node, view = variable_params
					my_drawer.node(f"$Pr.^{view}$", (last_time, node - 1.5))
				# last_time += 1
				elif name in send_receive_variables_options:
					send_time, node_from, time, node = variable_params
					last_time = max([last_time, send_time, time])
					options = send_receive_variables_options[name]
					my_drawer.line((send_time, node_from - 1), (time + 1, node - 1), options)
				# last_time += 1
				elif name == block_relay:
					time, node, _ = variable_params
					last_time = max(last_time, time)
					for node_i in range(nodes_range[0], nodes_range[1] + 1):
						if node_i != node:
							my_drawer.line((time, node - 1), (time + 1, node_i - 1), ['thick', '->', 'color=lime'])
			# last_time += 1

			line_size = last_time + 1
			for node in range(nodes_range[0], nodes_range[1] + 1):
				my_drawer.node(str(node), (0, node - 1))
				my_drawer.line((1, node - 1), (line_size, node - 1))

		# \node[draw] at (1,-0.5) {$Pr.^0$};

		if verbose:
			print(
				f"Problem: {sol.header.get('problemName')}, solution: {sol.header.get('solutionName')} has "
				f"{len(sol.variables.variable)} variables, {len(sol.linearConstraints.constraint)} linear constraints"
			)
			print(f"Time: {time_range}, nodes: {nodes_range}, views: {views_range}")
			print(count_variables)

# /* =================== */
# /* {DECISION VARIABLES */
# var primary{R,V}, binary;
# var SendPrepReq{T,R,V}, binary;
# var SendPrepResp{T,R,V}, binary;
# var SendCV{T,R,V}, binary;
# var RecvPrepReq{T,R,R,V}, binary;
# var RecvPrepResp{T,R,R,V}, binary;
# var RecvCV{T,R,R,V}, binary;
# var BlockRelay{T,R,V}, binary;
# /* DECISION VARIABLES} */
# /* ================== */
# T for the time
# R for the nodes
# V for the views
