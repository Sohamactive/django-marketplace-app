import jwt
import requests
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend
from django.conf import settings
from jose import jwk
from jose.utils import base64url_decode
from cryptography.hazmat.primitives import serialization
import binascii

class Auth0Backend(BaseBackend):
    def authenticate(self, request, token=None):
        if not token:
            return None

        # Fetch JWKS from Auth0
        jwks = requests.get(f'{settings.AUTH0_ISSUER}.well-known/jwks.json').json()
        unverified_header = jwt.get_unverified_header(token)

        # Find the matching key in JWKS
        rsa_key = None
        for key in jwks['keys']:
            if key['kid'] == unverified_header['kid']:
                rsa_key = key
                break

        if not rsa_key:
            print("No matching key found in JWKS")
            return None

        try:
            # Convert JWKS to public key
            public_key = jwt.algorithms.RSAAlgorithm.from_jwk(rsa_key)

            # Convert public key to PEM format
            pem_key = public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            ).decode('utf-8')

            # Decode the JWT token
            payload = jwt.decode(
                token,
                pem_key,
                algorithms=['RS256'],
                audience=settings.AUTH0_CLIENT_ID,
                issuer=f"https://{settings.AUTH0_DOMAIN}/",
                leeway=300  # Allows 5 minutes clock skew
            )

            # Get or create user
            User = get_user_model()
            user, created = User.objects.get_or_create(
                username=payload['sub'],  # Use Auth0's unique sub ID
                defaults={'email': payload.get('email', '')}
            )
            return user
        except (jwt.InvalidTokenError, binascii.Error, ValueError) as e:
            print(f"JWT Error: {str(e)}")
            return None

    def get_user(self, user_id):
        User = get_user_model()
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

