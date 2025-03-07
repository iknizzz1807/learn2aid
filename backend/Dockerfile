FROM golang:1.24

WORKDIR /app

COPY . .

RUN go mod tidy && go build -o app

CMD ["./app"]