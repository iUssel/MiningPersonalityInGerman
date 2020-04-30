class Scraping:
    """
    TODO docstring Class Scraping
    coordinates the initial scraping of streaming data from twitter
    """

    def __init__(
        self,
        config,
        twitter
    ):
        """
        TODO init func Class Scraping
        config of main
        initialized twitter class
        """
        self.config = config

        self.twitter = twitter

    def doScraping(
        self
    ):
        """
        TODO  docstring doScraping
        """

        # getting coordinates for streaming
        country1 = self.config['twitter']['coordinates']['country1']

        location = [
            country1['southwest']['lng'],
            country1['southwest']['lat'],
            country1['northeast']['lng'],
            country1['northeast']['lat']
        ]
        scrapedTweets = self.twitter.stream_tweets_by_location(
            timeLimit=self.config['scraping']['timer'],
            location=location
        )

        scrapedTweets.write_tweet_list_file(
            full_path='data/streamedUSAtweet.csv'
        )
