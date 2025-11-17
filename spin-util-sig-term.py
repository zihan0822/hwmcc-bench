#!/usr/bin/env python3
import argparse
import subprocess
import signal
import time
import re
import sys


def run_benchmark(program_args, duration, regex_pattern):
    """
    Run a program for a specified duration, kill it, and extract metrics.

    Args:
        program_args: List of program arguments (e.g., ['./myprogram', 'arg1'])
        duration: Time in seconds to run the program
        regex_pattern: Regex pattern to extract metric values

    Returns:
        Tuple of (average_per_second, total_value) or None if extraction failed
    """
    # Start the process
    process = subprocess.Popen(
        program_args,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
    )

    print(f"Started process (PID: {process.pid})")
    print(f"Running for {duration} seconds...")

    # Collect output for the specified duration
    output_lines = []
    start_time = time.time()

    try:
        while time.time() - start_time < duration:
            # Check if process is still running
            if process.poll() is not None:
                print("Process terminated early")
                break

            # Try to read a line with a short timeout
            time.sleep(0.1)

        # Send SIGTERM to gracefully terminate
        print(f"\nSending SIGTERM to process {process.pid}")
        process.send_signal(signal.SIGTERM)

        # Wait a bit for graceful shutdown
        try:
            stdout, stderr = process.communicate(timeout=2)
        except subprocess.TimeoutExpired:
            # Force kill if it doesn't terminate
            print("Process didn't terminate, sending SIGKILL")
            process.kill()
            stdout, stderr = process.communicate()

        output_lines = stdout.splitlines()

    except KeyboardInterrupt:
        print("\nInterrupted by user, killing process")
        process.kill()
        process.communicate()
        sys.exit(1)

    # Extract metric using regex (should be one total value)
    pattern = re.compile(regex_pattern)
    total_value = None

    for line in output_lines:
        match = pattern.search(line)
        if match:
            try:
                # Try to extract first capture group, or full match
                value_str = match.group(1) if match.groups() else match.group(0)
                # Remove any non-numeric characters except decimal point and minus
                value_str = re.sub(r"[^\d.\-]", "", value_str)
                total_value = float(value_str)
                break  # Take the first match
            except (ValueError, IndexError):
                continue

    if total_value is None:
        print("\nWarning: No value matched the regex pattern")
        print(f"Regex pattern used: {regex_pattern}")
        print("\nSample output lines:")
        for line in output_lines[:10]:
            print(f"  {line}")
        return None

    # Calculate average: total cycles / duration
    avg_per_second = total_value / duration
    return avg_per_second, total_value


def main():
    parser = argparse.ArgumentParser(
        description="Run a program for a specified time and extract performance metrics",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Single executable
  %(prog)s -t 10 -r "cycles: (\\d+)" ./myprogram
  
  # Multiple executables
  %(prog)s -t 10 -r "cycles: (\\d+)" ./program1 ./program2 ./program3
  
  # Executables with arguments (use -- to separate different executables)
  %(prog)s -t 5 -r "time: ([0-9.]+)" ./prog1 --fast -- ./prog2 --slow -- ./prog3
  
  # Shell expansion for multiple executables
  %(prog)s -t 10 -r "cycles: (\\d+)" ./build/benchmark_*
        """,
    )

    parser.add_argument(
        "-t",
        "--time",
        type=float,
        required=True,
        help="Duration to run the program (in seconds)",
    )

    parser.add_argument(
        "-r",
        "--regex",
        type=str,
        required=True,
        help="Regex pattern to extract metric values (use capture group for the number)",
    )

    parser.add_argument(
        "executables", nargs="+", help="One or more executables to benchmark"
    )

    parser.add_argument(
        "--args",
        type=str,
        default="",
        help="Arguments to pass to each executable (same args for all)",
    )

    args = parser.parse_args()

    # Parse executables - each space-separated item is a separate executable
    # If user wants to pass args, they use --args flag
    executables = []

    if "--" in args.executables:
        # Use -- as separator for executables with different arguments
        current_exec = []
        for item in args.executables:
            if item == "--":
                if current_exec:
                    executables.append(current_exec)
                    current_exec = []
            else:
                current_exec.append(item)
        if current_exec:
            executables.append(current_exec)
    else:
        # Each item is a separate executable
        extra_args = args.args.split() if args.args else []
        for exe in args.executables:
            executables.append([exe] + extra_args)

    print(f"Benchmarking {len(executables)} executable(s)")
    print(f"Duration: {args.time}s per executable")
    print(f"Regex pattern: {args.regex}")
    print("-" * 50)

    # Run benchmark for each executable
    results = []
    for i, exec_args in enumerate(executables, 1):
        print(f"\n{'=' * 50}")
        print(f"Executable {i}/{len(executables)}: {' '.join(exec_args)}")
        print("=" * 50)

        result = run_benchmark(exec_args, args.time, args.regex)

        if result:
            avg_per_second, total_value = result
            results.append(avg_per_second)
            print(f"\nTotal cycles: {total_value:,.0f}")
            print(f"Duration: {args.time:.2f} seconds")
            print(f"Cycles/second: {avg_per_second:,.2f}")
        else:
            print(f"\nFailed to extract metrics for {' '.join(exec_args)}")

    # Display overall statistics if multiple executables
    if len(executables) > 1 and results:
        print(f"\n{'=' * 50}")
        print(f"OVERALL RESULTS ({len(results)} executables)")
        print(f"{'=' * 50}")
        print(f"Mean cycles/second: {sum(results) / len(results):,.2f}")
        print(f"Min cycles/second: {min(results):,.2f}")
        print(f"Max cycles/second: {max(results):,.2f}")
        print(f"{'=' * 50}")
    elif not results:
        print("\nNo successful results")
        sys.exit(1)


if __name__ == "__main__":
    main()
