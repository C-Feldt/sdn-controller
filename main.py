#!/usr/bin/env python3
import argparse
import heapq
import sys

# GLOBALS
topo = None
flows = []
_next_flow_id = 0


# Flow Data Structure
class Flow:
	"""Represents a flow in the network"""
	def __init__(self, flow_id, src, dst, traffic_type, path):
		self.id = flow_id
		self.src = src
		self.dst = dst
		self.type = traffic_type
		self.path = path

	def table_entries(self):
		"""Generate flow table entries"""
		entries = []
		for i in range(len(self.path) - 1):
			node = self.path[i]
			out_port = self.path[i + 1]
			match = f"src={self.src}, dst={self.dst}, type={self.type}"
			entries.append((node, match, out_port))
		return entries


# Topology Class
class Topology:
	"""Graph with weighted edges and Dijkstra's shortest path"""
	def __init__(self):
		self.adj = {}

	def add_node(self, node):
		self.adj.setdefault(node, {})

	def remove_node(self, node):
		if node in self.adj:
			del self.adj[node]
			for num in self.adj.values():
				num.pop(node, None)

	def add_link(self, u, v, weight=1):
		self.add_node(u)
		self.add_node(v)
		self.adj[u][v] = weight
		self.adj[v][u] = weight

	def remove_link(self, u, v):
		if u in self.adj:
			self.adj[u].pop(v, None)
		if v in self.adj:
			self.adj[v].pop(u, None)

	def nodes(self):
		return list(self.adj.keys())
	
	def links(self):
		seen = set()
		out = []
		for u, num in self.adj.items():
			for v, w in num.items():
				if (v, u) not in seen:
					out.append((u, v, w))
					seen.add((u, v))
		return out
	
	def shortest_path(self, src, dst):
		if src not in self.adj or dst not in self.adj:
			return None
		dist = {src: 0}
		prev = {}
		heap = [(0, src)]
		while heap:
			d, u = heapq.heappop(heap)
			if u == dst:
				break
			if d > dist[u]:
				continue
			for v, w in self.adj[u].items():
				nd = d + w
				if v not in dist or nd < dist[v]:
					dist[v] = nd
					prev[v] = u
					heapq.heappush(heap, (nd, v))
		if dst not in dist:
			return None
		path = []
		node = dst
		while node != src:
			path.append(node)
			node = prev[node]
		path.append(src)
		path.reverse()
		return path
	

topo = Topology() # Global topology


# CLI commands

def add_node(args):
	topo.add_node(args.node)
	print(f'Adding node: {args.node}')

def remove_node(args):
	topo.remove_node(args.node)
	print(f'Removing node: {args.node}')

def add_link(args):
	topo.add_link(args.node1, args.node2)
	print(f'Adding link: {args.node1} <-> {args.node2}')

def remove_link(args):
	topo.remove_link(args.node1, args.node2)
	print(f'Removing link: {args.node1} <-> {args.node2}')

def inject_flow(args):
	global _next_flow_id
	path = topo.shortest_path(args.src, args.dst)
	if not path:
		print(f'No path found from {args.src} to {args.dst}')
		return
	flow_id = _next_flow_id
	_next_flow_id += 1
	flow = Flow(flow_id, args.src, args.dst, args.type, path)
	flows.append(flow)
	print(f'Injecting flow {flow_id}: {flow.src} -> {flow.dst} on path {flow.path}')
	for switch, match, out_port in flow.table_entries():
		print(f'  Switch {switch}: match [{match}] -> out_port={out_port}')

def fail_link(args):
	topo.remove_link(args.node1, args.node2)
	print(f'Link failed: {args.node1} <-> {args.node2}')

def show_topo(args):
	print('Nodes: ', topo.nodes())
	print('Links: ', topo.links())

def show_route(args):
	path = topo.shortest_path(args.src, args.dst)
	if path:
		print(f'Route: {path}')
	else:
		print(f'No route found from {args.src} to {args.dst}')

# Shell for commands
def repl(parser):
	print('Entering shell mode. Type \'exit\' or Ctrl-D to quit.')
	while True:
		try:
			line = input('> ')
		except EOFError:
			print('\nExiting shell.')
			break
		if not line.strip():
			continue
		if line.strip().lower() in ('exit', 'quit'):
			print('Exiting shell.')
			break
		parts = line.split()
		try:
			ns = parser.parse_args(parts)
			if hasattr(ns, 'func'):
				ns.func(ns)
			else:
				print('Unknown command. Type \'help\' for a list of commands.')
		except SystemExit:
			pass


def main():
	global topo
	topo = Topology()

	parser = argparse.ArgumentParser(description='SDN Controller CLI')
	subparsers = parser.add_subparsers(dest='command')

	# Add node
	p = subparsers.add_parser('add-node', help='Add a node')
	p.add_argument('node', help='Node ID')
	p.set_defaults(func=add_node)

	# Remove node
	p = subparsers.add_parser('remove-node', help='Remove a node')
	p.add_argument('node', help='Node ID')
	p.set_defaults(func=remove_node)

	# Add link
	p = subparsers.add_parser('add-link', help='Add a link')
	p.add_argument('node1', help='Source node ID')
	p.add_argument('node2', help='Destination node ID')
	p.set_defaults(func=add_link)

	# Remove link
	p = subparsers.add_parser('remove-link', help='Remove a link')
	p.add_argument('node1', help='Source node ID')
	p.add_argument('node2', help='Destination node ID')
	p.set_defaults(func=remove_link)

	# Inject flow
	p = subparsers.add_parser('inject-flow', help='Inject a traffic flow')
	p.add_argument('--src', required=True, help='Source node ID')
	p.add_argument('--dst', required=True, help='Destination node ID')
	p.add_argument('--type', default='default', help='Type of traffic')
	p.set_defaults(func=inject_flow)

	# Fail link
	p = subparsers.add_parser('fail-link', help='Simulate link failure')
	p.add_argument('node1', help='Source node ID')
	p.add_argument('node2', help='Destination node ID')
	p.set_defaults(func=fail_link)

	# Show topology
	p = subparsers.add_parser('show-topo', help='Show current topology')
	p.add_argument('--draw', action='store_true', help='Draw the topology')
	p.set_defaults(func=show_topo)

	# Show route
	p = subparsers.add_parser('show-route', help='Show route between nodes')
	p.add_argument('--src', required=True, help='Source node ID')
	p.add_argument('--dst', required=True, help='Destination node ID')
	p.set_defaults(func=show_route)

	args = parser.parse_args()
	if not args.command:
		repl(parser)
	elif hasattr(args, 'func'):
		args.func(args)
	else:
		parser.print_help()


if __name__ == '__main__':
	main()
