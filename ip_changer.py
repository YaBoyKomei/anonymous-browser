import time
import requests
import stem.process
import configparser
import os
import socket
import socks
from stem import Signal
from stem.control import Controller

def test_socks_connection(proxy_host, proxy_port, target_host, target_port=80):
    try:
        sock = socks.socksocket()
        sock.settimeout(10)

        sock.set_proxy(socks.SOCKS5, proxy_host, proxy_port)

        print(f"Testing SOCKS connection to {target_host}:{target_port} via {proxy_host}:{proxy_port}...")
        sock.connect((target_host, target_port))

        sock.close()
        print("SOCKS connection test successful!")
        return True
    except Exception as e:
        print(f"SOCKS connection test failed: {e}")
        return False

def get_current_ip(session):
    try:
        services = [
            "https://check.torproject.org/api/ip",
            "https://api.ipify.org?format=json",
            "https://httpbin.org/ip"
        ]

        for service in services:
            try:
                print(f"Trying to get IP from {service}...")
                response = session.get(service, timeout=30)
                response.raise_for_status()

                if "torproject" in service:
                    ip = response.json()["IP"]
                    print(f"Successfully retrieved IP from {service}: {ip}")
                    return ip
                elif "ipify" in service:
                    ip = response.json()["ip"]
                    print(f"Successfully retrieved IP from {service}: {ip}")
                    return ip
                elif "httpbin" in service:
                    ip = response.json()["origin"]
                    print(f"Successfully retrieved IP from {service}: {ip}")
                    return ip
            except requests.RequestException as e:
                print(f"Error with {service}: {e}")
                continue
            except (KeyError, ValueError) as e:
                print(f"Error parsing response from {service}: {e}")
                continue

        print("All IP checking services failed")
        return None
    except Exception as e:
        print(f"Unexpected error getting IP: {e}")
        return None

def cleanup_old_tor_data_dirs(max_dirs_to_keep=0):
    try:
        unnecessary_files = [
            'generate_hash.bat',
            'tor-expert-bundle-windows-x86_64-14.5.4.tar',
            'tor-expert-bundle-windows-x86_64-14.5.4.tar.gz'
        ]
        for file_name in unnecessary_files:
            if os.path.exists(file_name):
                try:
                    os.remove(file_name)
                    print(f"Deleted unnecessary file: {file_name}")
                except Exception as e:
                    print(f"Error deleting {file_name}: {e}")

        tor_data_dirs = []
        for item in os.listdir():
            if os.path.isdir(item) and (item.startswith("tor_data_") or item == "tor_data"):
                creation_time = os.path.getctime(item)
                tor_data_dirs.append((item, creation_time))

        tor_data_dirs.sort(key=lambda x: x[1], reverse=True)

        if len(tor_data_dirs) > max_dirs_to_keep:
            for dir_name, _ in tor_data_dirs[max_dirs_to_keep:]:
                print(f"Cleaning up old Tor data directory: {dir_name}")
                try:
                    for root, dirs, files in os.walk(dir_name, topdown=False):
                        for name in files:
                            file_path = os.path.join(root, name)
                            try:
                                if name == 'lock':
                                    temp_path = os.path.join(root, 'tmp')
                                    os.rename(file_path, temp_path)
                                    file_path = temp_path
                                os.remove(file_path)
                            except PermissionError:
                                temp_path = file_path + '.tmp'
                                os.rename(file_path, temp_path)
                                os.remove(temp_path)
                            except Exception as e:
                                print(f"Error deleting file {file_path}: {e}")
                        for name in dirs:
                            dir_path = os.path.join(root, name)
                            try:
                                os.rmdir(dir_path)
                            except Exception as e:
                                print(f"Error deleting dir {dir_path}: {e}")
                    os.rmdir(dir_name)
                except Exception as e:
                    print(f"Error cleaning up {dir_name}: {e}")
    except Exception as e:
        print(f"Error during cleanup: {e}")

