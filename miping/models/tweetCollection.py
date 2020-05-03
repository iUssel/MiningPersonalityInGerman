import csv
from .tweetObj import TweetObj


class TweetCollection:
    """
    TODO docstring Class TweetCollection
    """

    def __init__(
        self,
        additionalAttributes=None
    ):
        """
        TODO init func Class TweetCollection
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
        TODO funcAddTweet
        """

        self.tweetList.append(tweetObj)

        return

    def add_tweet_collection(
        self,
        tweetCol,
    ):
        """
        TODO add_tweet_collection
        """
        self.tweetList.extend(tweetCol.tweetList)

        return

    def write_tweet_list_file(
        self,
        full_path='tweetlist.csv',
        ids_only=False
    ):
        """
        TODO docstring write_tweet_list_file
        Write all from tweet list to file

        if ids_only True it will write only one column
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
        TODO docstring read_tweet_list_file
        Read all tweets from tweet list file
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
        TODO docstring get_id_list
        Return list with ids of list
        """

        idList = list(tweets.id_str for tweets in self.tweetList)

        return idList

    def get_distinct_user_id_list(
        self,
    ):
        """
        TODO docstring get_distinct_user_id_list
        """

        # get user ids from tweets
        idList = list(tweets.user_id for tweets in self.tweetList)

        # remove duplicate user ids
        userIDList = list(dict.fromkeys(idList))

        return userIDList
