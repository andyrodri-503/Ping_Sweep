A Python-based tool for scanning a network to see which hosts are up.

## Features
- Cross-platform (Windows, macOS, Linux)
- Command-line interface (CLI) via argparse
- Multithreaded scanning for speed
- Logging of host status

## Usage
Run the script from the terminal or command prompt:
 ```bash
python ping_sweep.py 192.168.1.0/24 --threads 40 --timeout 300 --quiet
```
- `192.168.1.0/24` → replace with the network you want to scan  
- `--threads` → number of parallel pings (default: 32)  
- `--timeout` → ping timeout in milliseconds (default: 300)  
- `--quiet` → hides per-host output

## Author
Andy
