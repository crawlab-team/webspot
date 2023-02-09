package request

import "github.com/go-rod/rod"

var browser *rod.Browser

func GetBrowser() *rod.Browser {
	if browser == nil {
		browser = rod.New()
	}
	return browser
}
