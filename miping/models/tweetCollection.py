import csv
from .tweetObj import TweetObj


class TweetCollection:
    """
    Data model for a collection of TweetObjs
    """

    def __init__(
        self,
        additionalAttributes=None
    ):
        """
        Initialize empty tweetList and save if there
        are additionalAttributes.
        """
        # initialize empty list to collect tweets
        self.tweetList = []

        # if any attributes are given, add them
        if additionalAttributes is not None:
            self.additionalAttributes = additionalAttributes
            self.addAttrBool = True
        else:
            self.addAttrBool = False

    def funcAddTweet(
        self,
        tweetObj: TweetObj,
    ):
        """
        Add tweetObj to tweetList.
        """

        self.tweetList.append(tweetObj)

        return

    def add_tweet_collection(
        self,
        tweetCol,
    ):
        """
        Add tweetCollection to tweetlist by extending it.
        """
        self.tweetList.extend(tweetCol.tweetList)

        return

    def write_tweet_list_file(
        self,
        full_path='tweetlist.csv',
        ids_only=False
    ):
        """
        Export objects in tweetlist to CSV file.

        Parameters
        ----------
        full_path : string, default='tweetlist.csv'
            Full path for export file.
        ids_only : boolean, default=False
            If True only one column for ids will be written.
        """
        # write output csv file
        with open(full_path, "w", newline='', encoding='utf-8') as outfile:
            # initialize csv writer
            writer = csv.writer(
                outfile,
                delimiter=',',
                quotechar='"',
                quoting=csv.QUOTE_MINIMAL
            )
            # write a row for each tweet
            for entries in self.tweetList:
                basicList = []
                basicList.append(entries.id_str)

                # only if bool is true, we write more than ID
                if ids_only is False:
                    basicList.append(entries.created_at)
                    basicList.append(entries.user_id)
                    basicList.append(entries.isRetweet)
                    basicList.append(entries.text)
                    # if additional attributes are given
                    # add them to list
                    if self.addAttrBool:
                        attrList = []
                        for attr in self.additionalAttributes:
                            attrList.append((getattr(entries, attr)))
                        # extend basicList
                        basicList.extend(attrList)

                writer.writerow(basicList)

        return

    def read_tweet_list_file(
        self,
        full_path='tweetlist.csv',
        ids_only=False,
        removeNewLineChar=True,
    ):
        """
        Import tweet objects to tweetlist from CSV file.

        Parameters
        ----------
        full_path : string, default='tweetlist.csv'
            Full path for import file.
        ids_only : boolean, default=False
            If True only one column for ids will be written.
        removeNewLineChar : boolean, default=True
            Remove new line characters from texts in tweets.
        """

        # read csv file
        with open(full_path, "r", newline='', encoding='utf-8') as infile:
            # initialize csv reader
            reader = csv.reader(
                infile,
                delimiter=',',
                quotechar='"',
                quoting=csv.QUOTE_MINIMAL
            )
            for row in reader:
                # convert to custom tweet object
                twInstance = TweetObj(removeNewLineChar=removeNewLineChar)
                twInstance.id_str = row[0]

                # only if False, we read other attributes
                if ids_only is False:
                    twInstance.created_at = row[1]
                    twInstance.user_id = row[2]
                    twInstance.isRetweet = row[3]

                    twInstance.text = row[4]
                    if removeNewLineChar is True:
                        # if setted, we will remove new line chars
                        twInstance.text = twInstance.text.replace("\n", " ")
                        twInstance.text = twInstance.text.replace("\r", " ")

                    if self.addAttrBool:
                        # if there are additional attributes
                        # we will read them column by column
                        # starting with index 5
                        # (the 6th column in 0 based index)
                        for num, attr in enumerate(self.additionalAttributes):
                            setattr(twInstance, attr, row[num+5])

                # add tweet to collection
                self.funcAddTweet(twInstance)

    def get_id_list(
        self,
    ):
        """
        Return list of tweet ids in tweetlist.
        """

        idList = list(tweets.id_str for tweets in self.tweetList)

        return idList

    def get_distinct_user_id_list(
        self,
    ):
        """
        Return list of distinct user ids in tweetlist.
        """

        # get user ids from tweets
        idList = list(tweets.user_id for tweets in self.tweetList)

        # remove duplicate user ids
        userIDList = list(dict.fromkeys(idList))

        return userIDList

    def get_tweets_of_userid(
        self,
        userID
    ):
        """
        Extract tweets from tweetlist written by given userID.

        Parameters
        ----------
        userID : string, default=None, required
            UserID to get tweets for.

        Returns
        -------
        twCol : TweetCollection
            Another Tweetcollection containing only tweet from the given user.
        """
        # initialize new tweet collection
        if self.addAttrBool:
            twCol = TweetCollection(
                additionalAttributes=self.additionalAttributes
            )
        else:
            twCol = TweetCollection()

        # filter current tweet list to get only tweets
        # relevant to userID
        userTweetList = [
            tweet for tweet in self.tweetList if tweet.user_id == userID
        ]

        # assign filtered list to new collection
        twCol.tweetList = userTweetList

        return twCol

    def combine_tweet_text(
        self,
    ):
        """
        Takes all tweets of tweetlist and combines the text in one string.
        Separated by space.
        """
        # join tweet texts with space in one string
        # it will access each tweets text attribute
        # of the tweetList
        totalText = ' '.join(tweet.text for tweet in self.tweetList)

        return totalText
