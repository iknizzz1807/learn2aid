### Chạy dự án nếu dùng docker-compose

- Tải Docker desktop nếu dùng Windows, nếu Linux thì cài Docker Engine
- Mở Docker Desktop (nhớ mở, nếu không sẽ không chạy được)

#### Docker Compose với Volume Mapping cho Development

1. **Khởi động lần đầu tiên hoặc thêm thư viện vào requirements.txt trong ai service**:

```bash
docker-compose up --build
```

2. **Khởi động thông thường** (sau các lần đầu):

```bash
docker-compose up
```

3. **Chạy ngầm**:

```bash
docker-compose up -d
```

4. **Xem logs**:

```bash
docker-compose logs -f
```

5. **Khởi động lại một service cụ thể**:

```bash
docker-compose restart ai-service
```

### Debug và Development

- **AI Service**: Code Python sẽ tự động reload với flag `--reload` của uvicorn
- **Go Backend**: Cần restart service khi có thay đổi code:
  ```bash
  docker-compose restart go-backend
  ```

### Kết thúc dự án

```bash
docker-compose down
```

## Lưu ý quan trọng

1. **Golang Hot Reload**: Để có hot reload với Go, cập nhật Dockerfile của backend để sử dụng công cụ như `air` hoặc `CompileDaemon` (đang không dùng).

2. **Container đang chạy**: Nếu thay đổi Dockerfile, cần chạy `docker-compose up --build` để áp dụng thay đổi.

3. **Phân biệt môi trường**:

   - Development: Sử dụng volume mapping như trên
   - Production: Không dùng volume mapping và `--reload` hoặc hot reload

4. **Vấn đề permission**: Trên Linux, có thể gặp vấn đề quyền truy cập với volume mapping. Kiểm tra quyền của thư mục và owner của files.

5. **Đối với AI Service**: Khi cài đặt thêm thư viện Python mới, cần rebuild lại container:
   ```bash
   docker-compose up --build ai-service
   ```

### Nếu không dùng Docker

- Chạy từng service một
- Cách chạy các service cụ thể đã được viết trong các file README.md trong các folder tương ứng
- Nhớ cài đặt đầy đủ theo yêu cầu
