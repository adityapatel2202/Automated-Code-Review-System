def current_user(self):
        """Retrieve the user ID of the current user talking to your bot.

        This is mostly useful inside of a Python object macro to get the user
        ID of the person who caused the object macro to be invoked (i.e. to
        set a variable for that user from within the object).

        This will return ``None`` if used outside of the context of getting a
        reply (the value is unset at the end of the ``reply()`` method).
        """
        if self._brain._current_user is None:
            # They're doing it wrong.
            self._warn("current_user() is meant to be used from within a Python object macro!")
        return self._brain._current_user