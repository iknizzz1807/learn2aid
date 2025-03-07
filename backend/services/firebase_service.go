package services

import (
	"context"
	"log"

	firebase "firebase.google.com/go/v4"
	"firebase.google.com/go/v4/auth"
)

// Phía frontend: Cần thêm code để:

// Đăng nhập với Google thông qua Firebase Auth
// Lấy ID token
// Gửi token trong header Authorization
// Xử lý refresh token khi nhận header X-Refresh-Token

type FirebaseService struct {
	AuthClient *auth.Client
}

func NewFirebaseService(app *firebase.App) *FirebaseService {
	authClient, err := app.Auth(context.Background())
	if err != nil {
		log.Fatalf("Error getting Auth client: %v", err)
	}

	return &FirebaseService{
		AuthClient: authClient,
	}
}

// VerifyToken validates a Firebase ID token
func (fs *FirebaseService) VerifyToken(idToken string) (*auth.Token, error) {
	ctx := context.Background()
	token, err := fs.AuthClient.VerifyIDToken(ctx, idToken)
	if err != nil {
		return nil, err
	}
	return token, nil
}

// GetUserByID gets user information by ID
func (fs *FirebaseService) GetUserByID(uid string) (*auth.UserRecord, error) {
	ctx := context.Background()
	return fs.AuthClient.GetUser(ctx, uid)
}
