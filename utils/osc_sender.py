from pythonosc.udp_client import SimpleUDPClient

class OSCSender:
    def __init__(self, ip="127.0.0.1", port=7001):
        self.client = SimpleUDPClient(ip, port)

    def send_position(self, x, y):
        self.client.send_message("/position", [float(x), float(y)])
