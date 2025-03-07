- Cài đặt thư viện
  - Thư viện Gin dùng để làm service API
  - Resty làm http client, hỗ trợ API request, hỗ trợ JSON, middleware và tích hợp tốt với API bên ngoài như AI service của FastAPI

```bash
go get -u github.com/gin-gonic/gin
go get -u github.com/go-resty/resty/v2
go get firebase.google.com/go/v4
go get google.golang.org/api/option
go get go.opentelemetry.io/otel/internal/global@v1.34.0

```

- Chạy service:

```bash
go run ./backend/main.go
```
