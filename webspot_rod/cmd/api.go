package cmd

import (
	"github.com/spf13/cobra"
	"webspot_rod/api"
)

var cmdApi = &cobra.Command{
	Use: "api",
	Run: func(cmd *cobra.Command, args []string) {
		api.RunApi()
	},
}
