package api

import (
	"log"
	"net/http"
	"strings"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/iknizzz1807/learn2aid/services"
)

// Refresh token phải được xử lý ở client, không phải server, vì Firebase không cho phép server refresh token trực tiếp.
// Middleware của bạn chỉ có thể thông báo cho client khi token sắp hết hạn.

// JavaScript client code
// async function makeAPICall(endpoint) {
//     const token = await getFirebaseToken(); // Lấy token từ Firebase Auth

//     const response = await fetch(`/api/${endpoint}`, {
//         headers: {
//             'Authorization': `Bearer ${token}`
//         }
//     });

//     // Kiểm tra header X-Refresh-Token
//     if (response.headers.get('X-Refresh-Token') === 'true') {
//         // Token sắp hết hạn, làm mới token
//         await refreshFirebaseToken();
//     }

//     return response.json();
// }

// AuthConfig defines configuration for the auth middleware
type AuthConfig struct {
	RequireAuth bool // Set to false for optional authentication
}

// AuthMiddleware checks Firebase ID token with options for refresh handling
func AuthMiddleware(fbService *services.FirebaseService, config ...AuthConfig) gin.HandlerFunc {
	// Default config
	cfg := AuthConfig{
		RequireAuth: true,
	}

	// Override with user config if provided
	if len(config) > 0 {
		cfg = config[0]
	}

	return func(c *gin.Context) {
		authHeader := c.GetHeader("Authorization")

		// Check if authentication is required
		if authHeader == "" {
			if cfg.RequireAuth {
				c.AbortWithStatusJSON(http.StatusUnauthorized, gin.H{
					"error":         "Missing authorization header",
					"authenticated": false,
				})
				return
			} else {
				// Optional auth - continue without user info
				c.Set("authenticated", false)
				c.Next()
				return
			}
		}

		// Extract token from Bearer header
		idToken := strings.Replace(authHeader, "Bearer ", "", 1)

		// Verify token
		token, err := fbService.VerifyToken(idToken)
		if err != nil {
			if cfg.RequireAuth {
				c.AbortWithStatusJSON(http.StatusUnauthorized, gin.H{
					"error":         "Invalid or expired token",
					"authenticated": false,
				})
				return
			} else {
				// Optional auth - continue without user info
				c.Set("authenticated", false)
				c.Next()
				return
			}
		}

		// Check token expiration time (add buffer before actual expiration)
		expiresAt := time.Unix(token.Expires, 0)
		tokenAboutToExpire := time.Now().Add(5 * time.Minute).After(expiresAt)

		// Set user info in context
		c.Set("authenticated", true)
		c.Set("userID", token.UID)
		c.Set("userEmail", token.Claims["email"])
		c.Set("userName", token.Claims["name"])
		c.Set("pictureUrl", token.Claims["picture"])

		// If token is about to expire, add refresh header
		if tokenAboutToExpire {
			c.Header("X-Refresh-Token", "true")
		}

		c.Next()
	}
}

// OptionalAuthMiddleware is a shorthand for optional authentication
func OptionalAuthMiddleware(fbService *services.FirebaseService) gin.HandlerFunc {
	return AuthMiddleware(fbService, AuthConfig{RequireAuth: false})
}

// LoggingMiddleware logs request information
func LoggingMiddleware() gin.HandlerFunc {
	return func(c *gin.Context) {
		// Start timer
		startTime := time.Now()

		// Process request
		c.Next()

		// End timer
		endTime := time.Now()
		latency := endTime.Sub(startTime)

		// Log request details
		statusCode := c.Writer.Status()
		clientIP := c.ClientIP()
		method := c.Request.Method
		path := c.Request.URL.Path

		log.Printf("[%s] %s %s %d %v", method, path, clientIP, statusCode, latency)
	}
}

// RateLimiterMiddleware implements a simple rate limiter
func RateLimiterMiddleware() gin.HandlerFunc {
	// In a production environment, use a proper rate limiter like Redis
	// This is a simple in-memory implementation for demonstration
	limits := make(map[string]int)
	resetTime := time.Now()

	return func(c *gin.Context) {
		// Reset counters every minute
		if time.Since(resetTime) > time.Minute {
			limits = make(map[string]int)
			resetTime = time.Now()
		}

		// Get client IP
		clientIP := c.ClientIP()

		// Check rate limit (100 requests per minute)
		if limits[clientIP] >= 100 {
			c.AbortWithStatusJSON(http.StatusTooManyRequests, gin.H{"error": "Rate limit exceeded"})
			return
		}

		// Increment counter
		limits[clientIP]++

		c.Next()
	}
}
