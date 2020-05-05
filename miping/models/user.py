class User:
    """
    TODO docstring Class user
    """

    def __str__(
        self
    ):
        """
        TODO ensuring that printing the object, prints id
        """
        returnString = (
            "User with ID " +
            self.id_str +
            " and screen_name " +
            str(self.screen_name)
        )
        return returnString

    def __init__(
        self,
        user_entity=None,
    ):
        """
        TODO init func Class user
        Creates user object, which can be manually filled
        or via init function
        """

        if user_entity is not None:
            self.id_str = user_entity.id_str
            self.screen_name = user_entity.screen_name
            self.followers = user_entity.followers_count
            self.tweet_count = user_entity.statuses_count

            # remove any new line char from location
            # this is confusing in csv files
            location = user_entity.location
            location = location.replace("\n", " ")
            location = location.replace("\r", " ")
            # coordinates work not well with google api
            location = location.replace("°","")
            location = location.replace('.', ' ')
            self.location = location

        else:
            # initialize empty values
            self.id_str = None
            self.screen_name = None
            self.followers = None
            self.tweet_count = None
            self.location = None

        return
