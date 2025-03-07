package main

import (
	"fmt"
	"log"
	"net/http"

	"github.com/gin-gonic/gin"
	"github.com/go-resty/resty/v2"
)

type InputData struct {
	X float64 `json:"x"`
}

type PredictionResponse struct {
	Prediction float64 `json:"prediction"`
}

func main() {
	r := gin.Default()

	r.GET("/", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{"message": "Hello from learn2aid!"})
	})

	r.POST("/predict", func(c *gin.Context) {
		var input InputData
		if err := c.ShouldBindJSON(&input); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid input"})
			return
		}

		client := resty.New()
		var response PredictionResponse
		_, err := client.R().
			SetHeader("Content-Type", "application/json").
			SetBody(input).
			SetResult(&response).
			Post("http://ai-service:8000/predict")

		if err != nil {
			log.Println("Error calling AI service:", err)
			c.JSON(http.StatusInternalServerError, gin.H{"error": "AI service unavailable"})
			return
		}

		c.JSON(http.StatusOK, gin.H{"prediction": response.Prediction})
	})

	fmt.Println("Go backend running on http://localhost:8080")
	r.Run(":8080")
}
