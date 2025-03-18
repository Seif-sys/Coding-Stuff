import socket
import argparse
import ssl
import re
import sys
from threading import Thread
import traceback

def is_port_in_use(port):
    """
    Check if a port is in use by attempting to bind a socket to it.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as test_socket:
        try:
            test_socket.bind(("127.0.0.1", port))
            return False
        except socket.error as e:
            print(f"Port {port} is in use: {e}")
            return True

def handle_client(client_conn, server_conn, output):
    try:
        while True:
            # Receive from client and forward to server
            client_data = client_conn.recv(4096)
            if not client_data:
                break

            try:
                message = client_data.decode(errors="ignore")
                filtered = re.sub(r'\b\d{4}\b', '', message)
                if output:
                    output.write(filtered + "\n")
                else:
                    print(filtered)
            except Exception:
                pass  # In case of decoding issues

            server_conn.sendall(client_data)

            # Receive from server and forward to client
            server_data = server_conn.recv(4096)
            if not server_data:
                break

            try:
                message = server_data.decode(errors="ignore")
                filtered = re.sub(r'\b\d{4}\b', '', message)
                if output:
                    output.write(filtered + "\n")
                else:
                    print(filtered)
            except Exception:
                pass

            client_conn.sendall(server_data)

    except Exception as e:
        print(f"Error in client handler: {e}")
        traceback.print_exc()
    finally:
        client_conn.close()
        server_conn.close()

def mitm_setup(ip, port, output_file=None):
    output = None
    try:
        if is_port_in_use(port):
            print(f"Warning: Port {port} appears to be in use.")

        if output_file:
            output = open(output_file, 'w')

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listener:
            listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            listener.bind(("0.0.0.0", port))
            listener.listen(5)
            print(f"[+] Listening on port {port}...")

            while True:
                try:
                    client_sock, client_addr = listener.accept()
                    print(f"[+] Accepted connection from {client_addr}")

                    # SSL context for client connection (your fake server)
                    server_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
                    server_context.load_cert_chain(certfile="server_cert.pem", keyfile="server_key.pem")
                    client_conn_ssl = server_context.wrap_socket(client_sock, server_side=True)

                    # SSL context for connecting to real server (you act as client)
                    client_context = ssl.create_default_context()
                    raw_server_conn = socket.create_connection((ip, port))
                    server_conn_ssl = client_context.wrap_socket(raw_server_conn, server_hostname=ip)

                    thread = Thread(target=handle_client, args=(client_conn_ssl, server_conn_ssl, output), daemon=True)
                    thread.start()

                except ssl.SSLError as ssl_error:
                    print(f"SSL error: {ssl_error}")
                    traceback.print_exc()
                except Exception as e:
                    print(f"Connection handling error: {e}")
                    traceback.print_exc()

    except Exception as e:
        print(f"[!] Setup error: {e}")
        traceback.print_exc()
    finally:
        if output:
            output.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Simple SSL MITM Proxy Tool")
    parser.add_argument("ip", help="Target server IP/domain")
    parser.add_argument("port", type=int, help="Target server port")
    parser.add_argument("--out", help="Output file for logs (default: stdout)", default=None)
    args = parser.parse_args()

    mitm_setup(args.ip, args.port, args.out)
