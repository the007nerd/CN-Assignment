import socket
import requests
import hashlib as hash
import bencodepy as ben
#b'\x95\x8e$\x87\xd2\xdb_A\xf9\xc0V\xbb5\xcfT~\xdf8R\x8f'
def decode_bencode(bencoded_value):
     
    try:
        return ben.Bencode(encoding="utf-8").decode(bencoded_value)
    except Exception as e:
        return ben.decode(bencoded_value)

def get_torrent_info(file_path):
     
    with open(file_path, "rb") as file:
        torrent_data = file.read()
        parsed = decode_bencode(torrent_data)
        tracker_url = parsed[b"announce"].decode("utf-8")
        info = parsed[b"info"]
        length = info[b"length"]
        
        # Bencode the info dictionary
        bencoded_info = ben.encode(info)
        
        # Calculate the SHA-1 hash of the bencoded info dictionary
        info_hash = hash.sha1(bencoded_info).digest()
        
        return tracker_url, info_hash, length

def get_peers(tracker_url, info_hash,length):
    
    #Makes a GET request to the tracker URL to retrieve peers.
    print(info_hash)
    # Use quote_from_bytes to correctly encode the info_hash
    encoded_info_hash = info_hash.hex()
    print(encoded_info_hash)
    params = {
        'info_hash': info_hash,
        'peer_id': b'-PC0001-' + hash.md5().digest()[0:12],  # Random peer ID
        'port': 6881,
        'uploaded': 0,
        'downloaded': 0,
        'left': length,
        'compact': 1,
        'event': 'started'
    }

    response = requests.get(tracker_url, params=params)
    decoded_response = decode_bencode(response.content)
    raw_peers = decoded_response[b"peers"]
    def decode_string(data):
        return data.decode('utf-8') if isinstance(data, bytes) else data
    
    peer_list = []
    for i in range(len(raw_peers)):
        raw_peers[i] = {decode_string(k): decode_string(v) if isinstance(v, bytes) else v for k, v in raw_peers[i].items()}
        peerElem = raw_peers[i]['ip'] + ":" + str(raw_peers[i]['port']) 
        peer_list.append(peerElem)

    return peer_list

def perform_handshake(info_hash, peer_ip, peer_port):
    try:
        print(f"Connecting to Peer Ip {peer_ip} at port {peer_port} ........")
        # Create a socket and connect to the peer
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)  # Set a timeout for socket operations
        sock.connect((peer_ip, int(peer_port)))
        
        # Build handshake message
        protocol_name = b'BitTorrent protocol'
        reserved_bytes = b'\x00' * 8
        peer_id = b'-PY0001-' + b''.join([bytes([i % 256]) for i in range(12)])   
        handshake_msg = bytes([len(protocol_name)]) + protocol_name + reserved_bytes + info_hash + peer_id
        # Send handshake message
        sock.sendall(handshake_msg)
        
        # Receive handshake response
        response = sock.recv(68)   #handshake response is 68 bytes
        if len(response) < 68:
            print("Received an incomplete handshake response.")
            return
        
        # Extract peer id from response
        peer_id_received = response[48:68]  
        
        # Print hexadecimal representation of peer id received
        print("Peer ID:", peer_id_received.hex(),"\n")
        
    except socket.timeout:
        print("Connection timed out. The peer might be unreachable.")
    except socket.error as e:
        print(f"Socket error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        sock.close()

if __name__ == "__main__":
     
    torrent_file = 'ComputerNetworks.torrent'
    tracker_url,info_hash,length = get_torrent_info(torrent_file)
    peer_list = get_peers(tracker_url,info_hash,length)
    raw_peer_list = [peer.split(":") for peer in peer_list]

    for rawPeer in raw_peer_list:
        perform_handshake(info_hash,rawPeer[0],rawPeer[1])

