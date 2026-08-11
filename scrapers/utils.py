USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
)


def nettoyer(texte):
    """Remplace les espaces insécables et espaces multiples par des espaces normaux."""
    return " ".join(texte.replace("\xa0", " ").split())


def accepter_cookies(page):
    for sel in [
        "#onetrust-accept-btn-handler",
        "button:has-text('Accepter')",
        "button:has-text('Tout accepter')",
        "#didomi-notice-agree-button",
    ]:
        try:
            if page.locator(sel).count() > 0:
                page.locator(sel).first.click(timeout=3000)
                page.wait_for_timeout(500)
        except Exception:
            pass
