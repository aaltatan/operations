import re


def validate_password(value: str) -> None:
    if value == value.lower():
        message = "Password must contain at least one uppercase letter"
        raise ValueError(message)

    numeric = re.compile(r"[0-9]")
    if numeric.search(value) is None:
        message = "Password must contain at least one number"
        raise ValueError(message)

    special = re.compile(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>/?~]")

    if special.search(value) is None:
        message = "Password must contain at least one special character"
        raise ValueError(message)

    blacklist_words = [
        "password",
        "123456",
        "qwerty",
        "123456789",
        "iloveyou",
        "letmein",
        "12345",
        "princess",
        "111111",
        "1234567",
        "abc123",
        "computer",
        "superman",
        "internet",
        "iloveyou",
        "trustno1",
        "1q2w3e4r",
        "sunshine",
        "football",
        "shadow",
        "monkey",
        "666666",
        "abc123456",
        "letmein1",
        "whatever",
    ]

    if any(word in value.lower() for word in blacklist_words):
        message = "Password must not contain any blacklisted words"
        raise ValueError(message)
