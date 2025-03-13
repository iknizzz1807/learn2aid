package api

import (
	"github.com/gin-gonic/gin"
	"github.com/iknizzz1807/learn2aid/services"
)

func GetUserHandler(fbService *services.FirebaseService) gin.HandlerFunc {
	return func(c *gin.Context) {
		uid, _ := c.Get("userID")
		email, _ := c.Get("userEmail")
		name, _ := c.Get("userName")
		picture, _ := c.Get("pictureUrl")

		userRecord, err := fbService.GetUserByID(uid.(string))

		if err != nil {
			c.JSON(404, gin.H{"error": "Cannot find the user"})
		}

		c.JSON(200, gin.H{
			"email":      email,
			"userRecord": userRecord,
			"name":       name,
			"picture":    picture,
			"record":     userRecord,
		})
	}
}

func UpdateUserHandler(fbService *services.FirebaseService) gin.HandlerFunc {
	return func(c *gin.Context) {
		// TODO: Implement updating user profile
		c.JSON(501, gin.H{"error": "Not implemented yet"})
	}
}
