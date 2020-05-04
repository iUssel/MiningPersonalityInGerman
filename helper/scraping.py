import random

from pathlib import Path
from miping.models.tweetCollection import TweetCollection
from miping.models.userCollection import UserCollection


class Scraping:
    """
    TODO docstring Class Scraping
    coordinates the initial scraping of streaming data from twitter
    """

    def __init__(
        self,
        config,
        twitter,
        maps=None,
    ):
        """
        TODO init func Class Scraping
        config of main
        initialized twitter class

        """
        self.config = config

        self.twitter = twitter

        self.maps = maps

    def doScrapingByLocation(
        self,
        readFiles=False,
        writeFiles=False,
    ):
        """
        TODO  docstring doScrapingByLocation

        return dict of [tweetCollection] (by country)
        """
        if writeFiles is True and readFiles is True:
            raise Exception(
                "readFiles and writeFiles cannot be True at the same time."
            )
        # if we scrape data for multiple countries
        # we will gather them in this list
        returnDictCollection = {}

        if readFiles is True:
            print("\nReading files for scraping by location")

            # for each country we need to read the file
            for country in self.config['twitter']['coordinates']:
                # getting coordinates for streaming
                countryConf = self.config['twitter']['coordinates'][country]

                print(
                    "Loading for country: " +
                    countryConf['name']
                )

                # path for saved tweets
                file_directory_string = (
                    'data/01streamed' +
                    countryConf['name'] +
                    'tweet.csv'
                )
                file_path = Path(file_directory_string)

                scrapedTweets = TweetCollection(
                    additionalAttributes=(
                        self.config["twitter"]["add_attributes"]
                    )
                )
                scrapedTweets.read_tweet_list_file(
                    full_path=file_path
                )

            # add collection to dict
            returnDictCollection[countryConf['name']] = scrapedTweets

            print("Files successfully loaded")
        else:
            print("\nBegin scraping by location")
            for country in self.config['twitter']['coordinates']:
                # getting coordinates for streaming
                countryConf = self.config['twitter']['coordinates'][country]

                location = [
                    countryConf['southwest']['lng'],
                    countryConf['southwest']['lat'],
                    countryConf['northeast']['lng'],
                    countryConf['northeast']['lat']
                ]
                print(
                    "Streaming for country: " +
                    countryConf['name']
                )

                scrapeConfig = self.config['scraping']
                scrapedTweets = self.twitter.stream_tweets_by_location(
                    location=location,
                    timeLimit=scrapeConfig['timer'],
                    maxFollowerCount=scrapeConfig['user_max_followers'],
                    minStatusesCount=scrapeConfig['users_min_tweet_no'],
                )

                # only write file if specified
                if writeFiles is True:
                    # path for saving tweets
                    file_directory_string = (
                        'data/01streamed' +
                        countryConf['name'] +
                        'tweet.csv'
                    )
                    file_path = Path(file_directory_string)

                    scrapedTweets.write_tweet_list_file(
                        full_path=file_path
                    )

            # add collection to dict
            returnDictCollection[countryConf['name']] = scrapedTweets
            print("End scraping by location")

        return returnDictCollection

    def doFollowerSelection(
        self,
        tweetSampleCol,
        countryName,
        readFiles=False,
        writeFiles=False,
    ):
        """
        TODO  docstring doFollowerSelection

        tweetSampleCol contains users that are already in the right
        location, have the right number of tweets and followers

        returns locationScrapedUsersCol, eligibleFollowersCol
        """
        if writeFiles is True and readFiles is True:
            raise Exception(
                "readFiles and writeFiles cannot be True at the same time."
            )

        if readFiles is True:
            print("\nReading files for Follower Selection")
            print(
                    "Loading for country: " +
                    countryName
                )

            # path for saved users
            file_directory_string = (
                    'data/02streamed' +
                    countryName
            )
            # users where we know the location
            file_path_loc = Path(
                    file_directory_string +
                    'users_location_verified.csv'
            )
            locationUsersCol = UserCollection()
            locationUsersCol.read_user_list_file(
                full_path=file_path_loc
            )

            file_path_fol = Path(
                    file_directory_string +
                    'users_location_follower.csv'
            )
            # selected followers, we need to verify location
            eligibleFollowersCol = UserCollection()
            eligibleFollowersCol.read_user_list_file(
                full_path=file_path_fol
            )

            print("Files successfully loaded")

        else:
            print("\nStart Follower Selection")
            scrapeConfig = self.config['scraping']
            sampling_follower = scrapeConfig['sampling_follower']

            print(
                'Will select followers from ' +
                str(sampling_follower) +
                ' users retrieved via location scraping. '
            )

            # retrieve user ids from tweets
            userList = tweetSampleCol.get_distinct_user_id_list()
            print(userList)
            # get users based on IDs
            # (follower and tweet count already ensured)
            locationUsersCol = self.twitter.getUsersByList(
                userIDList=userList
            )

            # get x random users from list
            # since API limit is limited (to 15 calls / 15 minutes)
            randList = self.getRandomItemsFromList(
                userList,
                sampling_follower
            )

            # get followers of scraped tweets/users
            followers = self.twitter.get_followers_of_user(
                userIDList=randList,
                limit=5000  # 5000 users are returned per API call
            )

            # remove duplicates inside follower list
            followers = list(set(followers))

            # remove duplicates from followers if
            # already in locationUsersCol
            # first get the ids apparent in both lists
            duplicates = set(userList).intersection(followers)
            # second only take the user id (idU) if it's not in 
            # the duplicate list
            followers = [idU for idU in followers if idU not in duplicates]

            # select eligible followers
            # tweet count and follower count will be checked
            eligibleFollowersCol = self.twitter.getUsersByList(
                userIDList=followers,
                maxFollowerCount=scrapeConfig['user_max_followers'],
                minStatusesCount=scrapeConfig['users_min_tweet_no']
            )

            # shuffle lists to have true random selection
            random.shuffle(locationUsersCol.userList)
            random.shuffle(eligibleFollowersCol.userList)

            # only write file if specified
            if writeFiles is True:
                # path for saving users
                file_directory_string = (
                    'data/02streamed' +
                    countryName
                )

                file_path_loc = Path(
                    file_directory_string +
                    'users_location_verified.csv'
                )
                # users where we know the location
                locationUsersCol.write_user_list_file(
                    full_path=file_path_loc
                )

                file_path_fol = Path(
                    file_directory_string +
                    'users_location_follower.csv'
                )
                # selected followers, we need to verify location
                eligibleFollowersCol.write_user_list_file(
                    full_path=file_path_fol
                )

            print("End Follower Selection")

        return locationUsersCol, eligibleFollowersCol

    def doUserSelection(
        self,
        country,
        locationUsersCol,
        eligibleFolCol,
        readFiles=False,
        writeFiles=False,
    ):
        """
        TODO Docstring doUserSelection
        """
        if writeFiles is True and readFiles is True:
            raise Exception(
                "readFiles and writeFiles cannot be True at the same time."
            )

        if readFiles is True:
            print("\nReading files for User Selection")
            print(
                    "Loading for country: " +
                    country
                )

            # base path for saved
            file_directory_string = (
                    'data/03verified' +
                    country
            )
            # verified and selected users
            file_path_user = Path(
                    file_directory_string +
                    'users.csv'
            )
            verifiedUsers = UserCollection()
            verifiedUsers.read_user_list_file(
                full_path=file_path_user
            )
            # tweets of verified and selected users
            file_path_tweets = Path(
                    file_directory_string +
                    'tweets.csv'
            )
            verifiedTweetCol = TweetCollection(
                additionalAttributes=self.config["twitter"]["add_attributes"]
            )
            verifiedTweetCol.read_tweet_list_file(
                full_path=file_path_tweets
            )

            print("Files successfully loaded")

        else:
            # no loading from file
            sampling_location = (
                self.config['scraping']['sampling_location_users']
            )
            sampling_total = self.config['scraping']['total_sample_size']
            sampling_other = sampling_total - sampling_location

            # verify that user's language and location is correct
            # this call is for already location verified users
            verifiedUsers, verifiedTweetCol = (
                self.verifyUserLocAndLang(
                    countryID=country,
                    usersCol=locationUsersCol,
                    userLimit=sampling_location,
                    verifyLocation=False
                )
            )
            # this call is for yet to be location verified users
            verifiedUsers2, verifiedTweetCol2 = (
                self.verifyUserLocAndLang(
                    countryID=country,
                    usersCol=eligibleFolCol,
                    userLimit=sampling_other,
                    verifyLocation=self.config['scraping']['validateLocation']
                )
            )

            # join both user and tweet list as our new base of users
            # we add the second results to the first result
            verifiedTweetCol.add_tweet_collection(
                tweetCol=verifiedTweetCol2
            )

            verifiedUsers.userList.extend(verifiedUsers2.userList)

            # only write file if specified
            if writeFiles is True:
                # base path for saved
                file_directory_string = (
                        'data/03verified' +
                        country
                )
                # verified and selected users
                file_path_user = Path(
                        file_directory_string +
                        'users.csv'
                )
                verifiedUsers.write_user_list_file(
                    full_path=file_path_user
                )
                # tweets of verified and selected users
                file_path_tweets = Path(
                        file_directory_string +
                        'tweets.csv'
                )
                verifiedTweetCol.write_tweet_list_file(
                    full_path=file_path_tweets
                )

        return verifiedUsers, verifiedTweetCol

    def verifyUserLocAndLang(
        self,
        countryID,
        usersCol,
        userLimit=10,
        verifyLocation=True,
    ):
        """
        TODO  docstring verifyUserLocAndLang
        limit defined how many successful verification we aim for

        """

        countryConf = self.config['twitter']['coordinates'][countryID]
        countryName = countryConf['name']
        targetLanguage = countryConf['lang']
        langThreshold = countryConf['langThreshold']
        otherLangThreshold = countryConf['otherLangThreshold']

        print(
                "\nStart verifying user location and language until " +
                str(userLimit) +
                " users are verified. Target language is " +
                str(targetLanguage) +
                ". Language Threshold is " +
                str(langThreshold) +
                " and other language threshold is " +
                str(otherLangThreshold)
        )

        verifiedCounter = 0
        verifiedUsers = UserCollection()
        verifiedTweetCol = TweetCollection(
            additionalAttributes=self.config["twitter"]["add_attributes"]
        )

        for num, user in enumerate(usersCol.userList):
            # retrieve user timeline upto max number of tweets
            max_tweets = self.config["twitter"]["user_max_tweet_no"]
            result, tweetCol = self.checkUserLanguage(
                user,
                targetLanguage=targetLanguage,
                langThreshold=langThreshold,
                otherLangThreshold=otherLangThreshold,
                limit=max_tweets
            )

            if result is True:
                # language of tweets is okay
                # now check if location is US based
                if verifyLocation is True:
                    if user.location == '':
                        # if user does not give location
                        # result is false
                        locationResult = False
                    else:
                        # checks if user's location is inside country
                        locationResult = self.checkUserLocation(
                            userLocation=user.location,
                            targetLocation=countryName
                        )

                else:
                    # if we do not verify
                    # it will automatically be true
                    locationResult = True

                if locationResult is True:
                    # for each user append the tweet list
                    # to the verified collection
                    verifiedTweetCol.add_tweet_collection(
                        tweetCol=tweetCol
                    )
                    verifiedUsers.funcAddUser(user)
                    verifiedCounter = verifiedCounter + 1
                    if (verifiedCounter % (userLimit/10)) == 0:
                        # give progress each 10 percent step
                        print(
                            "Current progress: " +
                            str(verifiedCounter) +
                            " verified users."
                        )

            if verifiedCounter >= userLimit:
                break


        print(
            'Number of inspected users ' +
            str(num + 1) +  # 0 based counting
            ' to get ' +
            str(verifiedCounter) +
            ' verified users.'
        )
        if verifiedCounter < userLimit:
            print("Limit was not reached.")

        return verifiedUsers, verifiedTweetCol

    def checkUserLanguage(
        self,
        user,
        targetLanguage,
        langThreshold=1,  # 100%
        otherLangThreshold=0,  # 0 %
        limit=3200,
    ):
        """
        TODO docstring checkUserLanguage

        tweetCol contains only tweets matching language
        otherLangThreshold = language not target and not undefined (und)

        limit including RTs
        """
        languageVerified = False
        targetTweetCollection = TweetCollection(
            additionalAttributes=self.config["twitter"]["add_attributes"]
        )
        totalTweets = 0
        tweetsTargetLang = 0
        undefinedTweets = 0
        otherLangTweets = 0

        # get tweets for given user
        tweetCol = self.twitter.funcGetTweetListByUser(
                user.id_str,
                limit=limit
        )
        # total number of tweets
        totalTweets = len(tweetCol.tweetList)

        # loop over all tweets and count language attributes
        for tweet in tweetCol.tweetList:
            if tweet.lang == targetLanguage:
                # correct language
                tweetsTargetLang = tweetsTargetLang + 1
                # add tweet to return collection
                targetTweetCollection.funcAddTweet(tweet)
            elif tweet.lang == 'und' or tweet.lang == '':
                # undefined language
                undefinedTweets = undefinedTweets + 1
            else:
                # other language
                otherLangTweets = otherLangTweets + 1

        # check if there are any tweets
        # possible that a user only posts retweets
        if totalTweets > 0:
            # analyse statistics with thresholds
            # default is False (meaning not verified)
            if (tweetsTargetLang / totalTweets) >= langThreshold:
                # enough target language tweets
                # now check other languages
                if (otherLangTweets / totalTweets) <= otherLangThreshold:
                    # not too much foreign language tweets
                    languageVerified = True
                else:
                    # too many other foreign language tweets
                    languageVerified = False
            else:
                # not enough target language tweets
                languageVerified = False
        else:
            # no tweet -> not verified
            languageVerified = False

        return languageVerified, tweetCol

    def checkUserLocation(
        self,
        userLocation,
        targetLocation,
    ):
        """
        TODO  docstring checkUserLocation
        Maybe put in maps interface
        """
        locationVerified = False

        # call api to get results for user profile location
        result = self.maps.get_address(
            userLocation
        )

        # take first result cancidate
        # (google might return multiple)
        if len(result['candidates']) > 0:
            address = result['candidates'][0]['formatted_address']
            if targetLocation in address:
                locationVerified = True
            else:
                # returned address is not in target country
                locationVerified = False
        else:
            # no results for location
            locationVerified = False

        return locationVerified

    def getRandomItemsFromList(
            self,
            itemList,
            numberOfElements=1,
    ):
        """
        TODO  docstring getRandomItemsFromList
        """
        return random.sample(itemList, numberOfElements)
