package request

import (
	"github.com/go-rod/rod"
)

func GetHtml(requestUrl string) string {
	page := rod.New().MustConnect().MustPage()
	page.MustNavigate(requestUrl).MustWaitLoad()
	html := page.MustHTML()
	return html
}
