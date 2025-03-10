package api

import (
	"net/http"

	"github.com/iknizzz1807/learn2aid/models"
	"github.com/iknizzz1807/learn2aid/services"

	"github.com/gin-gonic/gin"
)

// PredictHandler handles prediction requests
func PredictHandler(aiService *services.AIService, fbService *services.FirebaseService) gin.HandlerFunc {
	return func(c *gin.Context) {
		var input models.InputData
		if err := c.ShouldBindJSON(&input); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid input"})
			return
		}

		// Get user ID from context (set by AuthMiddleware)
		// userID, _ := c.Get("userID")
		// uid := userID.(string)

		// Call AI service for prediction
		prediction, err := aiService.GetPrediction(input)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "AI service unavailable"})
			return
		}

		// Store prediction in Firebase
		// err = fbService.StorePrediction(uid, input.X, prediction.Prediction)
		// if err != nil {
		// 	log.Printf("Error storing prediction: %v", err)
		// 	// Continue anyway, just log the error
		// }

		c.JSON(http.StatusOK, prediction)
	}
}
