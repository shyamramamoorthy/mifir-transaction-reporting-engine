"""
LEI (Legal Entity Identifier) validator.

Implements the ISO 17442 check-digit algorithm (ISO 7064 MOD 97-10):
an LEI is valid if, after converting letters to numbers (A=10 ... Z=35)
and treating the whole 20-character code as one big number, that number
leaves a remainder of exactly 1 when divided by 97.

Source: ISO 17442-1:2020; ISO/IEC 7064 MOD 97-10.
"""


def is_valid_lei(lei: str) -> bool:
    """
    Return True if `lei` is a structurally and check-digit valid LEI.

    Checks performed:
      1. Exactly 20 characters
      2. Only uppercase letters and digits
      3. MOD 97-10 checksum passes (remainder == 1)
    """
    lei = lei.strip().upper()

    # --- Structural checks ---
    if len(lei) != 20:
        return False
    if not lei.isalnum():
        return False

    # --- Checksum ---
    numeric_string = ""
    for char in lei:
        if char.isdigit():
            numeric_string += char
        else:
            # A=10, B=11, ..., Z=35 (ord('A') is 65, so ord(char) - 55 gives 10)
            numeric_string += str(ord(char) - 55)

    as_number = int(numeric_string)
    return as_number % 97 == 1


if __name__ == "__main__":
    # Quick manual sanity check while we build this — not the real test suite yet.
    # Hand-computed to be checksum-valid; not a real registered LEI.
    test_lei = "HELLO123456789012313"
    print(f"{test_lei}: {is_valid_lei(test_lei)}")

    # Same code with the last digit changed, to prove it correctly rejects a broken one.
    broken_lei = "HELLO123456789012314"
    print(f"{broken_lei}: {is_valid_lei(broken_lei)}")