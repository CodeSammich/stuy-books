def check_valid_email( email ):
    if len(email) >= 10:
        if email[-9:] == "@stuy.edu":
            return True
    return False

