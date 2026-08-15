import socket
import json

class Communication:
    
    def __init__(self, host="0.0.0.0", port=25001):
        # 初始化服务器地址和端口
        self.host = host
        self.port = port
        # 初始化socket对象
        self.server_socket = None
        self.client_socket = None

    def start_server(self):
    # 创建TCP服务器socket
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # 加入端口复用，防止端口 TIME_WAIT 状态无法复用
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        try:
        # 绑定地址和端口
            self.server_socket.bind((self.host, self.port))
        except OSError as e:
            print(f"❌ 绑定端口 {self.port} 失败：{e}")
            print("👉 可能是另一个程序正在使用该端口，或者之前未正常关闭")
            exit(1)

    # 开始监听连接
        self.server_socket.listen(1)
        print("等待客户端连接...")

        try:
            self.client_socket, _ = self.server_socket.accept()
            print("✅ 客户端连接成功！")
        except Exception as e:
            print("❌ 接受客户端连接失败：", e)
            self.server_socket.close()

    def send_point_info(self, hand_type, i, xPos, yPos):
        # 如果没有客户端连接，直接返回
        if not self.client_socket:
            return
        

        # 创建包含手部信息的字典
        npc_info = {
            "hand": hand_type,  # 手部类型（左手/右手）
            "Id": i,            # 关键点编号
            "xPos": xPos , 
            "yPos": yPos ,   
           
        }
        try:
            # 将字典转换为JSON字符串并添加换行符
            json_data = json.dumps(npc_info) + '\n'
            # 发送数据到客户端
            self.client_socket.sendall(json_data.encode('utf-8'))
            # 打印发送的信息
            #direction_text = "向上" if direction > 0 else "向下"
            #print(f"发送: {hand_type} hand {i}: X {xPos} :Y{yPos}")

        except Exception as e:
            print("发送失败:", e)

    def close(self):
        # 关闭客户端连接
        if self.client_socket:
            self.client_socket.close()
        # 关闭服务器socket
        if self.server_socket:
            self.server_socket.close() 