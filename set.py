import socketio

# Tạo một client Socket.IO
sio = socketio.Client()

# Hàm xử lý khi kết nối thành công
@sio.event
def connect():
    print("Kết nối thành công đến server!")

# Hàm xử lý khi mất kết nối
@sio.event
def disconnect():
    print("Mất kết nối với server!")

# Địa chỉ server cần kiểm tra
server_url = "https://23021510.pythonanywhere.com/"  # Thay đổi thành URL server của bạn

# Kết nối đến server
try:
    print(f"Đang kết nối đến {server_url}...")
    sio.connect(server_url)
    print("Kết nối kiểm tra thành công!")
    sio.disconnect()  # Đóng kết nối sau khi kiểm tra xong
except Exception as e:
    print(f"Không thể kết nối đến server: {e}")
