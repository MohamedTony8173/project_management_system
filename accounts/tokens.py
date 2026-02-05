from django.contrib.auth.tokens import PasswordResetTokenGenerator
from six import text_type

from django.contrib.auth.tokens import PasswordResetTokenGenerator

class UserEmailMakeLinkToken(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        # We include the user's primary key, the timestamp, and the active status.
        # If any of these change, the token becomes invalid.
        return (
            text_type(user.pk) + text_type(timestamp) + text_type(user.is_active)
        )

account_activation_token = UserEmailMakeLinkToken()