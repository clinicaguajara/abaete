from enum import Enum

class AuthStates(Enum):
    FORM = "form"
    AUTHENTICATED = "authenticated"
    LOGGED_OUT = "logout"

class LoadStates(Enum):
    LOAD = True
    LOADING = "loading"
    LOADED = False


class VerifyStates(Enum):
    VERIFY = True
    VERIFYING = "verifying"
    VERIFIED = False


class FeedbackStates(Enum):
    CLEAR = None
    SHOW = True
    DONE = False
    ACCEPTED = "accepted"
    REJECTED = "rejected"


class RedirectStates(Enum):
    REDIRECT = True
    REDIRECTED = False


class EvaluationStates(Enum):
    START = "start"
    FORM = "form"
    DONE = False
    LOADING = "loading"