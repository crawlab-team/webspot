package request

import (
	"time"
)

func GetHtml(requestUrl string, duration int) string {
	page := GetBrowser().MustPage()
	page.MustNavigate(requestUrl).MustWaitLoad()
	if duration > 0 {
		time.Sleep(time.Duration(duration) * time.Second)
	}
	html := page.MustHTML()
	page.MustClose()
	return html
}
