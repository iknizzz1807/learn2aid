package api

import (
	"net/http"

	"github.com/gin-gonic/gin"
	"github.com/iknizzz1807/learn2aid/services"
)

func SetupRouter(aiService *services.AIService, fbService *services.FirebaseService) *gin.Engine {
	r := gin.Default()

	// r.Use(gin.Recovery())

	r.Use(corsMiddleware())

	// Health check endpoints
	r.GET("/health", HealthCheckHandler())
	r.GET("/ping", func(c *gin.Context) {
		c.JSON(200, gin.H{"message": "pong"})
	})

	// Public routes
	r.GET("/", HomeHandler())

	// API v1 group
	v1 := r.Group("/api/v1")
	{
		// Public API endpoints
		// v1.POST("/register", RegisterHandler(fbService))
		// v1.POST("/login", LoginHandler(fbService))
		v1.GET("/videos", GetVideosHandler(fbService))
		v1.GET("/videos/category/:category", GetVideosByCategoryHandler(fbService))
		v1.GET("/videos/:id", GetVideoByIDHandler(fbService))

		// Quiz public endpoints
		v1.GET("/quizzes", GetQuizzesHandler(fbService))
		v1.GET("/quizzes/category/:category", GetQuizzesByCategoryHandler(fbService))

		// Protected API endpoints
		protected := v1.Group("")
		protected.Use(AuthMiddleware(fbService))
		// Change the order of this middleware to protect routes for every requests
		{
			// Prediction endpoints
			protected.POST("/predict", PredictHandler(aiService, fbService))
			protected.GET("/predictions", GetPredictionsHandler(fbService))

			// User endpoints
			protected.GET("/user", GetUserHandler(fbService))
			protected.PUT("/user", UpdateUserHandler(fbService))

			// Quiz protected endpoints
			protected.GET("/quizzes/:id", GetQuizForUserHandler(fbService))
			protected.POST("/quizzes/:id/start", StartQuizAttemptHandler(fbService))
			protected.POST("/quizzes/:id/submit", SubmitQuizAttemptHandler(fbService))
			protected.GET("/quiz-attempts", GetUserQuizAttemptsHandler(fbService))
		}
	}

	return r
}

func GetVideosHandler(fbService *services.FirebaseService) gin.HandlerFunc {
	return func(c *gin.Context) {
		videos, err := fbService.GetAllFirstAidVideos()
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to fetch videos"})
			return
		}
		c.JSON(http.StatusOK, videos)
	}
}

func GetVideosByCategoryHandler(fbService *services.FirebaseService) gin.HandlerFunc {
	return func(c *gin.Context) {
		category := c.Param("category")
		videos, err := fbService.GetVideosByCategory(category)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to fetch videos"})
			return
		}
		c.JSON(http.StatusOK, videos)
	}
}

func GetVideoByIDHandler(fbService *services.FirebaseService) gin.HandlerFunc {
	return func(c *gin.Context) {
		id := c.Param("id")
		video, err := fbService.GetVideoByID(id)
		if err != nil {
			c.JSON(http.StatusNotFound, gin.H{"error": "Video not found"})
			return
		}
		c.JSON(http.StatusOK, video)
	}
}

// Additional handlers (implement these as needed)
func HomeHandler() gin.HandlerFunc {
	return func(c *gin.Context) {
		c.JSON(200, gin.H{"message": "Welcome to Learn2Aid API"})
	}
}

func HealthCheckHandler() gin.HandlerFunc {
	return func(c *gin.Context) {
		c.JSON(200, gin.H{"status": "ok"})
	}
}

func corsMiddleware() gin.HandlerFunc {
	return func(c *gin.Context) {
		c.Writer.Header().Set("Access-Control-Allow-Origin", "*")
		c.Writer.Header().Set("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
		c.Writer.Header().Set("Access-Control-Allow-Headers", "Origin, Content-Type, Content-Length, Accept-Encoding, X-CSRF-Token, Authorization")

		if c.Request.Method == "OPTIONS" {
			c.AbortWithStatus(204)
			return
		}

		c.Next()
	}
}

// Additional handler placeholders (implement based on your needs)
func RegisterHandler(fbService *services.FirebaseService) gin.HandlerFunc {
	return func(c *gin.Context) {
		// TODO: Implement user registration
		c.JSON(501, gin.H{"error": "Not implemented yet"})
	}
}

func LoginHandler(fbService *services.FirebaseService) gin.HandlerFunc {
	return func(c *gin.Context) {
		// TODO: Implement user login
		c.JSON(501, gin.H{"error": "Not implemented yet"})
	}
}

func GetPredictionsHandler(fbService *services.FirebaseService) gin.HandlerFunc {
	return func(c *gin.Context) {
		// TODO: Implement fetching user predictions
		c.JSON(501, gin.H{"error": "Not implemented yet"})
	}
}

func GetUserHandler(fbService *services.FirebaseService) gin.HandlerFunc {
	return func(c *gin.Context) {
		// TODO: Implement fetching user profile
		c.JSON(501, gin.H{"error": "Not implemented yet"})
	}
}

func UpdateUserHandler(fbService *services.FirebaseService) gin.HandlerFunc {
	return func(c *gin.Context) {
		// TODO: Implement updating user profile
		c.JSON(501, gin.H{"error": "Not implemented yet"})
	}
}
