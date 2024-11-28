# Sử dụng Python image
FROM python:3.10-slim

# Đặt thư mục làm việc
WORKDIR /app

# Copy toàn bộ mã nguồn vào container
COPY . .

# Cài đặt các thư viện từ requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Mở cổng 8080
EXPOSE 8080

# Chạy ứng dụng Flask
CMD ["python", "app.py"]
