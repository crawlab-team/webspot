import cssutils


def is_valid_css_selector(selector: str) -> bool:
    try:
        return cssutils.css.CSSStyleRule(selectorText=selector).selectorList is not None
    except:
        return False
