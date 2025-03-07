- Cài đặt thư viện
  - Thư viện Gin dùng để làm service API
  - Resty làm http client, hỗ trợ API request, hỗ trợ JSON, middleware và tích hợp tốt với API bên ngoài như AI service của FastAPI

```bash
go get -u github.com/gin-gonic/gin
go get -u github.com/go-resty/resty/v2

```

- Chạy service:

```bash
go run ./backend/main.go
```
