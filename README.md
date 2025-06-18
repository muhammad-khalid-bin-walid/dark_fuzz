# DarkFuzz Usage Guide

**DarkFuzz** is a high-performance web fuzzing tool for security researchers and pentesters, supporting HTTP/HTTPS, WebSocket, and custom protocols. Made by Dark Legend.

## Installation

### Prerequisites
- Python 3.8+
- Required packages:
  ```
  aiohttp>=3.8.0
  colorama>=0.4.4
  websockets>=10.0
  ```

### Install Dependencies
```bash
pip install -r requirements.txt
```

## Basic Usage
Fuzz a URL with a wordlist:
```bash
python darkfuzz.py -u http://example.com/FUZZ -w words.txt
```
- `-u`: URL with `FUZZ` placeholder.
- `-w`: Path to wordlist file.

## Command-Line Options

| Option | Description | Example |
|--------|-------------|---------|
| `-u, --url` | Base URL with FUZZ placeholder(s) (required) | `-u http://example.com/FUZZ` |
| `-w, --wordlist` | Path to wordlist file(s) (multiple allowed) | `-w words.txt -w extras.txt` |
| `-o, --output` | Output file (default: `fuzz_results.txt`) | `-o results.json` |
| `-c, --concurrency` | Concurrent requests (default: 300) | `-c 500` |
| `--show` | Show specific status codes | `--show 200,301` |
| `--hide` | Hide specific status codes | `--hide 404,403` |
| `--min-size` | Minimum response size | `--min-size 100` |
| `--max-size` | Maximum response size | `--max-size 10000` |
| `--min-lines` | Minimum response lines | `--min-lines 10` |
| `--max-lines` | Maximum response lines | `--max-lines 1000` |
| `--match-regex` | Regex to match in response | `--match-regex "login"` |
| `--header-filter` | Filter by response headers | `--header-filter Server:nginx` |
| `--content-type` | Filter by Content-Type | `--content-type text/html` |
| `--method` | HTTP method (default: GET) | `--method POST` |
| `--headers` | JSON custom headers | `--headers '{"User-Agent": "Fuzzer"}'` |
| `--data` | POST data | `--data "key=value"` |
| `--timeout` | Request timeout in seconds (default: 10) | `--timeout 5` |
| `--retries` | Retries for failed requests (default: 3) | `--retries 5` |
| `--delay` | Delay between requests (ms) | `--delay 100` |
| `--jitter` | Max jitter for delay (ms) | `--jitter 200` |
| `--rate-limit` | Max requests per second | `--rate-limit 200` |
| `--proxy` | Proxy URL | `--proxy http://localhost:8080` |
| `--numeric` | Numeric range for payloads | `--numeric 1-1000` |
| `--chars` | Character set for combinations | `--chars abc:3` |
| `--mutations` | Payload mutations (upper, lower, urlencode, doubleencode) | `--mutations upper,lower` |
| `--output-format` | Output format (txt, json, csv; default: txt) | `--output-format json` |
| `--extract-title` | Extract HTML titles | `--extract-title` |
| `--session` | Session file for save/resume | `--session fuzz.session` |
| `--resume` | Resume from session | `--resume` |
| `--db` | SQLite database file (default: in-memory) | `--db results.db` |
| `--random-ua` | Random User-Agent headers | `--random-ua` |
| `--websocket` | Fuzz WebSocket endpoints | `--websocket` |
| `--custom-protocol` | Custom protocol (e.g., ftp, smtp) | `--custom-protocol ftp` |
| `--cluster` | Cluster similar responses | `--cluster` |
| `--ext-payload` | Custom payload script | `--ext-payload custom_payload.py` |
| `--ext-response` | Custom response script | `--ext-response custom_response.py` |
| `--header-fuzz` | Fuzz headers with random values | `--header-fuzz` |
| `--adaptive` | Adapt concurrency by response time | `--adaptive` |
| `--dashboard` | Show real-time ASCII dashboard | `--dashboard` |

## Examples

### Basic Fuzzing
```bash
python darkfuzz.py -u http://example.com/FUZZ -w words.txt
```

### WebSocket Fuzzing
```bash
python darkfuzz.py -u ws://example.com/FUZZ -w words.txt --websocket
```

### Advanced Fuzzing
```bash
python darkfuzz.py -u http://example.com/FUZZ -w words.txt -w extras.txt --numeric 1-1000 \
--show 200,301 --output-format json --concurrency 500
```

### Full-Power Fuzzing
```bash
python darkfuzz.py -u http://example.com/FUZZ -w words.txt --numeric 1-1000 --chars abc:3 \
--mutations upper,lower,urlencode,doubleencode --show 200,301 --content-type text/html \
--output-format csv --concurrency 500 --random-ua --header-fuzz --jitter 200 --rate-limit 200 \
--proxy http://localhost:8080 --extract-title --cluster --dashboard --adaptive \
--ext-payload custom_payload.py --db results.db
```

### Custom Extension
```python
# custom_payload.py
def generate_payloads(base):
    return [p + "_dark" for p in base]
```
```bash
python darkfuzz.py -u http://example.com/FUZZ -w words.txt --ext-payload custom_payload.py
```

## Notes
- URL must contain at least one `FUZZ` placeholder.
- Custom protocols require extension scripts (e.g., `--custom-protocol ftp --ext-payload ftp_script.py`).
- Use responsibly on authorized targets only.
- Made by Dark Legend.
