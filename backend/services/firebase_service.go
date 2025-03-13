package services

import (
	"context"
	"log"

	"time"

	"errors"

	"cloud.google.com/go/firestore"
	firebase "firebase.google.com/go/v4"
	"firebase.google.com/go/v4/auth"
	"github.com/iknizzz1807/learn2aid/models"
	"google.golang.org/api/iterator"
	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/status"
)

// Phía frontend: Cần thêm code để:

// Đăng nhập với Google thông qua Firebase Auth
// Lấy ID token
// Gửi token trong header Authorization
// Xử lý refresh token khi nhận header X-Refresh-Token

type FirebaseService struct {
	AuthClient      *auth.Client
	FirestoreClient *firestore.Client
}

type AidVideo struct {
	ID           string    `json:"id" firestore:"-"`
	Title        string    `json:"title"`
	Description  string    `json:"description"`
	VideoURL     string    `json:"videoUrl"`
	ThumbnailURL string    `json:"thumbnailUrl"`
	Category     string    `json:"category"`
	Duration     int       `json:"duration"`
	Created      time.Time `json:"created"`
}

func NewFirebaseService(app *firebase.App) *FirebaseService {
	ctx := context.Background()

	authClient, err := app.Auth(ctx)
	if err != nil {
		log.Fatalf("Error getting Auth client: %v", err)
	}

	firestoreClient, err := app.Firestore(ctx)
	if err != nil {
		log.Fatalf("Error getting Firestore client: %v", err)
	}

	return &FirebaseService{
		AuthClient:      authClient,
		FirestoreClient: firestoreClient,
	}
}

// VerifyToken validates a Firebase ID token
// Hàm này được sử dụng trong auth middleware
func (fs *FirebaseService) VerifyToken(idToken string) (*auth.Token, error) {
	ctx := context.Background()
	token, err := fs.AuthClient.VerifyIDToken(ctx, idToken)
	if err != nil {
		return nil, err
	}
	return token, nil
}

// GetUserByID gets user information by ID
func (fs *FirebaseService) GetUserByID(uid string) (*auth.UserRecord, error) {
	ctx := context.Background()
	return fs.AuthClient.GetUser(ctx, uid)
}

// GetAllFirstAidVideos retrieves all first aid videos from Firestore
func (fs *FirebaseService) GetAllFirstAidVideos() ([]AidVideo, error) {
	ctx := context.Background()

	iter := fs.FirestoreClient.Collection("aid_videos").Documents(ctx)
	var videos []AidVideo

	for {
		doc, err := iter.Next()
		if err == iterator.Done {
			break
		}
		if err != nil {
			return nil, err
		}

		var video AidVideo
		if err := doc.DataTo(&video); err != nil {
			return nil, err
		}

		video.ID = doc.Ref.ID
		videos = append(videos, video)
	}

	return videos, nil
}

// GetVideosByCategory retrieves first aid videos filtered by category
func (fs *FirebaseService) GetVideosByCategory(category string) ([]AidVideo, error) {
	ctx := context.Background()

	query := fs.FirestoreClient.Collection("aid_videos").Where("category", "==", category)
	iter := query.Documents(ctx)

	var videos []AidVideo

	for {
		doc, err := iter.Next()
		if err == iterator.Done {
			break
		}
		if err != nil {
			return nil, err
		}

		var video AidVideo
		if err := doc.DataTo(&video); err != nil {
			return nil, err
		}

		video.ID = doc.Ref.ID
		videos = append(videos, video)
	}

	return videos, nil
}

// GetVideoByID retrieves a specific video by ID
func (fs *FirebaseService) GetVideoByID(id string) (*AidVideo, error) {
	ctx := context.Background()

	doc, err := fs.FirestoreClient.Collection("aid_videos").Doc(id).Get(ctx)
	if err != nil {
		return nil, err
	}

	var video AidVideo
	if err := doc.DataTo(&video); err != nil {
		return nil, err
	}

	video.ID = doc.Ref.ID
	return &video, nil
}

// // Storage rules
// rules_version = '2';
// service firebase.storage {
//   match /b/{bucket}/o {
//     match /first_aid_videos/{video=**} {
//       allow read;  // Allow anyone to read videos
//       allow write: if false;  // Only allow admin upload through console
//     }
//   }
// }

// // Firestore rules
// rules_version = '2';
// service cloud.firestore {
//   match /databases/{database}/documents {
//     match /first_aid_videos/{document=**} {
//       allow read;  // Allow anyone to read
//       allow write: if request.auth != null && request.auth.token.admin == true;
//     }
//   }
// }

// GetAllQuizzes retrieves all quizzes from Firestore
func (fs *FirebaseService) GetAllQuizzes() ([]models.Quiz, error) {
	ctx := context.Background()

	iter := fs.FirestoreClient.Collection("quizzes").Documents(ctx)
	var quizzes []models.Quiz

	for {
		doc, err := iter.Next()
		if err == iterator.Done {
			break
		}
		if err != nil {
			return nil, err
		}

		var quiz models.Quiz
		if err := doc.DataTo(&quiz); err != nil {
			return nil, err
		}

		quiz.ID = doc.Ref.ID
		quizzes = append(quizzes, quiz)
	}

	return quizzes, nil
}

