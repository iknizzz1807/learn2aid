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

// Quiz represents a quiz with multiple questions
type Quiz struct {
	ID          string     `json:"id" firestore:"-"`
	Title       string     `json:"title"`
	Description string     `json:"description"`
	Category    string     `json:"category"`
	TimeLimit   int        `json:"timeLimit"` // in seconds, 0 means no limit
	Created     time.Time  `json:"created"`
	Questions   []Question `json:"questions,omitempty"`
}

// Question represents a single question in a quiz
type Question struct {
	ID       string   `json:"id" firestore:"-"`
	Text     string   `json:"text"`
	Options  []string `json:"options"`
	Answer   int      `json:"answer,omitempty"` // Index of correct answer (0-3)
	ImageURL string   `json:"imageUrl,omitempty"`
}

// QuizAttempt represents a user's attempt at a quiz
type QuizAttempt struct {
	ID          string    `json:"id" firestore:"-"`
	UserID      string    `json:"userId"`
	QuizID      string    `json:"quizId"`
	StartTime   time.Time `json:"startTime"`
	EndTime     time.Time `json:"endTime"`
	Score       int       `json:"score"`       // Number of correct answers
	MaxScore    int       `json:"maxScore"`    // Total number of questions
	Percentage  float64   `json:"percentage"`  // Score as percentage
	Answers     []int     `json:"answers"`     // User's answers (indices)
	TimeTaken   int       `json:"timeTaken"`   // Time taken in seconds
	IsCompleted bool      `json:"isCompleted"` // Whether the quiz was completed
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
