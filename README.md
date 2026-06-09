# Anonymous Browser

A powerful Python-based browser automation tool that provides anonymity through Tor integration, dynamic IP rotation, and advanced browser fingerprint masking. This project launches Selenium WebDriver with a SOCKS5 proxy that changes IP addresses every 10 seconds while implementing sophisticated anti-detection techniques.

# Demo Video

https://github.com/user-attachments/assets/4a9b4186-38c9-40dc-8c7a-4df6f43a2f86

## Features

🔐 **Complete Anonymity**
- Tor integration with obfs4 bridge support for bypassing ISP-level blocking
- Automatic IP rotation every 10 seconds via Tor circuit renewal
- GeoIP lookups for exit node information
- SOCKS5 proxy configuration for all traffic routing

🎭 **Advanced Fingerprint Obfuscation**
- Removes webdriver detection flags (`navigator.webdriver`)
- Randomizes browser viewport dimensions (1000-1200px width, 800-1080px height)
- Spoofs user agent strings with authentic Mozilla signatures
- Canvas fingerprinting randomization with noise injection
- WebRTC leak prevention
- Plugin simulation and navigator property spoofing
- Permissions query API interception

🚀 **Selenium Integration**
- Automated Chrome browser launches with proxy configuration
- Persistent browser profiles for session continuity
- Hardware concurrency spoofing
- Language preference manipulation
- Automation detection bypass through JavaScript injection

🛡️ **Security Features**
- No-sandbox disabled by default (can be configured)
- Dev SHM usage disabled for stability
- Local IP hiding with mDNS
- Certificate-based bridge authentication
- Configurable Tor control port and SOCKS port

## Project Structure

```
anonymous-browser/
├── ip_changer.py              # Core Tor management and IP rotation logic
├── sel.py                     # Selenium WebDriver initialization with anti-detection
├── test_tor_connection.py     # Connection diagnostics and verification
├── config.ini                 # Configuration file (ports, paths, delays)
├── requirements.txt           # Python dependencies
├── bridge.txt                 # Obfs4 bridge addresses for censorship bypass
├── data/
│   ├── geoip                 # GeoIP database for IPv4
│   └── geoip6                # GeoIP database for IPv6
├── tor/                       # Tor embedded binaries
│   ├── tor.exe
│   ├── pluggable_transports/
│   │   ├── lyrebird.exe      # Obfs4 plugin
│   │   ├── conjure.exe       # Conjure transport (optional)
│   │   └── pt_config.json
│   └── bridges.txt           # Bridge configuration
└── docs/                      # Documentation for dependencies
```

## Requirements

- **Python 3.7+**
- **Windows OS** (includes pre-configured Tor binaries)
- **Chrome/Chromium browser**
- **Tor binary** (included)
- **Pluggable Transports** (obfs4, included)

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/anonymous-browser.git
cd anonymous-browser
```

### 2. Install Python Dependencies
```bash
pip install -r requirements.txt
```

**Dependencies:**
- `selenium` - Browser automation framework
- `requests` - HTTP client library
- `stem` - Tor controller library
- `PySocks` - SOCKS proxy support

### 3. Verify Tor Setup
Ensure the following directories and files exist:
- `tor/tor.exe` - Tor executable
- `tor/pluggable_transports/lyrebird.exe` - Obfs4 transport
- `data/geoip` & `data/geoip6` - GeoIP databases
- `bridge.txt` - Bridge addresses (pre-configured with obfs4 bridges)

### 4. Update Configuration (Optional)
Edit `config.ini` to customize:
```ini
[Tor]
SocksPort = 9050          # SOCKS5 proxy port
ControlPort = 9051        # Tor control port
DataDirectory = tor_data  # Data storage location
NewNymDelay = 10          # IP rotation interval (seconds)

[Bridge]
UseBridges = true         # Enable bridge usage
BridgesFile = tor/bridge.txt  # Bridge configuration
```

## Quick Start

### Basic Usage

```python
from ip_changer import start_tor, get_current_ip
from sel import sel
import requests

# Step 1: Start Tor with bridges
print("Starting Tor...")
tor_process = start_tor()

# Step 2: Create a session with Tor proxy
session = requests.Session()
session.proxies = {
    'http': 'socks5h://127.0.0.1:9050',
    'https': 'socks5h://127.0.0.1:9050'
}

# Step 3: Check current IP
print("Current IP:", get_current_ip(session))

# Step 4: Launch anonymous browser
driver = sel(host='127.0.0.1', port=9050)
driver.get('https://example.com')

# Step 5: Browser automatically changes IP every 10 seconds
# Continue with your automation tasks...

# Cleanup
driver.quit()
```

### Test Tor Connection
```bash
python test_tor_connection.py
```

This will verify:
- Direct internet connectivity
- Tor proxy accessibility
- Current exit node IP
- Connection speeds

### Verify IP Rotation
```python
import time
from ip_changer import get_current_ip
import requests

session = requests.Session()
session.proxies = {'http': 'socks5h://127.0.0.1:9050', 'https': 'socks5h://127.0.0.1:9050'}

for i in range(5):
    ip = get_current_ip(session)
    print(f"Iteration {i+1}: IP = {ip}")
    time.sleep(11)  # Wait for IP rotation
