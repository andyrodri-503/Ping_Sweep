#!/usr/bin/env python3
"""
Cross-platform ping sweep with:
- CLI via argparse
- ThreadPoolExecutor for parallel pings
- logging for structured messages

Usage:
  python ping_sweep.py 192.168.1.0/24 --threads 40 --timeout 300 --quiet
"""
import argparse
import concurrent.futures
import ipaddress
import platform
import subprocess
import logging
import sys
import time

# --- Logging setup ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

def get_ping_command(ip, timeout_ms):
    """
    Return a list representing the OS-appropriate ping command for one ping.
    timeout_ms is interpreted in milliseconds for Windows; for Unix-like systems
    it's converted to seconds (minimum 1s).
    """
    system = platform.system()
    if system == "Windows":
        # -n 1 => send 1 ping, -w <ms> => timeout in ms
        return ["ping", "-n", "1", "-w", str(timeout_ms), str(ip)]
    else:
        # Unix-like: -c 1 => send 1 ping, -W <secs> => timeout in seconds (Linux)
        secs = max(1, int((timeout_ms + 999) // 1000))
        return ["ping", "-c", "1", "-W", str(secs), str(ip)]

def ping_once(ip, timeout_ms):
    """
    Ping a single IP once. Returns True if host is reachable, False otherwise.
    Uses the system 'ping' binary; raises RuntimeError if ping is missing.
    """
    cmd = get_ping_command(ip, timeout_ms)
    try:
        result = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return result.returncode == 0
    except FileNotFoundError:
        raise RuntimeError("'ping' command not found on this system")

def sweep_network(network_cidr, threads, timeout_ms, quiet=False):
    """
    Sweep the provided CIDR network in parallel and return a list of (ip, up_bool).
    If quiet is False, each host status will be logged at INFO level.
    """
    net = ipaddress.ip_network(network_cidr, strict=False)
    hosts = [str(ip) for ip in net.hosts()]
    results = []

    logging.info("Starting sweep of %s (%d hosts) with %d threads", network_cidr, len(hosts), threads)

    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
        future_to_ip = {executor.submit(ping_once, ip, timeout_ms): ip for ip in hosts}
        for future in concurrent.futures.as_completed(future_to_ip):
            ip = future_to_ip[future]
            try:
                up = future.result()
            except Exception as exc:
                up = False
                logging.error("Error pinging %s: %s", ip, exc)
            results.append((ip, up))
            if not quiet:
                if up:
                    logging.info("%s is UP", ip)
                else:
                    logging.info("%s is DOWN", ip)

    return results

def parse_args():
    parser = argparse.ArgumentParser(description="Simple cross-platform ping sweep")
    parser.add_argument("network", help="Network in CIDR form, e.g. 192.168.1.0/24")
    parser.add_argument("--threads", type=int, default=32, help="Number of parallel threads (default: 32)")
    parser.add_argument("--timeout", type=int, default=300, help="Timeout in milliseconds (default: 300)")
    parser.add_argument("--quiet", action="store_true", help="Minimize per-host logging")
    return parser.parse_args()

def main():
    args = parse_args()
    start = time.time()
    try:
        results = sweep_network(args.network, max(1, args.threads), max(1, args.timeout), quiet=args.quiet)
    except RuntimeError as e:
        logging.critical(str(e))
        sys.exit(1)

    elapsed = time.time() - start
    up_count = sum(1 for _, up in results if up)
    total = len(results)
    logging.info("Scan finished: %d/%d hosts up (%.1fs)", up_count, total, elapsed)

if __name__ == "__main__":
    main()