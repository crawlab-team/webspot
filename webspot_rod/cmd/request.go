package cmd

import (
	"fmt"
	"github.com/spf13/cobra"
	"webspot_rod/request"
)

var (
	requestUrl string
	duration   int
)

func init() {
	cmdRequest.PersistentFlags().StringVarP(&requestUrl, "url", "u", "", "URL to request")
	cmdRequest.PersistentFlags().IntVarP(&duration, "duration", "d", 0, "timeout")
}

var cmdRequest = &cobra.Command{
	Use: "request",
	Run: func(cmd *cobra.Command, args []string) {
		html := request.GetHtml(requestUrl, duration)
		fmt.Println(html)
	},
}
