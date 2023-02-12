package api

import (
	"github.com/gin-gonic/gin"
	"webspot_rod/request"
)

func postRequest(c *gin.Context) {
	var payload struct {
		Url      string `json:"url"`
		Duration int    `json:"duration"`
	}
	if err := c.BindJSON(&payload); err != nil {
		c.JSON(400, gin.H{"error": err.Error()})
		return
	}
	html := request.GetHtml(payload.Url, payload.Duration)
	c.JSON(200, gin.H{"html": html})
}
