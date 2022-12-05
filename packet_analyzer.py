import socket
import struct
import sys


def main():
    conn = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.ntohs(3))
    while True:
        raw_data, address = conn.recvfrom(sys.maxsize)
        dest_mac, src_mac, ethernet_proto, data = ethernet_frame(raw_data)
        print(f'Dest:{dest_mac}, Src{src_mac},Ptotocol{ethernet_proto}')

        # IPv4 is 8
        if ethernet_proto == 8:
            (ver, header_len, ttl, proto, src, tgt, data) = analyze_ipv4_packet(data)
            print(
                f'IPv4 packet:\n\t Version:{ver},Header Length:{header_len},TTL:{ttl}\n\t\t Protocol:{proto},Soruce:{src},Target{tgt}')
            # protocol number of icmp
            if proto == 1:
                icmp_type, code, checksum, data = icmp_packet(data)
            elif proto == 6:
                (
                    src_port, dest_port, seq, ack, urg_flag, ack_flag, psh_flag, rst_flag, syn_flag,
                    fin_flag) = tcp_packet(
                    data)
                print(
                    f'TCP packet:\n\t Source Port:{src_port},Destination Port{dest_port}\n\t\t Sequence:{seq},Acknowledgement:{ack}\n\t\t Flags:\n\t\t\t Urg:{urg_flag},Ack:{ack_flag},psh:{psh_flag},Rst:{rst_flag},Syn:{syn_flag},Fin:{fin_flag}')
                # tcp port 25 is smtop
                if dest_port == 25:
                    smtp_type, code, checksum = smtp_packet(data)
                    print(f'SMTP packet:\n\t smtp type:{smtp_type},code:{code},checksum:{checksum}')
            elif proto == 17:
                src_port, dest_port, len, data = udp_packet(data)
                print(f'UDP Packet:\n\t Source Port:{src_port},Dest Port:{dest_port},Length:{len}')
                if dest_port == 25:
                    smtp_type, code, checksum = smtp_packet(data)
                    print(f'SMTP packet:\n\t smtp type:{smtp_type},code:{code},checksum:{checksum}')
            else:
                print(f'Data:\n{data}')


# upacking the ehternet frame for sniffing
def ethernet_frame(data):
    dest_mac, src_mac, proto = struct.upack('!6s 6s H', data[:14])
    return get_mac_address(dest_mac, get_mac_address(src_mac), socket.htons(proto), data[:14])


# converting raw mac address into human readable mac of the form 00:00:7F:00:69:AF
def get_mac_address(bytes_addr):
    b_str = map('{:02x}', format, bytes_addr)
    print("Source MAC:" + ':'.join(b_str).upper())
    return ':'.join(b_str).upper()


# converting raw ipv4 address into human readable ipv4 address
def get_ip_addr(src_addr):
    print("IPv4 address:" + '.'.join(map(str, src_addr)))
    return '.'.join(map(str, src_addr))


def smtp_packet(data):
    smtp_type, code, checksum = struct.unpack('! B B H', data[:4])
    return smtp_type, code, checksum, data[4:]


def icmp_packet(data):
    icmp_type, code, checksum = struct.unpack('! B B H', data[:4])
    return icmp_type, code, checksum, data[4:]


def tcp_packet(data):
    (src_port, dest_port, seq, ack, offset_flags_reversed) = struct.unpack('! H H L L H', data[:14])
    offset = (offset_flags_reversed >> 12) * 4
    flag_urg = (offset_flags_reversed & 32) >> 5
    flag_ack = (offset_flags_reversed & 16) >> 4
    flag_psh = (offset_flags_reversed & 8) >> 3
    flag_rst = (offset_flags_reversed & 4) >> 2
    flag_syn = (offset_flags_reversed & 2) >> 1
    flag_fin = (offset_flags_reversed & 1)
    return src_port, dest_port, seq, ack, flag_urg, flag_ack, flag_psh, flag_rst, flag_syn, flag_fin


def udp_packet(data):
    (src_port, dest_port, len) = struct.unpack('! H H 2x H', data[:8])
    return src_port, dest_port, len, data[8:]


# analyzing ipv4 packet header
def analyze_ipv4_packet(data):
    ver_header_len = data[0]
    ver = ver_header_len >> 4
    header_len = (ver_header_len & 15) * 4
    ttl, proto, src, dest = struct.unpack('! 8x B B 2x 4s 4s', data[:20])
    return ver, header_len, ttl, proto, get_ip_addr(src), get_ip_addr(dest), data[header_len:]


main()
