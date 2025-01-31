class UserDoesNotExist(Exception):
    """
    Raised when a user does not exist.
    """

class ReusedUsernameError(Exception):
    """
    Raised when a user tries to create an account with a username that is already in use or
    when changing their username to a username that is already in use.
    """

class EmailAlreadyInUseError(Exception):
    """
    Raised when a user tries to create an account with an email that is already in use or
    when changing their email to an email that is already in use.
    """

class EmailIsAlreadyVerifiedError(Exception):
    """
    Raised when a user tries to verify an email that is already verified.
    """

class EmailIsNotUserEmailError(Exception):
    """
    Raised when a user tries to verify an email that is not their email.
    """

class EmailNotVerifiedError(Exception):
    """
    Raised when a user tries to login with an email that has not been verified.
    """

class SameAsOldEmailError(Exception):
    """
    Raised when a user tries to change their email to the email they are already using.
    """

class IncorrectPwdError(Exception):
    """
    Raised when a user tries to login with an incorrect password.
    """

class EmailDoesNotExistError(Exception):
    """
    Raised when a user tries to login with an email that does not exist.
    """

class ReusedPwdError(Exception):
    """
    Raised if the password to be changed is the same as the new password.
    """

class ChangePwdError(Exception):
    """
    Raised if the user tries to change their password but provided an incorrect old password.
    """

class PwdTooWeakError(Exception):
    """
    Raised if the password does not meet the minimum complexity requirements.
    """

class PwdCompromisedError(Exception):
    """
    Raised if the password is too weak as it has been found in haveibeenpwned's api databases of
    leaked passwords in the dark web caused by data breaches
    """

class haveibeenpwnedAPIDownError(Exception):
    """
    Raised if the haveibeenpwned API is down.
    """

class CardDoesNotExistError(Exception):
    """
    Raised if the user tries to do CRUD operations on their credit card but their credit card does not exist.
    """

class IsAlreadyTeacherError(Exception):
    """
    Raised if the user tries to become a teacher even though they are already a teacher.
    """

class AccountLockedError(Exception):
    """
    Raised if the user tries to login but their account is locked.

    Reasons for locked account: 
        - Too many failed login attempts. (> 8 attempts)
    """

class UserAccountNotRecoveringError(Exception):
    """
    Raised if the admin tries to revoke the account recovery token but the user account is not in the process of being recovered.
    """

class UserAccountIsRecoveringError(Exception):
    """
    Raised if the admin tries to recover the account but the user account is already being recovered.
    """

class No2FATokenError(Exception):
    """
    Raised if the user tries to login or when an admin tries
    to disable 2FA for a user but the user has not enabled 2FA.
    """

class CRC32ChecksumError(Exception):
    """
    Raised if the CRC32C checksum does not match during decryption.
    """

class CiphertextIsNotBytesError(Exception):
    """
    Raised if the ciphertext is not bytes.
    """

class DecryptionError(Exception):
    """
    Raised if the decryption fails.
    """

class InvalidProfilePictureError(Exception):
    """
    Raised if the profile image is not a valid image.
    """

class UserIsUsingOauth2Error(Exception):
    """
    Raised if the user tries to login but is not using Google OAuth2 to login.
    """

class LoginFromNewIpAddressError(Exception):
    """
    Raised if the user tries to login from a new IP address.
    """

class InvalidRecaptchaTokenError(Exception):
    """
    Raised if the user tries to login but the recaptcha token is invalid.
    """

class InvalidRecaptchaActionError(Exception):
    """
    Raised if the user tries to login but the recaptcha action is invalid.
    """

class EncryptionError(Exception):
    """
    Raised if the encryption fails.
    """

class UploadFailedError(Exception):
    """
    Raised if the uploading of files to Google Cloud Platform Storage API fails.
    """

class UserIsNotActiveError(Exception):
    """
    Raised if the user tries to login but their account is not active.
    """