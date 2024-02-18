from rest_framework_simplejwt.tokens import RefreshToken

def blacklist_token(base64_encoded_token_string):
    token = RefreshToken(base64_encoded_token_string)
    token.blacklist()