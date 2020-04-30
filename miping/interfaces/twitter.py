import tweepy
import time

from ..models import TweetObj
from ..models import TweetCollection


class TwitterAPI:
    """
    TODO docstring Class Twitter
    """

    def __init__(
        self,
        consumer_key,
        consumer_secret,
        access_token=None,
        access_token_secret=None,
        wait_on_rate_limit=True,
        wait_on_rate_limit_notify=True,
        additionalAttributes=None,
        removeNewLineChar=True,
        ignoreRetweets=True
    ):
        """
        TODO init func Class Twitter, check which keys are mandatory
        """

        if access_token is None or access_token_secret is None:
            # no user token supplied (only app context possible)
            auth = tweepy.AppAuthHandler(consumer_key, consumer_secret)
            self.api = tweepy.API(
                auth,
                wait_on_rate_limit=wait_on_rate_limit,
                wait_on_rate_limit_notify=wait_on_rate_limit_notify
            )
            # streaming is not possible
            self.streaming_enabled = False
        else:
            # tokens are supplied, we will do authentication
            # with user context
            auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
            auth.set_access_token(access_token, access_token_secret)
            self.api = tweepy.API(
                auth,
                wait_on_rate_limit=wait_on_rate_limit,
                wait_on_rate_limit_notify=wait_on_rate_limit_notify
            )
            # streaming is possible
            self.streaming_enabled = True

        print("Twitter API initialized")
        print("Streaming value: " + str(self.streaming_enabled))

        self.additionalAttributes = additionalAttributes
        self.removeNewLineChar = removeNewLineChar
        self.ignoreRetweets = ignoreRetweets

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

                    # if it's a retweet, we check if we skip it
                    if hasattr(tweet, 'retweeted_status'):
                        if self.ignoreRetweets is True:
                            # skip this tweet, otherwise continue
                            continue

                    # convert to custom tweet object
                    twInstance = TweetObj(
                        tweet,
                        self.additionalAttributes,
                        self.removeNewLineChar
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
        chunks = [
            idList[x:x+apiChunks] for x in range(0, len(idList), apiChunks)
        ]

        # for each 100er chunk, we will perform an API request
        for chunkList in chunks:
            # get all tweets in given id list
            # omit those we cannot retrieve (via map_)
            # (e.g. deleted or private)
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
                    self.additionalAttributes,
                    self.removeNewLineChar
                )
                # add tweet to collection
                tweetCol.funcAddTweet(twInstance)

        # calculate number of invalid ids
        invalidIDs = (listLength - len(tweetCol.tweetList))

        return tweetCol, invalidIDs

    def get_followers_of_user(
        self,
        userID,
    ):
        """
        TODO doctstring get_followers_of_user
        """
        pass

    def stream_tweets_by_location(
        self,
        location,
        timeLimit=5,
    ):
        """
        TODO docstring stream_tweets_by_location
        timeLimit in seconds

        location
        # southwest corner of the bounding box coming first
        # order longitude (Länge), latitude (Breite)
        """

        # holds tweets with attributes as TweetObj
        # passed in streamListener to save tweets
        tweetCol = TweetCollection(self.additionalAttributes)

        if self.streaming_enabled is False:
            print(
                "Streaming tweets is disabled. " +
                "Function stream_tweets_by_location."
            )
            return

        print("Time limit is set to: " + str(timeLimit))

        # build stream objects
        myStreamListener = _MyStreamListener(
            tweetCollect=tweetCol,
            additionalAttributes=self.additionalAttributes,
            time_limit=timeLimit
        )
        myStream = tweepy.Stream(
            auth=self.api.auth,
            listener=myStreamListener
        )

        # get tweets based on coordinates
        myStream.filter(locations=location)

        # after timeout we can return collected tweets
        return myStreamListener.tweetCollect


class _MyStreamListener(
    tweepy.StreamListener
):
    """
    TODO docstring _MyStreamListener
    """
    def __init__(
        self,
        tweetCollect,
        additionalAttributes,
        time_limit=10,
        removeNewLineChar=True,
        ignoreRetweets=True
    ):
        """
        TODO docstring __init__
        """
        # set time for time limit
        self.start_time = time.time()
        self.limit = time_limit

        self.tweetCollect = tweetCollect
        self.additionalAttributes = additionalAttributes

        self.removeNewLineChar = removeNewLineChar
        self.ignoreRetweets = ignoreRetweets

        super(_MyStreamListener, self).__init__()

    def on_status(
        self,
        tweet
    ):
        """
        TODO docstring on_status
        """
        # check time limit
        if (time.time() - self.start_time) < self.limit:
            # convert incoming tweet to custom tweet object
            twInstance = TweetObj(
                tweet,
                self.additionalAttributes,
                self.removeNewLineChar
            )
            # add tweet to collection
            self.tweetCollect.funcAddTweet(twInstance)
            return True
        else:
            # time is up
            # returning false will end stream
            print('Ending stream')
            return False

    def on_error(
        self,
        status_code
    ):
        """
        TODO docstring on_error
        """
        print("Error while streaming with status code:")
        print(status_code)
        return False
