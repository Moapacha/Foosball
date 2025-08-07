from pythonosc.udp_client import SimpleUDPClient

class OSCSender:
    def __init__(self, ip="127.0.0.1", port=11111, position_ip="127.0.0.1", position_port=11112):
        self.client = SimpleUDPClient(ip, port)
        self.position_client = SimpleUDPClient(position_ip, position_port)

    def send_position(self, x, y):
        """发送位置估计到独立端口"""
        self.position_client.send_message("/position", [float(x), float(y)])

    def send_full_status(self, rms_values, x, y, goal_detection, bpm):
        """
        发送6个通道RMS、定位x, y值、进球检测和BPM，OSC地址为/foosball_status
        :param rms_values: 长度为6的RMS数组（前6个通道）
        :param x: 预测x
        :param y: 预测y
        :param goal_detection: [左球门进球(0/1), 右球门进球(0/1)]
        :param bpm: 当前BPM值
        """
        msg = list(map(float, rms_values)) + [float(x), float(y)] + list(map(float, goal_detection)) + [float(bpm)]
        self.client.send_message("/foosball_status", msg)
