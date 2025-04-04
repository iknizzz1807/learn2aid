### Nếu không dùng docker-compose thì đọc

- Cài đặt thư viện cần thiết

```bash
pip install -r requirements.txt

```

- Nếu muốn thêm một thư viện nào đó vào dự án, thêm trong requirements.txt

- Chạy service riêng lẻ bằng lệnh sau:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```
