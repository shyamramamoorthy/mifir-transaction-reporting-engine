"""
ISIN (International Securities Identification Number) validator.

Implements the ISO 6166 check digit algorithm: a Luhn algorithm applied
to the ISIN after converting letters to numbers (A=10 ... Z=35), the
same conversion trick used for LEIs.

Source: ISO 6166.
"""


def is_valid_isin(isin: str) -> bool:
    """
    Return True if `isin` is a structurally and check-digit valid ISIN.

    Checks performed:
      1. Exactly 12 characters, alphanumeric
      2. Last character is a digit (the check digit is always numeric)
      3. Luhn checksum over the letter-converted first 11 characters passes
    """
    isin = isin.strip().upper()

    # --- Structural checks ---
    if len(isin) != 12 or not isin.isalnum():
        return False

    body = isin[:11]
    check_digit_char = isin[11]

    if not check_digit_char.isdigit():
        return False

    # --- Convert letters to numbers (same trick as lei.py) ---
    numeric_string = ""
    for char in body:
        if char.isdigit():
            numeric_string += char
        else:
            numeric_string += str(ord(char) - 55)

    # --- Luhn checksum, working right to left ---
    reversed_digits = numeric_string[::-1]
    total = 0
    for position, digit_char in enumerate(reversed_digits):
        digit = int(digit_char)
        if position % 2 == 0:  # 1st, 3rd, 5th... position from the right
            digit = digit * 2
            if digit > 9:
                digit -= 9
        total += digit

    check_digit = (10 - (total % 10)) % 10
    return check_digit == int(check_digit_char)


if __name__ == "__main__":
    # Apple Inc. — real, widely-cited worked example for this exact algorithm
    print("US0378331005:", is_valid_isin("US0378331005"))

    # Same code with the check digit deliberately broken
    print("US0378331006:", is_valid_isin("US0378331006"))