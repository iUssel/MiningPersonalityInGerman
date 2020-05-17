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

    # initialize result variables
    finalTweets = {}
    finalUsers = {}
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

            finalTweets[country] = verifiedTweetCol
            finalUsers[country] = verifiedUsers

    if globalConfig["process"]["dataPreparation"] is True:
        preparationConfig = globalConfig["preparationProcess"]

        # ibm api init
        ibmApi = miping.interfaces.IbmAPI(
            apiKey=apiKeys['ibm']['api'],
            url=apiKeys['ibm']['url'],
        )

        preparation = helper.PreparationProcess(
            config=globalConfig,
            ibm=ibmApi
        )

        # contains profile collections for each country
        # will be filled in next step
        globalProfileCollection = {}

        for country in globalConfig['twitter']['coordinates']:
            countryConf = globalConfig['twitter']['coordinates'][country]
            if preparationConfig["condenseTweets"]["readFile"] is True:
                # if we read from file, we do not need any input
                finalTweets[country] = None
                finalUsers[country] = None
            # prepare text and create empty profiles
            localProfileCollection = preparation.do_condense_tweets(
                verifiedTweetCol=finalTweets[country],
                verifiedUsers=finalUsers[country],
                language=countryConf['lang'],
                country=country,
                readFiles=preparationConfig["condenseTweets"]["readFile"],
                writeFiles=preparationConfig["condenseTweets"]["writeFile"]
            )

            # for desginated countries fill profiles with ibm data
            if country in preparationConfig['countriesIBM']:
                # get profiles for each user from IBM
                localProfileCollection = preparation.do_get_ibm_profiles(
                    profileCol=localProfileCollection,
                    country=country,
                    readFiles=preparationConfig["getIBMprofile"]["readFile"],
                    writeFiles=preparationConfig["getIBMprofile"]["writeFile"]
                )

            # global profile collection contains profiles inlcuding
            # ibm data, if available
            globalProfileCollection[country] = localProfileCollection

        # this is a manual step:
        # the extracted profiles will be enriched with LIWC
        # data. This is a separate program, therefore
        # we will ask the user if liwc files are provided
        for country in globalConfig['twitter']['coordinates']:
            # read profile collection from dict
            localProfileCollection = globalProfileCollection[country]

            # either read previously exported file or read LIWC output file
            localProfileCollection = preparation.do_liwc(
                    profileCol=localProfileCollection,
                    country=country,
                    liwcPath=preparationConfig["liwc"]["path"],
                    fileName=preparationConfig["liwc"]["fileName"],
                    readFiles=preparationConfig["liwc"]["readFile"],
                    writeFiles=preparationConfig["liwc"]["writeFile"],
                    skipInputWait=False
            )

            # global profile collection contains profiles inlcuding
            # ibm data, if available
            # now including liwc data
            globalProfileCollection[country] = localProfileCollection

        # TODO this is were we continue
        # Build LIWC based model with English texts

        # derive German personalities


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
