import socket
import socks
import requests
import time

def test_direct_connection():
    """Test if we can connect to the internet directly without Tor"""
    try:
        print("Testing direct internet connection...")
        response = requests.get("https://www.google.com", timeout=10)
        print(f"Direct connection successful! Status code: {response.status_code}")
        return True
    except Exception as e:
        print(f"Direct connection failed: {e}")
        return False

def test_tor_connection(socks_port=9050):
    """Test if we can connect through Tor"""
    # Configure requests to use Tor
    session = requests.session()
    proxy_url = f'socks5h://127.0.0.1:{socks_port}'
    session.proxies = {
        'http': proxy_url,
        'https': proxy_url
    }
    
    print(f"Using Tor proxy: {proxy_url}")
    
    # Try multiple IP checking services
    services = [
        "https://check.torproject.org/api/ip",
        "https://api.ipify.org?format=json",
        "https://httpbin.org/ip",
        "https://www.google.com"
    ]
    
    for service in services:
        try:
            print(f"Trying to connect to {service} through Tor...")
            start_time = time.time()
            response = session.get(service, timeout=30)
            elapsed = time.time() - start_time
            print(f"Connection to {service} successful! Status code: {response.status_code}")
            print(f"Response time: {elapsed:.2f} seconds")
            if 'json' in service:
                print(f"Response: {response.text}")
            return True
        except Exception as e:
            print(f"Error connecting to {service} through Tor: {e}")
    
    return False

def test_socket_connection(socks_port=9050):
    """Test direct socket connection through Tor"""
    # Save the original socket
    original_socket = socket.socket
    
    try:
        # Configure socket to use Tor
        socks.set_default_proxy(socks.SOCKS5, "127.0.0.1", socks_port)
        socket.socket = socks.socksocket
        
        # Test connections to different services
        test_hosts = [
            ("www.google.com", 80),
            ("check.torproject.org", 443),
            ("api.ipify.org", 443),
            ("httpbin.org", 80)
        ]
        
        for host, port in test_hosts:
            try:
                print(f"Testing socket connection to {host}:{port} through Tor...")
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(30)
                start_time = time.time()
                s.connect((host, port))
                elapsed = time.time() - start_time
                s.close()
                print(f"Socket connection to {host}:{port} successful!")
                print(f"Connection time: {elapsed:.2f} seconds")
                return True
            except Exception as e:
                print(f"Socket connection to {host}:{port} failed: {e}")
        
        return False
    finally:
        # Restore the original socket
        socket.socket = original_socket

def main():
    # First test direct connection
    direct_success = test_direct_connection()
    if not direct_success:
        print("WARNING: Direct internet connection failed. Check your network connection.")
    
    # Test Tor connection using requests
    tor_success = test_tor_connection()
    if not tor_success:
        print("Tor connection using requests failed.")
    
    # Test Tor connection using sockets
    socket_success = test_socket_connection()
    if not socket_success:
        print("Tor connection using sockets failed.")
    
    # Summary
    print("\nTest Summary:")
    print(f"Direct Internet Connection: {'SUCCESS' if direct_success else 'FAILED'}")
    print(f"Tor Connection (requests): {'SUCCESS' if tor_success else 'FAILED'}")
    print(f"Tor Connection (sockets): {'SUCCESS' if socket_success else 'FAILED'}")
    
    if not (tor_success or socket_success):
        print("\nPossible issues:")
        print("1. Tor is not running or not listening on port 9050")
        print("2. Firewall is blocking Tor connections")
        print("3. Network restrictions preventing Tor from connecting to the Tor network")
        print("4. Tor has not fully bootstrapped to 100%")

if __name__ == "__main__":
    main()