class TweetObj:
    """
    TODO docstring Class TweetObj
    """

    def __str__(
        self
    ):
        """
        TODO ensuring that printing the object, prints id
        """
        returnString = (
            "TweetObj with ID " +
            self.id_str +
            " and User ID " +
            self.user_id
        )
        return returnString

    def __init__(
        self,
        tweepyStatus=None,
        additionalAttributeList=None,
    ):
        """
        TODO init func Class TweetObj
        Creates tweetObj, which can be manually filled
        or via init function
        """

        if tweepyStatus is not None:
            self.id_str = tweepyStatus.id_str
            self.created_at = tweepyStatus.created_at

            self.user_id = tweepyStatus.author.id_str

            # is retweet? and text
            if hasattr(tweepyStatus, 'retweeted_status'):
                self.isRetweet = 1
                self.text = tweepyStatus.retweeted_status.full_text
            else:
                self.isRetweet = 0
                self.text = tweepyStatus.full_text

            # if any attributes are given, add them
            if additionalAttributeList is not None:
                for attr in additionalAttributeList:
                    value = getattr(tweepyStatus, attr)
                    if value is None:
                        # it is easier to handle empty strings
                        value = ''
                    setattr(self, attr, value)

        else:
            # initialize empty values
            self.id_str = None
            self.created_at = None
            self.user_id = None
            self.isRetweet = None
            self.text = None
            if additionalAttributeList is not None:
                for attr in additionalAttributeList:
                    setattr(self, attr, None)