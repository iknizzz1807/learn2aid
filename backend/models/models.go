package models

import "time"

// InputData represents the input for a prediction request
type InputData struct {
	X float64 `json:"x"`
}

// PredictionResponse represents the response from the AI service
type PredictionResponse struct {
	Prediction float64 `json:"prediction"`
}

// User represents a user in the system
type User struct {
	ID        string    `json:"id"`
	Email     string    `json:"email"`
	Name      string    `json:"name"`
	CreatedAt time.Time `json:"created_at"`
}

// PredictionRecord represents a stored prediction in Firebase
type PredictionRecord struct {
	ID         string    `json:"id"`
	UserID     string    `json:"user_id"`
	Input      float64   `json:"input"`
	Prediction float64   `json:"prediction"`
	Timestamp  time.Time `json:"timestamp"`
}

// ErrorResponse represents an API error response
type ErrorResponse struct {
	Error       string `json:"error"`
	Description string `json:"description,omitempty"`
	Code        int    `json:"code,omitempty"`
}

// SuccessResponse represents a generic success response
type SuccessResponse struct {
	Success bool        `json:"success"`
	Data    interface{} `json:"data,omitempty"`
	Message string      `json:"message,omitempty"`
}