def main():
    config = configparser.ConfigParser()
    config.read('config.ini')

    tor_config = config['Tor']
    bridge=config['Bridge']
    cleanup_old_tor_data_dirs()

    import random
    socks_port = random.randint(9152, 9999)
    control_port = random.randint(9152, 9999)
    while control_port == socks_port:
        control_port = random.randint(9152, 9999)

    print(f"Using SOCKS port {socks_port} and Control port {control_port} for this session")

    print("Testing direct internet connection...")
    try:
        response = requests.get("https://www.google.com", timeout=10)
        print(f"Direct connection successful! Status code: {response.status_code}")
    except Exception as e:
        print(f"Direct connection failed: {e}")
        print("This may indicate network connectivity issues")
        return

    tor_process = None
    tor_password = None
    try:
        unique_data_dir = f"tor_data_{int(time.time())}"
        if not os.path.exists(unique_data_dir):
            os.makedirs(unique_data_dir)

        import string
        import subprocess
        tor_password = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(16))

        tor_cmd = os.path.join(os.path.dirname(__file__), tor_config['TorCommand'])


        hashed_password_output = subprocess.check_output(
            [tor_cmd, '--hash-password', tor_password],
            universal_newlines=True
        )

        hashed_password = None
        for line in hashed_password_output.splitlines():
            if line.startswith('16:'):
                hashed_password = line.strip()
                break

        if not hashed_password:
            print("Failed to generate hashed password")
            return

        temp_torrc_path = os.path.join(unique_data_dir, 'torrc')
        with open(temp_torrc_path, 'w') as f:
            f.write(f"SocksPort {socks_port}\n")
            f.write(f"ControlPort {control_port}\n")
            f.write(f"DataDirectory {os.path.abspath(unique_data_dir)}\n")
            f.write(f"GeoIPFile {os.path.abspath(os.path.join(os.path.dirname(__file__), tor_config['GeoIPFile']))}\n")
            f.write(f"GeoIPv6File {os.path.abspath(os.path.join(os.path.dirname(__file__), tor_config['GeoIPv6File']))}\n")
            f.write(f"HashedControlPassword {hashed_password}\n")
            if bridge['UseBridges'].lower() == "true":
                f.write("UseBridges 1\n")
                ctp=bridge['ClientTransportPlugin']
                ctp_path=os.path.abspath(os.path.join(os.path.dirname(__file__), ctp))
                if not os.path.exists(ctp_path):
                    print(f"ClientTransportPlugin path does not exist: {ctp_path}")
                    return
                f.write(f"ClientTransportPlugin obfs4 exec {ctp_path}\n")
                bfile=os.path.abspath(os.path.join(os.path.dirname(__file__), 'bridge.txt'))
                with open(bfile, 'r') as bf:
                    brid = bf.readlines()
                if not os.path.exists(bfile):
                    print(f"Bridge file 'bridge.txt' not found in {bfile}")
                    return
                for line in brid:
                    line=line.strip()
                    f.write(f"Bridge {line}\n")

        print(f"Starting Tor on SOCKS port {socks_port} and Control port {control_port}...")

        tor_process = subprocess.Popen(
            [tor_cmd, '-f', temp_torrc_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )

        print("Waiting for Tor to be fully ready...")
        
        import threading
        import queue

        output_queue = queue.Queue()

        def read_output():
            for line in iter(tor_process.stdout.readline, ''):
                output_queue.put(line)
                print(f"Tor: {line.strip()}")
                if "Bootstrapped 100%" in line:
                    output_queue.put("TOR_READY")
                    break
            tor_process.stdout.close()

        read_output()

        tor_ready = False
        start_time = time.time()
        timeout = 60

        while time.time() - start_time < timeout:
            try:
                line = output_queue.get(timeout=0.1)
                if line == "TOR_READY":
                    tor_ready = True
                    break
            except queue.Empty:
                pass

            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex(('127.0.0.1', control_port))
                sock.close()

                if result == 0:
                    print("Tor control port is now available")
                    tor_ready = True
                    break
            except:
                pass

            time.sleep(1)

        if not tor_ready:
            print("Timed out waiting for Tor to be ready")
            if tor_process:
                tor_process.kill()
            return

        with Controller.from_port(port=control_port) as controller:
            try:
                controller.authenticate(password=tor_password)
                guards = controller.get_info("entry-guards")
                print("Successfully authenticated to Tor control port with generated password")
            except Exception as auth_error:
                print(f"Password authentication failed: {auth_error}")
                print("Script will terminate")
                if tor_process:
                    tor_process.kill()
                return

            proxy_host = '127.0.0.1'
            proxy_url = f'socks5h://{proxy_host}:{socks_port}'

            session = requests.session()
            session.proxies = {
                'http': proxy_url,
                'https': proxy_url
            }

            print(f"Using proxy: {proxy_url}")

            test_targets = [
                ("check.torproject.org", 443),
                ("api.ipify.org", 443),
                ("httpbin.org", 443),
                ("www.google.com", 443)
            ]

            connection_successful = False
            time.sleep(10)
            for target_host, target_port in test_targets:
                
                if test_socks_connection(proxy_host, socks_port, target_host, target_port):
                    connection_successful = True
                    break
            
            if not connection_successful:
                print("WARNING: Could not establish any SOCKS connections through Tor")
                print("This may indicate a network or firewall issue")
                print("Script will terminate")
                if tor_process:
                    tor_process.kill()
                return

            print("Getting initial IP address...")
            initial_ip = get_current_ip(session)
            print(f"Initial IP: {initial_ip}")

            try:
                newnym_delay = int(config['App']['NewNymDelay'])
            except (KeyError, ValueError):
                newnym_delay = 30

            print(f"IP will change every {newnym_delay} seconds. Press Ctrl+C to exit.")
            from sel import sel
            t=threading.Thread(target=sel,args=(proxy_host,socks_port))
            t.start()

            try:
                while True:
                    time.sleep(newnym_delay)
                    print("\nChanging IP address...")

                    controller.signal(Signal.NEWNYM)
                    print("New identity requested")

                    time.sleep(5)

                    new_ip = get_current_ip(session)
                    print(f"New IP: {new_ip} and guard: {guards}")
            except KeyboardInterrupt:
                print("\nExiting...")
                t.join()
            except Exception as e:
                print(f"\nError: {e}")
            finally:
                print("Cleaning up...")
                session.close()

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if tor_process:
            print("Terminating Tor process...")
            try:
                tor_process.kill()
                print("Tor process terminated")
            except Exception as e:
                print(f"Error terminating Tor process: {e}")
        else:
            print("Script terminated without starting Tor.")

if __name__ == "__main__":
    main()