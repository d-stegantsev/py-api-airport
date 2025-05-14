from rest_framework.throttling import SimpleRateThrottle

class SignupRateThrottle(SimpleRateThrottle):
    scope = "signup"

class TokenRateThrottle(SimpleRateThrottle):
    scope = "token_obtain"