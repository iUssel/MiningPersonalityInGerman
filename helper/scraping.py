import random
from pathlib import Path


class Scraping:
    """
    TODO docstring Class Scraping
    coordinates the initial scraping of streaming data from twitter
    """

    def __init__(
        self,
        config,
        twitter,
        writeFiles=True,
    ):
        """
        TODO init func Class Scraping
        config of main
        initialized twitter class
        """
        self.config = config

        self.twitter = twitter

        self.writeFiles = writeFiles

    def doScrapingByLocation(
        self
    ):
        """
        TODO  docstring doScrapingByLocation

        return tweetCollection
        """
        print("Begin scraping by location")

        for country in self.config['twitter']['coordinates']:
            # getting coordinates for streaming
            country = self.config['twitter']['coordinates'][country]

            location = [
                country['southwest']['lng'],
                country['southwest']['lat'],
                country['northeast']['lng'],
                country['northeast']['lat']
            ]
            print(
                "Streaming for country: " +
                country['name']
            )

            scrapeConfig = self.config['scraping']
            scrapedTweets = self.twitter.stream_tweets_by_location(
                location=location,
                timeLimit=scrapeConfig['timer'],
                maxFollowerCount=scrapeConfig['user_max_followers'],
                minStatusesCount=scrapeConfig['users_min_tweet_no'],
            )

            # only write file if specified
            if self.writeFiles is True:
                # path for saving tweets
                file_directory_string = (
                    'data/streamed' +
                    country['name'] +
                    'tweet.csv'
                )
                file_path = Path(file_directory_string)

                scrapedTweets.write_tweet_list_file(
                    full_path=file_path
                )

        print("End scraping by location")

        return scrapedTweets

    def doUserSelection(
        self,
        tweetSampleCol,
    ):
        """
        TODO  docstring doUserSelection

        tweetSampleCol contains users that are already in the right
        location, have the right number of tweets and followerss
        """
        print("Start selection of users")
        sampling_follower = self.config['scraping']['sampling_follower']
        sampling_location = self.config['scraping']['sampling_location_users']

        print(
            'Will select followers from ' +
            str(sampling_follower) +
            ' users retrieved via location scraping. '
            'Will include ' +
            str(sampling_location) +
            ' users directly retrieved via location scraping.'
        )

        # retrieve user ids from tweets
        userList = tweetSampleCol.get_distinct_user_id_list()

        # get users based on IDs
        # (follower and tweet count already ensured)
        locationScrapedUsersCol = self.twitter.getUsersByList(
            userIDList=userList
        )

        # get x random users from list
        # since API limit is limited
        randList = self.getRandomItemsFromList(
            userList,
            sampling_follower
        )

        # get followers of scraped tweets/users
        """
        followers = self.twitter.get_followers_of_user(
            userIDList=randList,
            limit=5000  # 5000 users are returned per API call
        )
        """
        followers=['21553001']

        # select eligible followers
        # tweet count and follower count
        scrapeConfig = self.config['scraping']
        eligibleFollowersCol = self.twitter.getUsersByList(
            userIDList=followers,
            maxFollowerCount=scrapeConfig['user_max_followers'],
            minStatusesCount=scrapeConfig['users_min_tweet_no']
        )
        print("Followers before selection")
        print(len(followers))

        # select X users from followers collection
        # but only users, where we can pinpoint
        # the location to country1
        self.checkUserLocation(
            userCol=eligibleFollowersCol,
            location='Germany',
            limit=sampling_location
        )

        

        print("End selection of users")

        return eligibleFollowersCol

    def checkUserLocation(
        self,
        userCol,
        location,
        limit=0,
    ):
        """
        TODO  docstring doScrapingByLocation
        Limit tells after how many positive tested users
        the function ends and returns the tested users
        """
        return userCol

    def getRandomItemsFromList(
            self,
            itemList,
            numberOfElements=1,
    ):
        """
        TODO  docstring getRandomItemsFromList
        """
        return random.sample(itemList, numberOfElements)