// GetQuizzesByCategory retrieves quizzes filtered by category
func (fs *FirebaseService) GetQuizzesByCategory(category string) ([]models.Quiz, error) {
	ctx := context.Background()

	query := fs.FirestoreClient.Collection("quizzes").Where("category", "==", category)
	iter := query.Documents(ctx)

	var quizzes []models.Quiz

	for {
		doc, err := iter.Next()
		if err == iterator.Done {
			break
		}
		if err != nil {
			return nil, err
		}

		var quiz models.Quiz
		if err := doc.DataTo(&quiz); err != nil {
			return nil, err
		}

		quiz.ID = doc.Ref.ID
		quizzes = append(quizzes, quiz)
	}

	return quizzes, nil
}

// GetQuizByID retrieves a quiz by ID with questions
func (fs *FirebaseService) GetQuizByID(id string) (*models.Quiz, error) {
	ctx := context.Background()

	// Get quiz document
	doc, err := fs.FirestoreClient.Collection("quizzes").Doc(id).Get(ctx)
	if err != nil {
		if status.Code(err) == codes.NotFound {
			return nil, errors.New("quiz not found")
		}
		return nil, err
	}

	var quiz models.Quiz
	if err := doc.DataTo(&quiz); err != nil {
		return nil, err
	}
	quiz.ID = doc.Ref.ID

	// Get questions
	questionsRef := fs.FirestoreClient.Collection("quizzes").Doc(id).Collection("questions")
	questionIter := questionsRef.Documents(ctx)

	for {
		questionDoc, err := questionIter.Next()
		if err == iterator.Done {
			break
		}
		if err != nil {
			return nil, err
		}

		var question models.Question
		if err := questionDoc.DataTo(&question); err != nil {
			return nil, err
		}
		question.ID = questionDoc.Ref.ID

		quiz.Questions = append(quiz.Questions, question)
	}

	return &quiz, nil
}

// GetQuizForUser retrieves a quiz by ID but removes correct answers
func (fs *FirebaseService) GetQuizForUser(id string) (*models.Quiz, error) {
	quiz, err := fs.GetQuizByID(id)
	if err != nil {
		return nil, err
	}

	// Remove correct answers from questions
	for i := range quiz.Questions {
		quiz.Questions[i].Answer = -1 // Hide correct answer
	}

	return quiz, nil
}

// SubmitQuizAttempt processes a user's quiz submission
func (fs *FirebaseService) SubmitQuizAttempt(attempt *models.QuizAttempt) (*models.QuizAttempt, error) {
	ctx := context.Background()

	// Get quiz with correct answers for scoring
	quiz, err := fs.GetQuizByID(attempt.QuizID)
	if err != nil {
		return nil, err
	}

	// Calculate score
	correctAnswers := 0
	if len(attempt.Answers) != len(quiz.Questions) {
		return nil, errors.New("number of answers doesn't match number of questions")
	}

	for i, answer := range attempt.Answers {
		if i < len(quiz.Questions) && answer == quiz.Questions[i].Answer {
			correctAnswers++
		}
	}

	// Update attempt with score
	attempt.Score = correctAnswers
	attempt.MaxScore = len(quiz.Questions)
	attempt.Percentage = float64(correctAnswers) / float64(len(quiz.Questions)) * 100
	attempt.EndTime = time.Now()
	attempt.TimeTaken = int(attempt.EndTime.Sub(attempt.StartTime).Seconds())
	attempt.IsCompleted = true

	// Save attempt to Firestore
	ref, _, err := fs.FirestoreClient.Collection("quiz_attempts").Add(ctx, attempt)
	if err != nil {
		return nil, err
	}
	attempt.ID = ref.ID

	return attempt, nil
}

// GetUserQuizAttempts retrieves all quiz attempts for a specific user
func (fs *FirebaseService) GetUserQuizAttempts(userID string) ([]models.QuizAttempt, error) {
	ctx := context.Background()

	query := fs.FirestoreClient.Collection("quiz_attempts").
		Where("userId", "==", userID).
		OrderBy("startTime", firestore.Desc)

	iter := query.Documents(ctx)
	var attempts []models.QuizAttempt

	for {
		doc, err := iter.Next()
		if err == iterator.Done {
			break
		}
		if err != nil {
			return nil, err
		}

		var attempt models.QuizAttempt
		if err := doc.DataTo(&attempt); err != nil {
			return nil, err
		}

		attempt.ID = doc.Ref.ID
		attempts = append(attempts, attempt)
	}

	return attempts, nil
}

// StartQuizAttempt creates a new quiz attempt
func (fs *FirebaseService) StartQuizAttempt(userID string, quizID string) (*models.QuizAttempt, error) {
	// Check if quiz exists
	quiz, err := fs.GetQuizForUser(quizID)
	if err != nil {
		return nil, err
	}

	// Create new attempt
	attempt := &models.QuizAttempt{
		UserID:      userID,
		QuizID:      quizID,
		StartTime:   time.Now(),
		IsCompleted: false,
		Answers:     make([]int, len(quiz.Questions)),
	}

	// Initialize answers with -1 (not answered)
	for i := range attempt.Answers {
		attempt.Answers[i] = -1
	}

	// Save attempt
	ctx := context.Background()
	ref, _, err := fs.FirestoreClient.Collection("quiz_attempts").Add(ctx, attempt)
	if err != nil {
		return nil, err
	}

	attempt.ID = ref.ID
	return attempt, nil
}
