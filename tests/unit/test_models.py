from werkzeug.security import generate_password_hash

from app import User


def test_new_user():
    """
    GIVEN a User model
    WHEN a new User is created
    THEN check the name, email, password are defined correctly
    """
    user = User(
        name="user",
        email="user@usre.com",
        password=generate_password_hash("user", method="sha256"),
    )
    assert user.name == "user"
    assert user.email == "user@usre.com"
    assert user.password != "user"
