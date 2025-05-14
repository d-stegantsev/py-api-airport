from rest_framework.throttling import SimpleRateThrottle

class SignupRateThrottle(SimpleRateThrottle):
    scope = "signup"

    def get_cache_key(self, request, view):
        return self.get_ident(request)


class TokenRateThrottle(SimpleRateThrottle):
    scope = "token_obtain"

    def get_cache_key(self, request, view):
        return self.get_ident(request)
