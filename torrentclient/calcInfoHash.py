import bencodepy as ben
import hashlib as hash

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
        info_hash = hash.sha1(bencoded_info).hexdigest()
        
        return tracker_url, length, info_hash

def main(file_path):
    
    tracker_url, length, info_hash = get_torrent_info(file_path)
    print(f"Tracker URL: {tracker_url}")
    print(f"Length: {length}")
    print(f"Info Hash: {info_hash}")

if __name__ == "__main__":
    file_path = "ComputerNetworks.torrent"   
    main(file_path)
