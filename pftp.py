import socket
from protocol import protocol_pb2
import math

class Pftp:
    def __init__(self, address: str, port: int) -> None:
        self.address = address
        self.port = port
        self.sock = None

    def connect(self) -> None:
        print("Trying to connect to Polar FTP server at", socket.inet_ntop(socket.AF_INET6, self.address), "on port", self.port)
        self.sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        server_address = (socket.inet_ntop(socket.AF_INET6, self.address), self.port)
        self.sock.connect(server_address)
        data = self._read()
        if(data.decode('ascii').startswith("Polar FTP server")):
            print(data.decode('ascii'))
            return
        raise Exception("Not a Polar FTP server")

    def disconnect(self)  -> None:
        self.sock.close()

    def get_device_info(self) -> None:
        message = protocol_pb2.File()
        message.unkown_1 = 0
        message.path = "/DEVICE.BPB"
        self.sock.sendall(self._frame_length(message.ByteSize() + 2) + self._header_length(message.ByteSize())  + message.SerializeToString())
        data = self._read()

        message = protocol_pb2.DeviceInfo()
        message.ParseFromString(data[2:-2])

        print(f"Model: {message.model_name}")
        print(f"Device ID: {message.device_id}")
        print(f"Platform version: {message.platform_version.major}.{message.platform_version.minor}.{message.platform_version.patch}")
        print(f"Device version: {message.device_version.major}.{message.device_version.minor}.{message.device_version.patch}")
        print(f"System id: {':'.join(message.system_id[i:i + 2] for i in range(0, len(message.system_id), 2))}")

    def start_sync(self) -> None:
        self.sock.sendall(b'\x06\x00\x00')

    def stop_sync(self) -> None:
        self.sock.sendall(b'\x0c\x00\x01\x80\x05')
        self.sock.sendall(b'\x0c\x00\x01\x80\x08')
        
    def upload_map(self, map: str) -> None:
        with open(map, 'rb') as f:

            frame_lenght = 16383
            header_content = protocol_pb2.File()
            header_content.unkown_1 = 1
            header_content.path = "/U/0/MAP/0/MAPDATA.MAP"
            header = self._frame_length(frame_lenght) + self._header_length(header_content.ByteSize()) + header_content.SerializeToString()

            file_size = len(f.read())
            f.seek(0)

            chunk_count = math.ceil((file_size + len(header) - 2) / (frame_lenght)) # -2 for the header
            
            for i in range(chunk_count):

                data = f.read(frame_lenght - len(header) + 2)

                if i == chunk_count - 1:
                    header = self._frame_length(len(data), True)

                self.sock.sendall(header + data)

                if i == 0:
                    header = self._frame_length(frame_lenght, True)

                response = self._read()


                if response == b'\x00\x02\x00\x00':
                    if i % 10 == 0:
                        progress = ((i + 1) / chunk_count) * 100
                        print(f"Uploading {progress:.0f}%")
                elif response == b'\x00\x00\x00\x00':
                    progress = ((i + 1) / chunk_count) * 100
                    print(f"Uploading {progress:.0f}%")
                    print("Map upload complete")
                    break
                else:
                    print("Error sending chunk!")
                    print("response:")
                    print(" ".join(hex(n) for n in response))
                    break

            return
            

    def _read(self) -> None:
        data = self.sock.recv(1024)
        return data

    def _frame_length(self, lenght: int, flag: bool = False) -> bytes:
        var3 = lenght << 2 | 0
        var2 = (var3 >> 8) & 255
        var1 = var3 & 255
        return bytes(bytearray([var1 + flag, var2]))
    
    def _header_length(self, lenght: int) -> bytes:
        return lenght.to_bytes(2, byteorder='little')