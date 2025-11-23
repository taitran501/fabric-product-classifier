# Cách tạo file trực tiếp trên GPU server (nếu SCP không work)

Nếu gặp lỗi khi upload file bằng SCP, bạn có thể tạo file trực tiếp trên server:

## Bước 1: SSH vào server

```bash
ssh -p 54754 root@143.55.45.86
```

## Bước 2: Tạo file api_server.py

```bash
nano /root/api_server.py
```

Sau đó copy toàn bộ nội dung từ file `api_server.py` (trong repo) và paste vào, sau đó:
- Nhấn `Ctrl + O` để save
- Nhấn `Enter` để confirm
- Nhấn `Ctrl + X` để exit

## Bước 3: Tạo file api_requirements.txt

```bash
nano /root/api_requirements.txt
```

Copy nội dung:
```
flask>=2.3.0
flask-cors>=4.0.0
transformers>=4.30.0
torch>=2.0.0
sentencepiece>=0.1.99
tokenizers>=0.13.0
huggingface-hub>=0.16.0
```

Save và exit (Ctrl+O, Enter, Ctrl+X)

## Bước 4: Cài đặt dependencies

```bash
cd /root
pip3 install -r api_requirements.txt
```

## Bước 5: Chạy API server

```bash
# Chạy trong screen để giữ chạy khi disconnect
screen -S api_server
python3 api_server.py
```

Nhấn `Ctrl+A` rồi `D` để detach khỏi screen.

## Kiểm tra API

```bash
# Health check
curl http://localhost:5000/health

# Test prediction
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{"texts": ["cotton fabric", "polyester yarn"]}'
```

