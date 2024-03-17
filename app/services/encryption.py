import bcrypt


def make_password(password: bytes) -> str:
    """ Шифрует пароль с помощью bcrypt."""

    # Генерируем "соль"
    salt = bcrypt.gensalt()

    # Хешируем пароль с использованием соли и декодируем (превращаем в строку)
    hashed_password = bcrypt.hashpw(password, salt).decode()

    return hashed_password


def check_password(password: str, hashed_password: str) -> bool:
    """Принимает пароль и проверяет его на соответствие с шифрованным паролем.

   :param password: Пароль, который требуется проверить.
   :param hashed_password: Зашифрованный пароль, с которым сравнивается предоставленный пароль.

   :return: True, если пароль соответствует зашифрованному паролю, в противном случае - False.
   """

    password = password.encode()
    hashed_password = hashed_password.encode()
    return bcrypt.checkpw(password, hashed_password)
