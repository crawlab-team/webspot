package request

import (
	"github.com/go-rod/rod"
	"time"
)

func GetHtml(requestUrl string, duration int) string {
	page := rod.New().MustConnect().MustPage()
	page.MustNavigate(requestUrl).MustWaitLoad()
	if duration > 0 {
		time.Sleep(time.Duration(duration) * time.Second)
	}
	html := page.MustHTML()
	return html
}
