package api

import (
	"github.com/gin-gonic/gin"
	"github.com/iknizzz1807/learn2aid/services"
	"net/http"
)

func GetVideosHandler(fbService *services.FirebaseService) gin.HandlerFunc {
	return func(c *gin.Context) {
		videos, err := fbService.GetAllFirstAidVideos()
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to fetch videos"})
			return
		}
		c.JSON(http.StatusOK, videos)
	}
}

func GetVideosByCategoryHandler(fbService *services.FirebaseService) gin.HandlerFunc {
	return func(c *gin.Context) {
		category := c.Param("category")
		videos, err := fbService.GetVideosByCategory(category)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to fetch videos"})
			return
		}
		c.JSON(http.StatusOK, videos)
	}
}

func GetVideoByIDHandler(fbService *services.FirebaseService) gin.HandlerFunc {
	return func(c *gin.Context) {
		id := c.Param("id")
		video, err := fbService.GetVideoByID(id)
		if err != nil {
			c.JSON(http.StatusNotFound, gin.H{"error": "Video not found"})
			return
		}
		c.JSON(http.StatusOK, video)
	}
}
