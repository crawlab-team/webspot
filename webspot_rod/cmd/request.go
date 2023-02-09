package cmd

import (
	"fmt"
	"github.com/spf13/cobra"
	"webspot_rod/request"
)

func init() {
	cmdRequest.PersistentFlags().StringVarP(&requestUrl, "url", "u", "", "URL to request")
}

var cmdRequest = &cobra.Command{
	Use: "request",
	Run: func(cmd *cobra.Command, args []string) {
		html := request.GetHtml(requestUrl)
		fmt.Println(html)
	},
}
