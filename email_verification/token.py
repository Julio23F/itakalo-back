"""
Copyright (c) Django Software Foundation and individual contributors.
All rights reserved.

Redistribution and use in source and binary forms, with or without modification,
are permitted provided that the following conditions are met:

    1. Redistributions of source code must retain the above copyright notice,
       this list of conditions and the following disclaimer.

    2. Redistributions in binary form must reproduce the above copyright
       notice, this list of conditions and the following disclaimer in the
       documentation and/or other materials provided with the distribution.

    3. Neither the name of Django nor the names of its contributors may be used
       to endorse or promote products derived from this software without
       specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

from datetime import datetime

from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.crypto import constant_time_compare, salted_hmac
from django.utils.http import base36_to_int, int_to_base36, urlsafe_base64_decode, urlsafe_base64_encode


class EmailVerificationTokenGenerator:
    """
    Strategy object used to generate and check tokens for the password
    reset mechanism.
    """
    key_salt = "django-email-verification.token"
    algorithm = None
    secret = settings.SECRET_KEY

    def make_token(self, member, expiry=None):
        """
        Return a token that can be used once to do a password reset
        for the given member.

        Args:
            member (Model): the member
            expiry (datetime): optional forced expiry date

        Returns:
             (tuple): tuple containing:
                token (str): the token
                expiry (datetime): the expiry datetime
        """
        if expiry is None:
            return self._make_token_with_timestamp(member, self._num_seconds(self._now()))
        return self._make_token_with_timestamp(member, self._num_seconds(expiry) - settings.EMAIL_TOKEN_LIFE)

    def check_token(self, token):
        """
        Check that a password reset token is correct.
        Args:
            token (str): the token from the url

        Returns:
            (tuple): tuple containing:
                valid (bool): True if the token is valid
                member (Model): the member model if the token is valid
        """
        from utils.member_utils import get_member_model
        try:
            email_b64, ts_b36, _ = token.split("-")
            email = urlsafe_base64_decode(email_b64).decode()
            # member = get_user_model().objects.get(email=email)
            member = get_member_model().objects.get(email=email)
            ts = base36_to_int(ts_b36)
        except (ValueError, get_member_model().DoesNotExist):
            return False, None

        if not constant_time_compare(self._make_token_with_timestamp(member, ts)[0], token):
            return False, None

        now = self._now()
        if (self._num_seconds(now) - ts) > settings.EMAIL_TOKEN_LIFE:
            return False, None

        return True, member

    def _make_token_with_timestamp(self, member, timestamp):
        email_b64 = urlsafe_base64_encode(member.email.encode())
        ts_b36 = int_to_base36(timestamp)
        hash_string = salted_hmac(
            self.key_salt,
            self._make_hash_value(member, timestamp),
            secret=self.secret,
        ).hexdigest()
        return f'{email_b64}-{ts_b36}-{hash_string}', \
               datetime.fromtimestamp(timestamp + settings.EMAIL_TOKEN_LIFE)

    @staticmethod
    def _make_hash_value(member, timestamp):
        login_timestamp = '' if member.login_date is None else member.login_date.replace(microsecond=0, tzinfo=None)
        return str(member.pk) + member.password + str(login_timestamp) + str(timestamp)

    @staticmethod
    def _num_seconds(dt):
        return int((dt - datetime(2001, 1, 1)).total_seconds())

    @staticmethod
    def _now():
        return datetime.now()


default_token_generator = EmailVerificationTokenGenerator()
