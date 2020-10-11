class UserNameError(Exception):
    """Raised if user name is not valid"""
    pass


class NotASuitableUserError(Exception):
    """Raised if user is not suitable (e.g. private or suspended)"""
    pass
