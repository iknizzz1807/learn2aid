package api

import (
	"github.com/gin-gonic/gin"
	"github.com/iknizzz1807/learn2aid/services"
)

func SetupRouter(aiService *services.AIService, fbService *services.FirebaseService) *gin.Engine {
	r := gin.Default()

	// r.Use(gin.Recovery())

	r.Use(corsMiddleware())

	// Public routes - không cần xác thực
	// Health check endpoints
	r.GET("/health", HealthCheckHandler())
	r.GET("/ping", func(c *gin.Context) {
		c.JSON(200, gin.H{"message": "pong"})
	})
	r.GET("/", HomeHandler())

	// API v1 group - tất cả routes còn lại
	v1 := r.Group("/api/v1")
	{
		// Public API endpoints - không cần xác thực
		// Tạo nhóm riêng cho các routes public không cần Auth
		// public := v1.Group("")
		// {
		// v1.POST("/login", LoginHandler(fbService))
		// }

		// Tất cả các routes khác trong API đều cần xác thực
		authenticated := v1.Group("")
		authenticated.Use(AuthMiddleware(fbService))
		{
			// Video endpoints
			authenticated.GET("/videos", GetVideosHandler(fbService))
			authenticated.GET("/videos/category/:category", GetVideosByCategoryHandler(fbService))
			authenticated.GET("/videos/:id", GetVideoByIDHandler(fbService))

			// Quiz endpoints
			authenticated.GET("/quizzes", GetQuizzesHandler(fbService))
			authenticated.GET("/quizzes/category/:category", GetQuizzesByCategoryHandler(fbService))
			authenticated.GET("/quizzes/:id", GetQuizForUserHandler(fbService))
			authenticated.POST("/quizzes/:id/start", StartQuizAttemptHandler(fbService))
			authenticated.POST("/quizzes/:id/submit", SubmitQuizAttemptHandler(fbService))
			authenticated.GET("/quiz-attempts", GetUserQuizAttemptsHandler(fbService))

			// Prediction endpoints
			authenticated.POST("/predict", PredictHandler(aiService, fbService))
			authenticated.GET("/predictions", GetPredictionsHandler(fbService))

			// User endpoints
			authenticated.GET("/user", GetUserHandler(fbService))
			// authenticated.PUT("/user", UpdateUserHandler(fbService))
		}
	}

	return r
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

// func LoginHandler(fbService *services.FirebaseService) gin.HandlerFunc {
// 	return func(c *gin.Context) {
// 		// TODO: Implement user login
// 		c.JSON(501, gin.H{"error": "Not implemented yet"})
// 	}
// }

func GetPredictionsHandler(fbService *services.FirebaseService) gin.HandlerFunc {
	return func(c *gin.Context) {
		// TODO: Implement fetching user predictions
		c.JSON(501, gin.H{"error": "Not implemented yet"})
	}
}