```

## Configuration Details

### Tor Configuration (config.ini)

| Setting | Default | Description |
|---------|---------|-------------|
| `SocksPort` | 9050 | SOCKS5 proxy listening port |
| `ControlPort` | 9051 | Tor controller port |
| `DataDirectory` | tor_data | Where Tor stores data (certs, descriptors, etc.) |
| `GeoIPFile` | data/geoip | IPv4 geolocation database |
| `GeoIPv6File` | data/geoip6 | IPv6 geolocation database |
| `NewNymDelay` | 10 | Seconds between IP rotations (circuit renewal) |
| `TorCommand` | tor/tor.exe | Path to Tor executable |
| `UseBridges` | true | Enable obfs4 bridges for ISP bypass |
| `BridgesFile` | tor/bridge.txt | Bridge address file |

### Browser Fingerprint Spoofing

The `sel.py` module implements the following fingerprint obfuscation techniques:

| Technique | Purpose |
|-----------|---------|
| Random User-Agent | Mimics different browser versions |
| Random Window Size | Prevents resolution-based tracking |
| Canvas Noise Injection | Breaks canvas fingerprinting |
| WebRTC Leak Prevention | Hides local IP through mDNS |
| Plugin Simulation | Simulates browser plugins |
| Navigator Property Spoofing | Masks automation detection |
| Permissions API Interception | Handles permission queries naturally |

## Advanced Usage

### Custom User Agents
Edit `sel.py` to add more realistic user agents:
```python
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36...",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)...",
]
```

### Modify IP Rotation Speed
In `config.ini`:
```ini
NewNymDelay = 5  # Change IP every 5 seconds (faster rotation)
```

### Add More Bridges
Edit or append to `bridge.txt`:
```
obfs4 <IP>:<PORT> <FINGERPRINT> cert=<CERT> iat-mode=<MODE>
```

## Troubleshooting

### Connection Issues

**"Failed to connect to Tor"**
```bash
# Check if ports 9050 and 9051 are available
netstat -ano | findstr :9050
netstat -ano | findstr :9051
```

**"Bridge connection failed"**
- Verify internet connectivity: `python test_tor_connection.py`
- Check bridge validity in `bridge.txt`
- Ensure obfs4 transport binary exists at `tor/pluggable_transports/lyrebird.exe`

**"Chrome driver not found"**
```bash
# Ensure chromedriver is in PATH or in current directory
# Or update webdriver initialization in sel.py with explicit path
driver = webdriver.Chrome(executable_path='./chromedriver', options=options)
```

### Performance Issues

- **Slow connections**: Bridges add latency; direct Tor is faster but less censorship-resistant
- **Memory usage**: Each browser instance uses ~150-300MB; limit concurrent instances
- **IP not changing**: Verify `NewNymDelay` is set and check Tor logs at `tor_data/notice.log`

## Legal & Ethical Considerations

⚠️ **Important Disclaimer:**

This tool is designed for **legitimate privacy and security research purposes only**. Users are responsible for ensuring their usage complies with applicable laws and the terms of service of websites they access.

### Legal Considerations:
- Unauthorized access to computer systems is illegal
- Bypassing authentication mechanisms violates the CFAA (US) and similar laws globally
- Web scraping may violate website terms of service and copyright laws
- Some jurisdictions restrict or prohibit circumventing censorship tools

### Responsible Use:
- Only access systems you own or have explicit permission to access
- Respect robots.txt and website terms of service
- Do not impersonate other users or services
- Be mindful of server load when automating requests
- Use for security research, privacy testing, and legitimate automation only

## Performance Tips

1. **Reduce fingerprinting overhead**: Disable unused spoofing for faster loads
2. **Connection pooling**: Reuse sessions across requests
3. **Batch operations**: Group multiple tasks before IP rotation
4. **Monitor resources**: Watch memory usage with many concurrent instances
5. **Cache GeoIP**: Pre-load geolocation databases for faster lookups

## Dependencies & Versions

| Package | Version | Purpose |
|---------|---------|---------|
| selenium | 4.x | Browser automation |
| requests[socks] | 2.28+ | HTTP with SOCKS proxy support |
| stem | 1.8+ | Tor control and management |
| PySocks | 1.7+ | SOCKS protocol implementation |

## Future Enhancements

- [ ] Multi-platform support (Linux, macOS)
- [ ] Docker containerization
- [ ] Dynamic proxy list support
- [ ] Browser fingerprint randomization via machine learning
- [ ] VPN chain integration (Tor + VPN)
- [ ] Real-time geolocation spoofing
- [ ] Automated bridge discovery and rotation
- [ ] Web UI for configuration and monitoring

## Contributing

Contributions are welcome! Please ensure your changes:
- Follow PEP 8 style guidelines
- Include proper error handling
- Add documentation for new features
- Test on Windows environment
- Consider privacy and security implications

## License

[Specify your license - MIT, GPL, Apache, etc.]

## Disclaimer

This software is provided "as-is" for educational and research purposes. The author assumes no liability for misuse, damage, or legal consequences resulting from usage of this tool. Users are solely responsible for ensuring their activities are legal and ethical in their jurisdiction.

## Support & Resources

- **Tor Project**: https://www.torproject.org/
- **Selenium Documentation**: https://selenium.dev/
- **Stem Library**: https://stem.torproject.org/
- **obfs4 Bridges**: https://bridges.torproject.org/

## Contact

For questions, issues, or suggestions, please open an issue on GitHub or contact the maintainers.

---

**Stay anonymous. Stay safe. Use responsibly.** 🔐
