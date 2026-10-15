from django.contrib.auth.backends import ModelBackend


class AllowInactiveLoginBackend(ModelBackend):
    """Shows the "This account is inactive." message on the login form.

    The default backend hides inactive accounts behind a generic "wrong
    password" error. Here they may reach the form's own check, but they are
    never kept signed in: `get_user` ignores inactive gamers.
    """

    def user_can_authenticate(self, user):
        return True

    def get_user(self, user_id):
        user = super().get_user(user_id)
        if user is not None and user.is_active:
            return user
        return None
