package services

import (
	"fmt"
	"log"
	"time"

	"github.com/go-resty/resty/v2"
	"github.com/iknizzz1807/learn2aid/models"
)

// AIService handles communication with the AI service
type AIService struct {
	client      *resty.Client
	baseURL     string
	predictPath string
}

// NewAIService creates a new AI service client
func NewAIService(baseURL string) *AIService {
	client := resty.New()
	client.SetHeader("Content-Type", "application/json")
	client.SetTimeout(10 * time.Second) // Set reasonable timeout

	return &AIService{
		client:      client,
		baseURL:     baseURL,
		predictPath: "/predict",
	}
}

// GetPrediction calls the AI service to get a prediction
func (s *AIService) GetPrediction(input models.InputData) (*models.PredictionResponse, error) {
	var response models.PredictionResponse
	url := fmt.Sprintf("%s%s", s.baseURL, s.predictPath)

	resp, err := s.client.R().
		SetBody(input).
		SetResult(&response).
		Post(url)

	if err != nil {
		log.Printf("Error calling AI service: %v", err)
		return nil, err
	}

	if resp.StatusCode() != 200 {
		log.Printf("AI service returned non-200 status code: %d, body: %s",
			resp.StatusCode(), resp.Body())
		return nil, fmt.Errorf("AI service error: %d", resp.StatusCode())
	}

	return &response, nil
}

// HealthCheck checks if the AI service is up and running
func (s *AIService) HealthCheck() error {
	resp, err := s.client.R().Get(s.baseURL)
	if err != nil {
		return err
	}

	if resp.StatusCode() != 200 {
		return fmt.Errorf("AI service health check failed with status: %d", resp.StatusCode())
	}

	return nil
}
