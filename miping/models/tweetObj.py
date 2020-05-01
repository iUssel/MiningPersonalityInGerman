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
            str(self.user_id)
        )
        return returnString

    def __init__(
        self,
        tweepyStatus=None,
        additionalAttributeList=None,
        removeNewLineChar=True
    ):
        """
        TODO init func Class TweetObj maybe reduce complexity
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
                # if it has attribute full_text, take that
                if hasattr(tweepyStatus.retweeted_status, 'full_text'):
                    self.text = tweepyStatus.retweeted_status.full_text
                elif hasattr(tweepyStatus, 'extended_tweet'):
                    self.text = tweepyStatus.extended_tweet['full_text']
                else:
                    self.text = tweepyStatus.retweeted_status.text
            else:
                self.isRetweet = 0
                # if it has attribute full_text, take that
                if hasattr(tweepyStatus, 'full_text'):
                    self.text = tweepyStatus.full_text
                elif hasattr(tweepyStatus, 'extended_tweet'):
                    self.text = tweepyStatus.extended_tweet['full_text']
                else:
                    self.text = tweepyStatus.text

            # now that text if filled, we will remove new line chars
            if removeNewLineChar is True:
                self.text = self.text.replace("\n", " ")
                self.text = self.text.replace("\r", " ")

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

        return
