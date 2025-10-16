import argparse
import json
from backend import start_process, stop_process, status_process, list_processes

def main():
    parser = argparse.ArgumentParser(description="Process Manager CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    parser_start = subparsers.add_parser("start", help="Start a new process")
    parser_start.add_argument("cmd", help="Command to execute")

    parser_stop = subparsers.add_parser("stop", help="Stop a process")
    parser_stop.add_argument("pid", type=int, help="Process PID to stop")

    parser_status = subparsers.add_parser("status", help="Check process status")
    parser_status.add_argument("pid", type=int, help="Process PID to check")

    parser_list = subparsers.add_parser("list", help="List all processes")

    args = parser.parse_args()

    if args.command == "start":
        result = start_process(args.cmd)
        print(json.dumps(result, indent=4))
    elif args.command == "stop":
        result = stop_process(args.pid)
        print(json.dumps(result, indent=4))
    elif args.command == "status":
        result = status_process(args.pid)
        print(json.dumps(result, indent=4))
    elif args.command == "list":
        result = list_processes()
        print(json.dumps(result, indent=4))
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
