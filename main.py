import os

import helper
import miping

from pathlib import Path


def main():
    """TODO Doc string
    """

    # get configuration
    globalConfig, apiKeys = initialize()

    # initialize Twitter API with keys
    twitter = miping.interfaces.TwitterAPI(
        consumer_key=apiKeys['twitter']['ConsumerKey'],
        consumer_secret=apiKeys['twitter']['ConsumerSecret'],
        access_token=apiKeys['twitter']['AccessToken'],
        access_token_secret=apiKeys['twitter']['AccessTokenSec'],
        wait_on_rate_limit_notify=(
            globalConfig["twitter"]["wait_on_rate_limit_notify"]
        ),

        additionalAttributes=globalConfig["twitter"]["add_attributes"],
        removeNewLineChar=globalConfig["twitter"]["remove_new_line"],
        ignoreRetweets=globalConfig["twitter"]["ignore_retweets"],
    )

    if globalConfig["process"]["scraping"] is True:
        scrapeConf = globalConfig["scraping"]
        # initialize maps interface
        maps = miping.interfaces.MapsAPI(
            apiKey=apiKeys['google']['maps']
        )
        # initialize object
        scraping = helper.Scraping(
            config=globalConfig,
            twitter=twitter,
            maps=maps,
        )
        # get data from stream
        scrapedTweetsDict = scraping.doScrapingByLocation(
            readFiles=scrapeConf["scrapingByLoc"]["readFile"],
            writeFiles=scrapeConf["scrapingByLoc"]["writeFile"]
        )

        for country in globalConfig['twitter']['coordinates']:
            countryConf = globalConfig['twitter']['coordinates'][country]
            # select users and some followers
            locationUsersCol, eligibleFolCol = scraping.doFollowerSelection(
                tweetSampleCol=scrapedTweetsDict[countryConf['name']],
                countryName=countryConf['name'],
                readFiles=scrapeConf["followerSelect"]["readFile"],
                writeFiles=scrapeConf["followerSelect"]["writeFile"]
            )

            verifiedUsers, verifiedTweetCol = scraping.doUserSelection(
                country=country,
                locationUsersCol=locationUsersCol,
                eligibleFolCol=eligibleFolCol,
                readFiles=scrapeConf["userSelect"]["readFile"],
                writeFiles=scrapeConf["userSelect"]["writeFile"]
            )

            print(len(verifiedUsers.userList))
            print(len(verifiedTweetCol.get_distinct_user_id_list()))

    if globalConfig["process"]["dataPreparation"] is True:
        dataPre = miping.training.DataPreparation(
        )

        # Test TODO CONTINUE
        newTwCol = miping.models.TweetCollection(
            additionalAttributes=None
        )
        newTwCol.read_tweet_list_file(
            full_path='data/trash/streamedGermanytweet.csv',
            ids_only=False
        )

        laksd = newTwCol.get_tweets_of_userid(userID='405251081')

        textString = laksd.combine_tweet_text()
        print(textString)
        print('After')
        textString = dataPre.clean_text(
            textString=textString
        )
        print(textString)



def initialize():
    """
    TODO Doc String funcInitialize
    """
    # load configuration
    configPath = Path(os.path.dirname(os.path.abspath(__file__)))
    configFullPath = configPath / "config.yml"
    configHelper = helper.ConfigLoader(configFullPath)
    config = configHelper.config

    # retrieve API keys and other secrets from environment variables
    apiKeys = configHelper.environmentVars

    return config, apiKeys


if __name__ == "__main__":
    main()
