import socket
import struct


class Faber:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.connect()
        
        self.req_prefix = [0xa1, 0xa2, 0xa3, 0xa4, 0x00, 0xfa, 0x00, 0x02]
        self.req_command_prefix = [0x00, 0x00, 0x7d, 0xed, 0x00, 0x00, 0x10, 0x40, 0xff, 0xff, 0x00]
        self.req_name_prefix =  [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x20, 0x00, 0x00, 0x00]
        self.req_status_prefix = [0x00, 0x00, 0x7d, 0xed, 0x00, 0x00, 0x10, 0x30, 0x00, 0x00, 0x00]
        self.req_suffix = [0x00, 0xfa, 0xfb, 0xfc, 0xfd]

    def connect(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error:
            print('Failed to create socket')

        try:
            self.socket.connect((self.host, self.port))
        except socket.error:
            print('Failed to connect to host')

    def send(self, prefix, command, length=29):
        data = struct.pack('29B', *self.req_prefix, *prefix, *command, *self.req_suffix)
        try:
            self.socket.sendall(data)
        except socket.error:
            print('Failed to send data')
            self.close()
            self.connect()
            return b''
        res = b''
        while len(res) < (length):
            try:
                res += self.socket.recv(min(length, length-len(res)))
            except socket.error:
                print('Failed to receive data')
                self.close()
                self.connect()
                return b''
        res = struct.unpack(f'!{length}B', res)
        return res

    def close(self):
        self.socket.close()

    def set_temp(self, temp):
        temp = int(temp*2)
        command = [0x22, 0x00, 0x00, 0x00, temp]
        return self.send(self.req_command_prefix, command) != b''

    def set_flame_wide(self):
        command = [0x06, 0x00, 0x00, 0x00, 0x00]
        return self.send(self.req_command_prefix, command) != b''

    def set_flame_narrow(self):
        command = [0x05, 0x00, 0x00, 0x00, 0x00]
        return self.send(self.req_command_prefix, command) != b''

    def set_flame_height(self, height):
        command = [0x09, 0x00, 0x00, 0x00, int(height)]
        return self.send(self.req_command_prefix, command) != b''
    
    def set_off(self):
        command = [0x01, 0x00, 0x00, 0x00, 0x00]
        return self.send(self.req_command_prefix, command) != b''
    
    def set_on(self):
        command = [0x02, 0x00, 0x00, 0x00, 0x00]
        return self.send(self.req_command_prefix, command) != b''

    def get_status(self):
        command = [0x00, 0x00, 0x00, 0x00, 0x00]
        data = self.send(self.req_status_prefix, command, 61)
        set_temp = float(data[33])/2
        current_temp = float(data[36]*256 + data[37])/10
        flame_height = int(data[31])
        flame_width = int(data[32])
        mode = int(data[27])
        return (set_temp, current_temp, flame_height, flame_width, mode)




if __name__ == "__main__":

    HOST = "192.168.1.18"
    PORT = 58779

    temp = 26.5
    fireplace = Faber(HOST, PORT)
    set_temp, current_temp, flame_height, flame_width, mode = fireplace.get_status()
    #fireplace.set_on()

    print("Set temp: ", set_temp)
    print("Current temp: ", current_temp)
    print("Flame height: ", flame_height)
    print("Flame width: ", flame_width)
    print("Mode: ", mode)