from Core.security.Password import hash_password, verify_password


def test_hash_password_success():
    hashed_password = hash_password("password")
    assert hashed_password is not None


def test_verify_success():
    hashed_password = hash_password("password")
    assert verify_password("password", hashed_password) is True

def test_verify_failed():
    hashed_password = hash_password("password")
    assert verify_password("wrong_password", hashed_password) is False

def test_verify_empty():
    hashed_password = hash_password("password")
    assert verify_password("", hashed_password) is False

def test_verify_empty_hash():
    hashed_password = hash_password("password")
    assert verify_password("password", "") is False
    
    