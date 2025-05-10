#!/usr/bin/env python3
import argparse

def add_node(args):
	print(f'Adding node: {args.node}')

def remove_node(args):
	print(f'Removing node: {args.node}')

def add_link(args):
	print(f'Adding link: {args.node1} <-> {args.node2}')

def remove_link(args):
	print(f'Removing link: {args.node1} <-> {args.node2}')

def inject_flow(args):
	print(f'Injecting flow: src={args.src}, dst={args.dst}, type={args.type}')

def fail_link(args):
	print(f'Failing link: {args.node1} <-> {args.node2}')

def show_topo(args):
	print('Current topology: ...PLACEHOLDER...')

def show_route(args):
	print(f'Showing route from {args.src} to {args.dst}: ...PLACEHOLDER...')


def main():
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
	if hasattr(args, 'func'):
		args.func(args)
	else:
		parser.print_help()


if __name__ == '__main__':
	main()
