package config

import (
	"context"
	"log"
	"os"

	firebase "firebase.google.com/go/v4"
	"google.golang.org/api/option"
)

type Config struct {
	FirebaseApp  *firebase.App
	AIServiceURL string
}

func NewConfig() *Config {
	credentialsPath := os.Getenv("FIREBASE_CREDENTIALS")
	if credentialsPath == "" {
		credentialsPath = "service-account.json"
	}

	opt := option.WithCredentialsFile(credentialsPath)
	app, err := firebase.NewApp(context.Background(), nil, opt)
	if err != nil {
		log.Fatalf("Error initializing Firebase: %v", err)
	}

	aiServiceURL := os.Getenv("AI_SERVICE_URL")
	if aiServiceURL == "" {
		aiServiceURL = "http://ai-service:8000"
	}

	return &Config{
		FirebaseApp:  app,
		AIServiceURL: aiServiceURL,
	}
}

// Client
// const firebaseConfig = {
//     apiKey: "AIzaSyB9Cl_caDnMbkDdtRd7oGlFB11C0wFh7FE",
//     authDomain: "learn2aid.firebaseapp.com",
//     projectId: "learn2aid",
//     storageBucket: "learn2aid.firebasestorage.app",
//     messagingSenderId: "720302589716",
//     appId: "1:720302589716:web:bcd5400adc8d41aa73e401"
//   };
