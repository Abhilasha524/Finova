import re


MERCHANT_RULES = {
    # ---------------------------------------------------------
    # FOOD & GROCERIES
    # ---------------------------------------------------------
    "SWIGGY": "Food",
    "ZOMATO": "Food",
    "DOMINOS": "Food",
    "PIZZA HUT": "Food",
    "MCDONALD": "Food",
    "KFC": "Food",
    "BURGER KING": "Food",
    "STARBUCKS": "Food",
    "SUBWAY": "Food",
    "RESTAURANT": "Food",
    "CAFE": "Food",
    "BAKERY": "Food",
    "FOOD": "Food",
    "DUNZO": "Food",

    # Groceries / household shopping
    "BIGBASKET": "Household",
    "DMART": "Household",
    "D MART": "Household",
    "RELIANCE SMART": "Household",
    "BLINKIT": "Household",
    "ZEPTO": "Household",
    "INSTAMART": "Household",
    "SPENCERS": "Household",
    "MORE SUPERMARKET": "Household",

    # ---------------------------------------------------------
    # TRANSPORTATION
    # ---------------------------------------------------------
    "UBER": "Transportation",
    "OLA": "Transportation",
    "RAPIDO": "Transportation",
    "METRO": "Transportation",
    "IRCTC": "Transportation",
    "INDIAN RAILWAYS": "Transportation",
    "RED BUS": "Transportation",
    "REDBUS": "Transportation",

    # ---------------------------------------------------------
    # TRAVEL / TOURISM
    # ---------------------------------------------------------
    "MAKEMYTRIP": "Tourism",
    "MAKE MY TRIP": "Tourism",
    "GOIBIBO": "Tourism",
    "BOOKING.COM": "Tourism",
    "BOOKING": "Tourism",
    "AIRBNB": "Tourism",
    "CLEARTRIP": "Tourism",
    "EASEMYTRIP": "Tourism",
    "YATRA": "Tourism",
    "OYO": "Tourism",

    # ---------------------------------------------------------
    # HEALTH
    # ---------------------------------------------------------
    "APOLLO": "Health",
    "PHARMACY": "Health",
    "MEDICAL": "Health",
    "HOSPITAL": "Health",
    "CLINIC": "Health",
    "MEDICINE": "Health",
    "PHARMEASY": "Health",
    "1MG": "Health",
    "TATA 1MG": "Health",
    "NETMEDS": "Health",
    "PRACTO": "Health",

    # ---------------------------------------------------------
    # EDUCATION
    # ---------------------------------------------------------
    "COLLEGE": "Education",
    "UNIVERSITY": "Education",
    "SCHOOL": "Education",
    "COURSE": "Education",
    "UDEMY": "Education",
    "COURSERA": "Education",
    "BYJU": "Education",
    "UNACADEMY": "Education",
    "SKILLSHARE": "Education",
    "EDX": "Education",

    # ---------------------------------------------------------
    # APPAREL / SHOPPING
    # ---------------------------------------------------------
    "MYNTRA": "Apparel",
    "AJIO": "Apparel",
    "NYKAA FASHION": "Apparel",
    "H&M": "Apparel",
    "ZARA": "Apparel",
    "WESTSIDE": "Apparel",
    "PANTALOONS": "Apparel",
    "MAX FASHION": "Apparel",
    "LIFESTYLE": "Apparel",
    "DECATHLON": "Apparel",

    # ---------------------------------------------------------
    # ONLINE SHOPPING
    # ---------------------------------------------------------
    "AMAZON": "Other",
    "FLIPKART": "Other",
    "MEESHO": "Other",
    "SNAPDEAL": "Other",
    "TATACLIQ": "Other",

    # ---------------------------------------------------------
    # SUBSCRIPTIONS / DIGITAL SERVICES
    # ---------------------------------------------------------
    "NETFLIX": "Subscription",
    "SPOTIFY": "Subscription",
    "PRIME VIDEO": "Subscription",
    "AMAZON PRIME": "Subscription",
    "YOUTUBE PREMIUM": "Subscription",
    "YOUTUBE MUSIC": "Subscription",
    "HOTSTAR": "Subscription",
    "JIOHOTSTAR": "Subscription",
    "DISNEY+": "Subscription",
    "APPLE MUSIC": "Subscription",

    # ---------------------------------------------------------
    # BEAUTY / GROOMING
    # ---------------------------------------------------------
    "NYKAA": "Beauty",
    "SEPHORA": "Beauty",
    "PURPLLE": "Beauty",
    "PARACHUTE": "Beauty",
    "SALON": "Grooming",
    "BARBER": "Grooming",

    # ---------------------------------------------------------
    # UTILITIES / BILLS
    # ---------------------------------------------------------
    "ELECTRICITY": "Bills",
    "ELECTRICITY BILL": "Bills",
    "WATER BILL": "Bills",
    "GAS BILL": "Bills",
    "BROADBAND": "Bills",
    "WIFI": "Bills",
    "AIRTEL": "Bills",
    "JIO": "Bills",
    "VI": "Bills",
    "VODAFONE": "Bills",

    # ---------------------------------------------------------
    # INSURANCE / FINANCIAL SERVICES
    # ---------------------------------------------------------
    "LIC": "Life Insurance",
    "LIFE INSURANCE": "Life Insurance",
    "INSURANCE": "Life Insurance",

    # ---------------------------------------------------------
    # FUEL
    # ---------------------------------------------------------
    "HPCL": "Transportation",
    "INDIAN OIL": "Transportation",
    "IOCL": "Transportation",
    "BHARAT PETROLEUM": "Transportation",
    "BPCL": "Transportation",
    "SHELL": "Transportation",
}


def extract_merchant_pattern(description: str) -> str:
    """
    Extract a stable merchant pattern from a transaction description.

    Examples:

    UPI/123456789/ABC STORE
        -> ABC STORE

    UPI/987654/ABC STORE/REF123
        -> ABC STORE
    """

    description = (description or "").strip()

    if not description:
        return ""

    text = description.upper()

    # Remove common UPI prefixes.
    text = re.sub(
        r"^(UPI|UPI/|UPI-)\s*",
        "",
        text,
    )

    # Remove leading transaction/reference numbers.
    text = re.sub(
        r"^\d{5,}\s*[/\-]?\s*",
        "",
        text,
    )

    # Split UPI-style fields.
    parts = [
        part.strip()
        for part in re.split(r"[/|]", text)
        if part.strip()
    ]

    if parts:
        meaningful_parts = [
            part
            for part in parts
            if not re.fullmatch(r"\d+", part)
            and not re.fullmatch(r"[A-Z0-9]{8,}", part)
        ]

        if meaningful_parts:
            text = meaningful_parts[0]

    # Remove reference information.
    text = re.sub(
        r"\b(REF|REFERENCE|TXN|TRANSACTION|ID|NO)\b.*$",
        "",
        text,
    )

    # Clean punctuation and extra spaces.
    text = re.sub(
        r"[^A-Z0-9 &.\-]",
        " ",
        text,
    )

    text = re.sub(
        r"\s+",
        " ",
        text,
    ).strip()

    return text


def get_rule_category(description: str) -> str | None:
    """
    Return a category when a known merchant keyword is found.
    """

    text = (description or "").upper()

    for keyword, category in MERCHANT_RULES.items():
        if keyword in text:
            return category

    return None