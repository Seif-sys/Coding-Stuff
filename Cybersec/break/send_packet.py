import argparse
import random
import socket
import struct
import logging
import sys


# Set up logging for better output control
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_local_ip():
    """
    Gets the local IP address of the machine.
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
        return local_ip
    except Exception as e:
        logging.error(f"Error determining local IP: {e}")
        return None
    

def calculate_checksum(segment):
    """
    Calculates the checksum for a segment.
    """
    if len(segment) % 2 != 0:
        segment += b'\x00'

    checksum = 0
    for i in range(0, len(segment), 2):
        word = segment[i] << 8 | segment[i+1]
        checksum += word
        checksum = (checksum & 0xFFFF) + (checksum >> 16)
    return ~checksum & 0xFFFF


def create_ip_header(source_ip, dest_ip):
    ip_version = 4
    header_length = 5  # IP header is 20 bytes (5x4)
    type_of_service = 0
    total_length = 40
    identification = random.randint(0, 65535)
    flags_offset = 0
    ttl = 64
    protocol = socket.IPPROTO_TCP
    checksum = 0

    try:
        source_ip = socket.inet_aton(source_ip)
        dest_ip = socket.inet_aton(dest_ip)
    except socket.error as e:
        raise ValueError(f"Invalid IP address: {e}")

    ip_header = struct.pack(
        '!BBHHHBBH4s4s',
        (ip_version << 4) + header_length, type_of_service, total_length,
        identification, flags_offset, ttl, protocol,
        checksum, source_ip, dest_ip
    )
    checksum = calculate_checksum(ip_header)
    ip_header = struct.pack(
        '!BBHHHBBH4s4s',
        (ip_version << 4) + header_length, type_of_service, total_length,
        identification, flags_offset, ttl, protocol,
        checksum, source_ip, dest_ip
    )
    return ip_header

def create_tcp_header(source_ip, dest_ip, source_port, dest_port, flags):
    """
    Creates the TCP header for the packet.
    """
    sequence = random.randint(0, 4294967295)
    ack = 0
    do = 5
    reserved = 0  
    window = 5840  
    checksum = 0  
    urgent_pointer = 0

    offset_res_flags = (do << 12) + (reserved << 9) + flags

    tcp_header = struct.pack(
        '!HHLLBBHHH',
        source_port, dest_port, sequence, ack, (do << 4), flags,
        window, checksum, urgent_pointer
    )

    pseudo_header = struct.pack(
        '!4s4sBBH',
        socket.inet_aton(source_ip), socket.inet_aton(dest_ip),
        0, socket.IPPROTO_TCP, len(tcp_header)
    )

    checksum = calculate_checksum(pseudo_header + tcp_header)

    tcp_header = struct.pack(
        '!HHLLBBHHH',
        source_port, dest_port, sequence, ack, (do << 4), flags,
        window, checksum, urgent_pointer
    )

    return tcp_header


def send_packet(dest_ip, dest_port, packet_type):
    """
    Sends a custom TCP packet.
    """
    try:
        raw_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
    except PermissionError:
        logging.error("You need to run this program as root/admin.")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Error creating raw socket: {e}")
        sys.exit(1)

    source_ip = get_local_ip()
    if not source_ip:
        logging.error("Unable to determine local IP. Exiting.")
        sys.exit(1)

    source_port = random.randint(20000, 65535)

    flags = {
        'syn': 0x02,
        'xmas': 0x29,
        'fin': 0x01,
        'null': 0x00
    }.get(packet_type, 0x00)

    try:
        ip_header = create_ip_header(source_ip, dest_ip)
        tcp_header = create_tcp_header(source_ip, dest_ip, source_port, dest_port, flags)
        packet = ip_header + tcp_header
    except ValueError as e:
        logging.error(e)
        sys.exit(1)

    logging.info(f"send_packet(dest_ip={dest_ip}, dest_port={dest_port}, packet_type={packet_type})")

    try:
        raw_socket.sendto(packet, (dest_ip, 0))
    except Exception as e:
        logging.error(f"Error sending packet: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Send custom TCP packets with raw sockets.",
        usage="%(prog)s [-h] (--syn | --xmas | --fin | --null) IP/DOMAIN PORT"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--syn", action="store_true", help="Send an SYN package")
    group.add_argument("--xmas", action="store_true", help="Send a XMAS package")
    group.add_argument("--fin", action="store_true", help="Send a FIN package")
    group.add_argument("--null", action="store_true", help="Send a NULL packet")
    parser.add_argument("IP/DOMAIN", help="Target IP address or domain")
    parser.add_argument("PORT", type=int, help="Target port")

    args = parser.parse_args()

    if not (1 <= args.port <= 65535):
        logging.error("Port must be in the range 1-65535.")
        sys.exit(1)

    dest_ip = args.ip
    dest_port = args.port

    packet_type = "syn" if args.syn else "xmas" if args.xmas else "fin" if args.fin else "null"
    send_packet(dest_ip, dest_port, packet_type)


if __name__ == "__main__":
    main()

