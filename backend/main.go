package main

import (
	"log"
	"os"

	"github.com/gin-gonic/gin"
	"github.com/iknizzz1807/learn2aid/api"
	"github.com/iknizzz1807/learn2aid/config"
	"github.com/iknizzz1807/learn2aid/services"
)

func main() {
	// Set Gin mode based on environment
	mode := os.Getenv("GIN_MODE")
	if mode == "" {
		mode = "debug" // Default to debug mode
	}
	gin.SetMode(mode)

	// Initialize configuration
	cfg := config.NewConfig()

	// Initialize services
	firebaseService := services.NewFirebaseService(cfg.FirebaseApp)
	aiService := services.NewAIService(cfg.AIServiceURL)

	// Check AI service health
	log.Println("Checking AI service health...")
	if err := aiService.HealthCheck(); err != nil {
		log.Printf("Warning: AI service health check failed: %v", err)
	} else {
		log.Println("AI service is healthy")
	}

	// Setup router with all the routes
	r := api.SetupRouter(aiService, firebaseService)

	// Get port from environment or use default
	port := os.Getenv("PORT")
	if port == "" {
		port = "8080" // Default port
	}

	log.Printf("Starting server on port %s in %s mode", port, mode)
	r.Run(":" + port)
}
