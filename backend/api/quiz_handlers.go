package api

import (
	"net/http"

	"github.com/gin-gonic/gin"
	"github.com/iknizzz1807/learn2aid/models"
	"github.com/iknizzz1807/learn2aid/services"
)

// Mô hình dữ liệu cho Quiz, Question và QuizAttempt
// Các phương thức Firebase Service để:
// - Lấy danh sách quiz
// - Lấy quiz theo category
// - Bắt đầu làm quiz
// - Nộp bài và chấm điểm
// - Xem lịch sử làm quiz

// GetQuizzesHandler returns all quizzes
func GetQuizzesHandler(fbService *services.FirebaseService) gin.HandlerFunc {
	return func(c *gin.Context) {
		quizzes, err := fbService.GetAllQuizzes()
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to fetch quizzes"})
			return
		}

		// Map to simplified view (without questions)
		var simplifiedQuizzes []gin.H
		for _, quiz := range quizzes {
			simplifiedQuizzes = append(simplifiedQuizzes, gin.H{
				"id":            quiz.ID,
				"title":         quiz.Title,
				"description":   quiz.Description,
				"category":      quiz.Category,
				"timeLimit":     quiz.TimeLimit,
				"created":       quiz.Created,
				"questionCount": len(quiz.Questions),
			})
		}

		c.JSON(http.StatusOK, simplifiedQuizzes)
	}
}

// GetQuizzesByCategoryHandler returns quizzes by category
func GetQuizzesByCategoryHandler(fbService *services.FirebaseService) gin.HandlerFunc {
	return func(c *gin.Context) {
		category := c.Param("category")
		quizzes, err := fbService.GetQuizzesByCategory(category)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to fetch quizzes"})
			return
		}

		// Map to simplified view (without questions)
		var simplifiedQuizzes []gin.H
		for _, quiz := range quizzes {
			simplifiedQuizzes = append(simplifiedQuizzes, gin.H{
				"id":            quiz.ID,
				"title":         quiz.Title,
				"description":   quiz.Description,
				"category":      quiz.Category,
				"timeLimit":     quiz.TimeLimit,
				"created":       quiz.Created,
				"questionCount": len(quiz.Questions),
			})
		}

		c.JSON(http.StatusOK, simplifiedQuizzes)
	}
}

// GetQuizForUserHandler returns a quiz for a user (without answers)
func GetQuizForUserHandler(fbService *services.FirebaseService) gin.HandlerFunc {
	return func(c *gin.Context) {
		quizID := c.Param("id")
		quiz, err := fbService.GetQuizForUser(quizID)
		if err != nil {
			c.JSON(http.StatusNotFound, gin.H{"error": "Quiz not found"})
			return
		}
		c.JSON(http.StatusOK, quiz)
	}
}

// StartQuizAttemptHandler creates a new quiz attempt
func StartQuizAttemptHandler(fbService *services.FirebaseService) gin.HandlerFunc {
	return func(c *gin.Context) {
		quizID := c.Param("id")
		userID, exists := c.Get("userID")
		if !exists {
			c.JSON(http.StatusUnauthorized, gin.H{"error": "User not authenticated"})
			return
		}

		attempt, err := fbService.StartQuizAttempt(userID.(string), quizID)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to start quiz: " + err.Error()})
			return
		}

		c.JSON(http.StatusOK, attempt)
	}
}

// SubmitQuizAttemptHandler processes a quiz submission
func SubmitQuizAttemptHandler(fbService *services.FirebaseService) gin.HandlerFunc {
	return func(c *gin.Context) {
		quizID := c.Param("id")
		userID, exists := c.Get("userID")
		if !exists {
			c.JSON(http.StatusUnauthorized, gin.H{"error": "User not authenticated"})
			return
		}

		var submission struct {
			AttemptID string `json:"attemptId"`
			Answers   []int  `json:"answers"`
		}

		if err := c.ShouldBindJSON(&submission); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid submission format"})
			return
		}

		// Create attempt object
		attempt := &models.QuizAttempt{
			UserID:  userID.(string),
			QuizID:  quizID,
			Answers: submission.Answers,
		}

		result, err := fbService.SubmitQuizAttempt(attempt)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to submit quiz: " + err.Error()})
			return
		}

		c.JSON(http.StatusOK, result)
	}
}

// GetUserQuizAttemptsHandler retrieves all quiz attempts for the current user
func GetUserQuizAttemptsHandler(fbService *services.FirebaseService) gin.HandlerFunc {
	return func(c *gin.Context) {
		userID, exists := c.Get("userID")
		if !exists {
			c.JSON(http.StatusUnauthorized, gin.H{"error": "User not authenticated"})
			return
		}

		attempts, err := fbService.GetUserQuizAttempts(userID.(string))
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to fetch quiz attempts"})
			return
		}

		c.JSON(http.StatusOK, attempts)
	}
}
