import os
import helper
import miping

from pathlib import Path


def main():
    """TODO Doc string
    """

    # get configuration
    globalConfig, apiKeys = initialize()

    # print basic configuration
    print(
        "Max tweets per user: " +
        str(globalConfig["twitter"]["user_max_tweet_no"])
    )

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

    """
    # test function
    userID = twitter.funcGetUserID(
        screen_name='iUssel'
    )
    print(userID)

    # test function
    twCol = twitter.funcGetTweetListByUser(
        userID='13310352',
        limit=globalConfig["twitter"]["user_max_tweet_no"],
    )  # '13310352')

    twCol.write_tweet_list_file(full_path='data/tweetlist.csv', ids_only=True)

    newTwCol = miping.models.TweetCollection(
        globalConfig["twitter"]["add_attributes"]
    )

    newTwCol.read_tweet_list_file(
        full_path='data/tweetlist.csv',
        ids_only=True
    )
    """
    """
    listID = ['488827559187333121']
    # test get tweet by id
    fullTweets, invalidIDs = twitter.get_tweets_by_list(
        listID  # newTwCol.get_id_list()
    )

    print("Invalid " + str(invalidIDs))

    for tweet in fullTweets.tweetList:
        print(tweet.text)
    """

    if globalConfig["process"]["scraping"] is True:
        print("Begin Twitter Scraping")
        scraping = helper.Scraping(
            config=globalConfig,
            twitter=twitter
        )
        scraping.doScraping()
        print("End Twitter Scraping")


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
