import tweepy
import time

from datetime import datetime

from ..models import TweetObj
from ..models import TweetCollection
from ..models import User
from ..models import UserCollection


class TwitterAPI:
    """
    Class to wrap Twitter API functions.
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
        Initialization function to establish Authentication.

        Depending on what access tokens are passed, streaming
        is enabled or disabled.

        Parameters
        ----------
        consumer_key : string, default=None, required
            Developer API key consumer key. Needed to query the Twitter API.
        consumer_secret : string, default=None, required
            Developer API key consumer key secret. Needed to query the
            Twitter API.
        access_token : string, default=None
            Developer API key, access token. Needed for streaming and
            user actions.
        access_token_secret : string, default=None
            Developer API key, access token secret. Needed for streaming and
            user actions.
        wait_on_rate_limit : boolean, default=True
            Will automatically wait if rate limit is reached.
        wait_on_rate_limit_notify : boolean, default=True
            Passed to Tweepy. Prints warning if rate limit is reached.
        additionalAttributes : list, default=None
            Additional attributes that should be included when querying
            tweets. Such as 'lang' attribute, for language.
            Usually configured in global config file.
        removeNewLineChar : boolean, default=True
            Remove new line characters (\n or \r) from tweet texts.
            This is useful for CSV exports
        ignoreRetweets : boolean, default=True
            For all tweet queries exclude retweets.

        Returns
        -------
        config : dict
            The parsed dict containing all config values.
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
        Return corresponding user id to screen_name.

        Parameters
        ----------
        screen_name : string, default=None, required
            Twitter user name.

        Returns
        -------
        user.id_str : string
            User id fitting the screen_name.
        """
        user = self.api.get_user(screen_name=screen_name)

        return user.id_str

    def getUsersByList(
        self,
        userIDList,
        maxFollowerCount=0,
        minStatusesCount=0,
        minFollowerCount=0,
        skipPrivateUsers=True,
    ):
        """
        Select users based in passed user id list and given criteria.

        With the passed user id list, user objects are retrieved and
        tested against the criteria. If users match the criteria,
        a new user object is created and included in the return user
        collection.

        Parameters
        ----------
        userIDList : list, default=None
            List of strings of user ids.
        maxFollowerCount : integer, default=0
            Selection criteria - if user has more than given number
            of maximum follower, he/she is excluded. If 0, not applied.
        minStatusesCount : integer, default=0
            Selection criteria - if user has less than minimum number
            of status counts, he/she is excluded. If 0, not applied.
        minFollowerCount : integer, default=0
            Selection criteria - if user has less than minimum number
            of followers, he/she is excluded. If 0, not applied.
        skipPrivateUsers : boolean, default=True
            Protected user accounts are not accessible to the public,
            so usually those should be excluded.

        Returns
        -------
        userCol : UserCollection
            User collection of user objects fitting the passed
            user id list.
        """
        userCol = UserCollection()

        # twitter's API acceppts only 100 users at a time
        # so we split our given list in 100er chunks
        apiPart = 100
        chunks = [
            userIDList[x:x+apiPart] for x in range(0, len(userIDList), apiPart)
        ]

        # for all IDs in list, get the user object
        # for each 100er chunk, we will perform an API request
        for chunkList in chunks:
            # get all users in given id list
            result = self.api.lookup_users(
                user_ids=chunkList,
            )

            for userIter in result:
                if userIter.protected is True and skipPrivateUsers is True:
                    # skip private/protected users
                    continue
                # if set, we will check the user requirements
                # follower count and statuses count
                if minStatusesCount > 0:
                    # check for number of statuses
                    if userIter.statuses_count < minStatusesCount:
                        # user does not have necessary number of tweets
                        # skip this user, otherwise continue
                        continue

                if maxFollowerCount > 0:
                    # check for number of followers
                    if userIter.followers_count > maxFollowerCount:
                        # user has too many followers
                        # skip this user, otherwise continue
                        continue

                if maxFollowerCount > 0:
                    # check for number of followers
                    if userIter.followers_count < minFollowerCount:
                        # user has too few followers
                        # skip this user, otherwise continue
                        continue

                # convert incoming user to custom tweet object
                userInstance = User(
                    userIter,
                )
                # add user to collection
                userCol.funcAddUser(userInstance)

        return userCol

    def funcGetTweetListByUser(
        self,
        userID,
        limit=0,
        reRaiseExceptions=False,
    ):
        """
        Get tweets for given user id and return TweetCollection.

        Parameters
        ----------
        userID : string, default=None, required
            user id to get tweets for.
        limit : integer, default=0
            Limit tweets to retrieve. Limit = 0 means no limit.
            Free API limit including retweets is 3200.
        reRaiseExceptions : boolean, default=False
            If exceptions are encountered, reRaise them.

        Returns
        -------
        tweetCol : TweetCollection
            TweetCollection containing retrieved tweets for given
            user id. Will be empty if error occured and reRaise is False.
        """

        # holds tweets with attributes as TweetObj
        tweetCol = TweetCollection(self.additionalAttributes)

        # check if user exists
        try:
            self.api.get_user(user_id=userID)
        except tweepy.error.TweepError as e:
            if reRaiseExceptions is True:
                raise(e)
            else:
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
                    tweet_mode='extended',
                    include_rts=(not self.ignoreRetweets),
                    count=200  # API allows up to 200 tweets per request
                ).items(limit):

                    # if it's a retweet, we check if we skip it
                    if hasattr(tweet, 'retweeted_status'):
                        if self.ignoreRetweets is True:
                            # skip this tweet, otherwise add tweet to list
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
                if reRaiseExceptions is True:
                    raise(e)
                else:
                    print("An error occured, probably your user is private.")
                    print(str(e))

        return tweetCol

    def get_tweets_by_list(
        self,
        idList,
        limit=0,
    ):
        """
        Get tweet object for list of tweet ids and return collection.

        Parameters
        ----------
        idList : list, default=None, required
            List of tweet ids to hydrate.
        limit : integer, default=0
            Obsolete - exists for historic reasons.

        Returns
        -------
        tweetCol : TweetCollection
            TweetCollection with tweets for tweet ids.
        invalidIDs : integer
            Number of invalid IDs.
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

                # if it's a retweet, we check if we skip it
                if hasattr(tweet, 'retweeted_status'):
                    if self.ignoreRetweets is True:
                        # skip this tweet, otherwise add tweet to list
                        continue

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
        userIDList,
        limit=0
    ):
        """
        Get user ids of followers for given user ids in list.

        Parameters
        ----------
        userIDList : list, default=None, required
            List of user ids to get followers from.
        limit : integer, default=0
            Number of followers to get for each user id.
            5000 is recommended, as the Twitter API returns 5000
            followers per request per user.
            0 means no limit.

        Returns
        -------
        followerIDs : list
            List of user ids of followers.
        """

        followerIDs = []
        sleepTime = 900

        # twitter's API limits us to 15 calls
        # so we split our given list in 15er chunks
        # after that we need to wait 15 minutes
        # this prevents timeouts of the connection
        apiPart = 15
        chunks = [
            userIDList[x:x+apiPart] for x in range(0, len(userIDList), apiPart)
        ]
        chunkLen = len(chunks)

        # for all IDs in list, get followers
        # for each 15er chunk, we will perform an API request
        # and sleep afterwards
        for num, chunkList in enumerate(chunks):
            for userID in chunkList:
                # get follower ids of specified user
                for user in tweepy.Cursor(
                    self.api.followers_ids,
                    user_id=userID,
                ).items(limit):
                    # add ID to list
                    followerIDs.append(str(user))
            if ((num + 1) < chunkLen):
                # num is 0 based index
                # if we have another chunk waiting, we need to sleep
                # to comply with API limit
                print(
                    "Rate limit reached for Followers. Sleeping for: " +
                    str(sleepTime)
                )
                # print current time
                now = datetime.now()
                current_time = now.strftime("%H:%M:%S")
                print("Current Time =", current_time)
                # sleep for 15 minutes
                # necessary to avoid timeouts in tweepy
                time.sleep(sleepTime)

        return followerIDs

    def stream_tweets_by_location(
        self,
        location,
        timeLimit=5,
        maxFollowerCount=0,
        minStatusesCount=0,
        minFollowerCount=0,
    ):
        """
        Get live tweet via streaming API matching location and other criteria.

        Parameters
        ----------
        location : list, default=None, required
            List of location GPS coordinates that should be passed as filter
            to streaming API. Following structure is expected (start with
            southwest corner):
            location = [
                    countryConf['southwest']['lng'],
                    countryConf['southwest']['lat'],
                    countryConf['northeast']['lng'],
                    countryConf['northeast']['lat']
            ]
        timeLimit : integer, default=5
            Time in seconds the stream will be running.
        maxFollowerCount : integer, default=0
            Selection criteria - if user has more than given number
            of maximum follower, he/she is excluded. If 0, not applied.
        minStatusesCount : integer, default=0
            Selection criteria - if user has less than minimum number
            of status counts, he/she is excluded. If 0, not applied.
        minFollowerCount : integer, default=0
            Selection criteria - if user has less than minimum number
            of followers, he/she is excluded. If 0, not applied.

        Returns
        -------
        myStreamListener.tweetCollect : TweetCollection
            All tweets that were streamed during the time limit and matched
            the given criteria.
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
            time_limit=timeLimit,
            removeNewLineChar=self.removeNewLineChar,
            ignoreRetweets=self.ignoreRetweets,
            maxFollowerCount=maxFollowerCount,
            minStatusesCount=minStatusesCount,
            minFollowerCount=minFollowerCount,
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
    Private class stream listener for wrapping streaming functions
    """
    def __init__(
        self,
        tweetCollect,
        additionalAttributes,
        time_limit=10,
        removeNewLineChar=True,
        ignoreRetweets=True,
        maxFollowerCount=0,
        minStatusesCount=0,
        minFollowerCount=0,
    ):
        """
        Init function for streamer class
        """
        # set time for time limit
        self.start_time = time.time()
        self.limit = time_limit

        self.tweetCollect = tweetCollect
        self.additionalAttributes = additionalAttributes

        self.removeNewLineChar = removeNewLineChar
        self.ignoreRetweets = ignoreRetweets

        self.maxFollowerCount = maxFollowerCount
        self.minStatusesCount = minStatusesCount
        self.minFollowerCount = minFollowerCount

        # keep track of how many tweets we skip
        self.skipFollowerCounter = 0
        self.skipStatusesCounter = 0

        super(_MyStreamListener, self).__init__()

    def on_status(
        self,
        tweet
    ):
        """
        Function that is run on each streamed tweet.
        Checks criteria and saves to TweetCollection.
        """
        # check time limit
        if (time.time() - self.start_time) < self.limit:
            # if it's a retweet, we check if we skip it
            if hasattr(tweet, 'retweeted_status'):
                if self.ignoreRetweets is True:
                    # skip this tweet, otherwise continue
                    return True

            # if set, we will check the user requirements
            # follower count and statuses count
            if self.minStatusesCount > 0:
                # check for number of statuses
                if tweet.user.statuses_count < self.minStatusesCount:
                    # user does not have necessary number of tweets
                    # skip this tweet, otherwise continue
                    self.skipStatusesCounter = self.skipStatusesCounter + 1
                    return True

            if self.maxFollowerCount > 0:
                # check for number of followers
                if tweet.user.followers_count > self.maxFollowerCount:
                    # user has too many followers
                    # skip this tweet, otherwise continue
                    self.skipFollowerCounter = self.skipFollowerCounter + 1
                    return True

            if self.minFollowerCount > 0:
                # check of number of minimum followers
                if tweet.user.followers_count < self.minFollowerCount:
                    # user has too few followers
                    # skip this tweet, otherwise continue
                    self.skipFollowerCounter = self.skipFollowerCounter + 1
                    return True

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
            print(
                "Skipped " +
                str(self.skipStatusesCounter) +
                " tweet(s) because user has to few tweets" +
                " and skipped " +
                str(self.skipFollowerCounter) +
                " tweet(s) because user has too many followers."
            )
            return False

    def on_error(
        self,
        status_code
    ):
        """
        Called for handling errors in streaming.
        """
        print("Error while streaming with status code:")
        print(status_code)
        return False
