#!/usr/bin/env python3
import argparse
import heapq
import sys
from collections import defaultdict
import copy

# GLOBALS
topo = None
flows = []
_next_flow_id = 1
_rr_counters = defaultdict(int)


# Flow Data Structure
class Flow:
	"""Represents a flow in the network"""
	def __init__(self, flow_id, src, dst, traffic_type, priority, primary_path, backup_path=None):
		self.id = flow_id
		self.src = src
		self.dst = dst
		self.type = traffic_type
		self.priority = priority
		self.primary_path = primary_path
		self.backup_path = backup_path

	def table_entries(self, use_backup=False):
		"""Generate flow table entries"""
		path = self.backup_path if use_backup and self.backup_path else self.primary_path
		entries = []
		for i in range(len(path) - 1):
			switch = path[i]
			out_port = path[i + 1]
			match = f"src={self.src}, dst={self.dst}, type={self.type}, priority={self.priority}"
			entries.append((switch, match, out_port))
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
	
	def _dijkstra(self, src):
		dist = {src: 0}
		heap = [(0, src)]
		while heap:
			d, u = heapq.heappop(heap)
			if d > dist[u]:
				continue
			for v, w in self.adj[u].items():
				nd = d + w
				if v not in dist or nd < dist[v]:
					dist[v] = nd
					heapq.heappush(heap, (nd, v))
		return dist
	
	def all_shortest_paths(self, src, dst):
		if src not in self.adj or dst not in self.adj:
			return []
		dist_src = self._dijkstra(src)
		dist_dst = self._dijkstra(dst)
		if dst not in dist_src:
			return []
		target = dist_src[dst]
		paths = []
		def dfs(u, path):
			if u == dst:
				paths.append(path.copy())
				return
			for v, w in self.adj[u].items():
				if v not in path and dist_src[u] + w + dist_dst.get(v, float('inf')) == target:
						path.append(v)
						dfs(v, path)
						path.pop()
		dfs(src, [src])
		return paths
	
	def shortest_path(self, src, dst):
		paths = self.all_shortest_paths(src, dst)
		return paths[0] if paths else None
	

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
	paths = topo.all_shortest_paths(args.src, args.dst)
	if not paths:
		print(f'No path found from {args.src} to {args.dst}')
		return
	# Round-robin load balancing
	index = _rr_counters[(args.src, args.dst)] % len(paths)
	_rr_counters[(args.src, args.dst)] += 1
	primary = paths[index]
	# Backup path for critical flows
	backup = None
	if args.critical:
		# Remove strongest edges
		removed = []
		for u, v in zip(primary, primary[1:]):
			if v in topo.adj[u]:
				removed.append((u, v, topo.adj[u][v]))
			topo.remove_link(u, v)
		backup_paths = topo.all_shortest_paths(args.src, args.dst)
		backup = backup_paths[0] if backup_paths else None
		# Restore edges
		for u, v, w in removed:
			topo.add_link(u, v, w)
		if backup:
			print(f"Backup path found: {backup}")
	flow = Flow(_next_flow_id, args.src, args.dst, args.type, args.priority, primary, backup)
	_next_flow_id += 1
	flows.append(flow)
	# Display flow table entries
	print(f'Injecting flow {flow.id}: {flow.src} -> {flow.dst} on path {flow.primary_path}')
	for switch, match, out_port in flow.table_entries():
		print(f'  Switch {switch}: match [{match}] -> out_port={out_port}')

def fail_link(args):
	topo.remove_link(args.node1, args.node2)
	print(f'Link failed: {args.node1} <-> {args.node2}')
	# reroute flows
	for flow in flows:
		if any((flow.primary_path[i], flow.primary_path[i+1]) == (args.node1, args.node2) or (flow.primary_path[i], flow.primary_path[i+1]) == (args.node2, args.node1) for i in range(len(flow.primary_path) - 1)):
			if flow.backup_path:
				print(f'Rerouting flow {flow.id} from {flow.primary_path} to backup path {flow.backup_path}')
				# Update flow table entries
				for switch, match, out_port in flow.table_entries(use_backup=True):
					print(f'  Switch {switch}: match [{match}] -> out_port={out_port}')
			else:
				new_path = topo.shortest_path(flow.src, flow.dst)
				print(f'Rerouting flow {flow.id} from {flow.primary_path} to new path {new_path}')
				for switch, match, out_port in Flow(flow.id, flow.src, flow.dst, flow.type, flow.priority, new_path).table_entries():
					print(f'  Switch {switch}: match [{match}] -> out_port={out_port}')

def show_topo(args):
	print('Nodes: ', topo.nodes())
	print('Links: ', topo.links())

def show_route(args):
	path = topo.all_shortest_paths(args.src, args.dst)
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
	p.add_argument('--priority', type=int, default=0, help='Priority of the flow')
	p.add_argument('--critical', action='store_true', help='Enable backup path')
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
