import tweepy

from ..models import TweetObj
from ..models import TweetCollection

from itertools import zip_longest


class TwitterAPI:
    """
    TODO docstring Class Twitter
    """

    def __init__(
        self,
        consumer_key,
        consumer_secret,
        wait_on_rate_limit=True,
        wait_on_rate_limit_notify=True,
        additionalAttributes=None,
    ):
        """
        TODO init func Class Twitter, check which keys are mandatory
        """
        print("Hello Twitter")

        auth = tweepy.AppAuthHandler(consumer_key, consumer_secret)
        self.api = tweepy.API(
            auth,
            wait_on_rate_limit=wait_on_rate_limit,
            wait_on_rate_limit_notify=wait_on_rate_limit_notify
        )

        self.additionalAttributes = additionalAttributes

    def funcGetUserID(
        self,
        screen_name,
    ):
        """
        TODO docstring funcGetUserID
        """
        user = self.api.get_user(screen_name=screen_name)

        return user.id_str

    def funcGetTweetListByUser(
        self,
        userID,
        limit=0,
    ):
        """
        TODO docstring funcGetTweetListByUser
        Return id list and tweet col
        limit=0 -> no limit

        will be empty if error occured
        """

        # holds tweets with attributes as TweetObj
        tweetCol = TweetCollection(self.additionalAttributes)

        # check if user exists
        try:
            self.api.get_user(user_id=userID)
        except tweepy.error.TweepError as e:
            print("An error occured, probably your user does not exist.")
            print(str(e))
        else:
            # check if getting tweets is possible
            # private users will raise an exception
            try:
                # loop over all tweets in user timeline
                for tweet in tweepy.Cursor(
                    self.api.user_timeline,
                    user_id=userID,
                    tweet_mode='extended'
                ).items(limit):

                    # convert to custom tweet object
                    twInstance = TweetObj(
                        tweet,
                        self.additionalAttributes
                    )
                    # add tweet to collection
                    tweetCol.funcAddTweet(twInstance)

            except tweepy.error.TweepError as e:
                print("An error occured, probably your user is private.")
                print(str(e))

        return tweetCol

    def get_tweets_by_list(
        self,
        idList,
        limit=0,
    ):
        """
        TODO docstring get_tweets_by_list
        """

        # list length for error count
        listLength = len(idList)

        apiChunks = 100

        # holds tweets with attributes as TweetObj
        tweetCol = TweetCollection(self.additionalAttributes)

        # twitter's API acceppts only 100 tweets at a time
        # so we split our given list in 100er chunks
        chunks = [idList[x:x+apiChunks] for x in range(0, len(idList), apiChunks)]

        # for each 100er chunk, we will perform an API request
        for chunkList in chunks:
            # get all tweets in given id list
            # omit those we cannot retrieve (via map_) (e.g. deleted or private)
            result = self.api.statuses_lookup(
                id_=chunkList,
                trim_user=True,
                map_=False,
                tweet_mode='extended',
            )
            
            for tweet in result:           
                # convert to custom tweet object
                twInstance = TweetObj(
                    tweet,
                    self.additionalAttributes
                )
                # add tweet to collection
                tweetCol.funcAddTweet(twInstance)

        # calculate number of invalid ids
        invalidIDs = (listLength - len(tweetCol.tweetList))

        return tweetCol, invalidIDs
