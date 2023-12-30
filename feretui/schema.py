from typing import Callable

from password_validator import PasswordValidator
from pydantic import BaseModel, model_validator
from pydantic.functional_validators import AfterValidator
from typing_extensions import Annotated

from feretui.translate import translated_message

PasswordInvalid = translated_message('The password should have {msg}.')
PasswordMinSize = translated_message('more than {min_size} caractere')
PasswordMaxSize = translated_message('less than {max_size} caractere')
PasswordWithLowerCase = translated_message('with lowercase')
PasswordWithoutLowerCase = translated_message('without lowercase')
PasswordWithUpperCase = translated_message('with uppercase')
PasswordWithoutUpperCase = translated_message('without uppercase')
PasswordWithDigits = translated_message('with digits')
PasswordWithoutDigits = translated_message('without digits')
PasswordWithSymbols = translated_message('with symbols')
PasswordWithoutSymbols = translated_message('without symbols')
PasswordWithSpaces = translated_message('with spaces')
PasswordWithoutSpaces = translated_message('without spaces')

FieldRequired = translated_message('This field is required')


def format_errors(pydantic_errors: list[dict]):
    errors: dict[str, list[str]] = {}
    for error in pydantic_errors:
        msg = error['msg']
        for loc in error['loc']:
            field = errors.setdefault(loc, [])
            field.append(msg)

    return errors


def required_validator(entry):
    if not entry:
        raise ValueError(FieldRequired)

    return entry


def password_validator(
    min_size: int = 12,
    max_size: int = None,
    has_lowercase: bool = True,
    has_uppercase: bool = True,
    has_digits: bool = True,
    has_symbols: bool = True,
    has_spaces: bool = False,
) -> Callable[str, str]:
    schema = PasswordValidator()
    waiting = []
    if min_size:
        schema.min(min_size)
        waiting.append((
            PasswordMinSize,
            dict(min_size=min_size),
        ))

    if max_size:
        schema.min(max_size)
        waiting.append((
            PasswordMaxSize,
            dict(max_size=max_size),
        ))

    if has_lowercase:
        schema.has().lowercase()
        waiting.append((
            PasswordWithLowerCase,
            dict(),
        ))
    else:
        schema.has().no().lowercase()
        waiting.append((
            PasswordWithoutLowerCase,
            dict(),
        ))

    if has_uppercase:
        schema.has().uppercase()
        waiting.append((
            PasswordWithUpperCase,
            dict(),
        ))
    else:
        schema.has().no().uppercase()
        waiting.append((
            PasswordWithoutUpperCase,
            dict(),
        ))

    if has_digits:
        schema.has().digits()
        waiting.append((
            PasswordWithDigits,
            dict(),
        ))
    else:
        schema.has().no().digits()
        waiting.append((
            PasswordWithoutDigits,
            dict(),
        ))

    if has_symbols:
        schema.has().symbols()
        waiting.append((
            PasswordWithSymbols,
            dict(),
        ))
    else:
        schema.has().no().symbols()
        waiting.append((
            PasswordWithoutSymbols,
            dict(),
        ))

    if has_spaces:
        schema.has().spaces()
        waiting.append((
            PasswordWithSpaces,
            dict(),
        ))
    else:
        schema.has().no().spaces()
        waiting.append((
            PasswordWithoutSpaces,
            dict(),
        ))

    def validator(entry: str) -> str:
        msg = PasswordInvalid.get(
            msg=', '.join(x[0].get(**x[1]) for x in waiting)
        )
        if not schema.validate(entry):
            raise ValueError(msg)

        return entry

    return validator


class LoginValidator(BaseModel):
    login: str
    password: str


Password = Annotated[str, AfterValidator(password_validator())]


class SignupValidator(BaseModel):
    login: str
    lang: str
    password: Password
    confirm_password: str

    @model_validator(mode='after')
    def check_passwords_match(self) -> 'SignupValidator':
        pw1 = self.password
        pw2 = self.confirm_password
        if pw1 is not None and pw2 is not None and pw1 != pw2:
            raise ValueError('passwords do not match')

        return self
