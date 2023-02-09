package api

import (
	"github.com/gin-gonic/gin"
)

func RunApi() {
	app := gin.New()
	gin.SetMode("debug")

	app.POST("/request", postRequest)

	// TODO: parameterize address
	if err := app.Run("0.0.0.0:7777"); err != nil {
		panic(err)
	}
}
