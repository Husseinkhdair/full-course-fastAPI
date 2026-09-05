from Core.security.Password import hash_password, verify_password


def test_hash_password():
    hashed_password = hash_password("password")
    assert hashed_password is not None


def test_verify_password():
    hashed_password = hash_password("password")
    assert verify_password("password", hashed_password) is True

test_hash_password()
test_verify_password()