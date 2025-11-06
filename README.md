# Ping Sweep

Python script that scans a network and tells you which devices are up. Works on Windows, macOS, and Linux.

## Features

- Fast network sweep using multiple threads
- Shows which hosts are UP or DOWN
- Minimal logging, or quiet mode for just a summary
- Works with any CIDR network (e.g., 192.168.1.0/24)

## Requirements

- Python 3.x
- No extra packages

## How to Use

1. Clone or download this repo.
2. Open a terminal in the project folder.
3. Run:

```bash
python ping_sweep.py 192.168.1.0/24 --threads 40 --timeout 300
```

### Optional flags
- `--threads` — number of parallel pings (default: 32)  
- `--timeout` — ping timeout in milliseconds (default: 300)  
- `--quiet` — only show summary, no per-host logs  

Press Ctrl + C to stop the scan.
