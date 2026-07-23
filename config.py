"""Configuration: Tesla markets, models, and database location."""

DB_PATH = "tesla_prices.db"

# Model URL slugs. Cybertruck exists only in North America; 404s are skipped gracefully.
MODELS = ["model3", "modely", "models", "modelx", "cybertruck"]

# market key -> (base_url, locale_path, currency)
# locale_path "" means the base URL serves that market directly (US, China).
MARKETS = {
    # North America
    "United States":  ("https://www.tesla.com", "",       "USD"),
    "Canada":         ("https://www.tesla.com", "en_ca",  "CAD"),
    "Mexico":         ("https://www.tesla.com", "es_mx",  "MXN"),
    "Puerto Rico":    ("https://www.tesla.com", "en_pr",  "USD"),
    # Europe
    "Austria":        ("https://www.tesla.com", "de_at",  "EUR"),
    "Belgium":        ("https://www.tesla.com", "nl_be",  "EUR"),
    "Croatia":        ("https://www.tesla.com", "hr_hr",  "EUR"),
    "Czech Republic": ("https://www.tesla.com", "cs_cz",  "CZK"),
    "Denmark":        ("https://www.tesla.com", "da_dk",  "DKK"),
    "Finland":        ("https://www.tesla.com", "fi_fi",  "EUR"),
    "France":         ("https://www.tesla.com", "fr_fr",  "EUR"),
    "Germany":        ("https://www.tesla.com", "de_de",  "EUR"),
    "Greece":         ("https://www.tesla.com", "el_gr",  "EUR"),
    "Hungary":        ("https://www.tesla.com", "hu_hu",  "HUF"),
    "Iceland":        ("https://www.tesla.com", "is_is",  "ISK"),
    "Ireland":        ("https://www.tesla.com", "en_ie",  "EUR"),
    "Italy":          ("https://www.tesla.com", "it_it",  "EUR"),
    "Luxembourg":     ("https://www.tesla.com", "fr_lu",  "EUR"),
    "Netherlands":    ("https://www.tesla.com", "nl_nl",  "EUR"),
    "Norway":         ("https://www.tesla.com", "no_no",  "NOK"),
    "Poland":         ("https://www.tesla.com", "pl_pl",  "PLN"),
    "Portugal":       ("https://www.tesla.com", "pt_pt",  "EUR"),
    "Romania":        ("https://www.tesla.com", "ro_ro",  "RON"),
    "Slovenia":       ("https://www.tesla.com", "sl_si",  "EUR"),
    "Spain":          ("https://www.tesla.com", "es_es",  "EUR"),
    "Sweden":         ("https://www.tesla.com", "sv_se",  "SEK"),
    "Switzerland":    ("https://www.tesla.com", "de_ch",  "CHF"),
    "United Kingdom": ("https://www.tesla.com", "en_gb",  "GBP"),
    # Middle East
    "Israel":         ("https://www.tesla.com", "he_il",  "ILS"),
    "UAE":            ("https://www.tesla.com", "ar_ae",  "AED"),
    "Qatar":          ("https://www.tesla.com", "en_qa",  "QAR"),
    "Jordan":         ("https://www.tesla.com", "en_jo",  "JOD"),
    # Asia-Pacific
    "China":          ("https://www.tesla.cn", "",        "CNY"),
    "Hong Kong":      ("https://www.tesla.com", "en_hk",  "HKD"),
    "Macau":          ("https://www.tesla.com", "en_mo",  "MOP"),
    "Japan":          ("https://www.tesla.com", "ja_jp",  "JPY"),
    "South Korea":    ("https://www.tesla.com", "ko_kr",  "KRW"),
    "Taiwan":         ("https://www.tesla.com", "zh_tw",  "TWD"),
    "Singapore":      ("https://www.tesla.com", "en_sg",  "SGD"),
    "Malaysia":       ("https://www.tesla.com", "en_my",  "MYR"),
    "Thailand":       ("https://www.tesla.com", "th_th",  "THB"),
    "Australia":      ("https://www.tesla.com", "en_au",  "AUD"),
    "New Zealand":    ("https://www.tesla.com", "en_nz",  "NZD"),
    # South America
    "Chile":          ("https://www.tesla.com", "es_cl",  "CLP"),
}
