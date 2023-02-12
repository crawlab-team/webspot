package cmd

import (
	"fmt"
	"github.com/go-rod/rod"
	"github.com/spf13/cobra"
	"time"
)

func init() {
	rootCmd.PersistentFlags().StringVarP(&requestUrl, "url", "u", "", "URL to request")
}

var rootCmd = &cobra.Command{
	Use: "rod",
	Run: func(cmd *cobra.Command, args []string) {
		page := rod.New().MustConnect().MustPage()
		page.Timeout(5 * time.Second).MustNavigate(requestUrl)
		html := page.MustHTML()
		fmt.Println(html)
	},
}

func Execute() {
	var rootCmd = &cobra.Command{Use: "app"}
	rootCmd.AddCommand(
		cmdApi,
		cmdRequest,
	)
	rootCmd.Execute()
}
