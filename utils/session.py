from enum import Enum


class AuthStates(Enum):
    FORM = "form"
    AUTHENTICATED = "authenticated"
    LOGGED_OUT = "logout"
    LOADING = "loading"

class FeedbackState(Enum):
    NONE = "none"
    LINK_SENT = "vinculo_enviado"
    LINK_ERROR = "erro_envio"
    LINK_ACCEPTED = "link_accepted"
    LINK_REJECTED = "link_rejected"
    GOAL_SENT = "goal_sent"