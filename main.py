import os

import helper
import miping

from pathlib import Path


def main():
    """TODO Doc string
    """

    # get configuration
    globalConfig, config_models, apiKeys = initialize()

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

        if preparationConfig["printStatistics"] is True:
            preparation.print_statistics(globalProfileCollection)

    if globalConfig["process"]["modelTrainingLIWC"] is True:
        trainConf = globalConfig["modelTraining"]
        # init helper class
        trainingSteps = helper.TrainingProcess(
            config=trainConf,
            modelConfig=config_models
        )
        # build LIWC model based on English texts
        globalLIWCModels = trainingSteps.doLIWCModelTraining(
            profileCol=globalProfileCollection['USA'],
            writePickleFiles=trainConf["writePickleFiles"],
            readPickleFiles=trainConf["readPickleFiles"],
            writeONNXModel=trainConf["writeONNXModel"],
            readONNXModel=trainConf["readONNXModel"]
        )

    if globalConfig["process"]["derivePersonalities"] is True:
        trainConf = globalConfig["modelTraining"]
        # use trained model to derive German personalities
        # init helper class
        trainingSteps = helper.TrainingProcess(
            config=trainConf,
            modelConfig=config_models
        )
        # set variables to None, if we read files,
        # because they are not needed
        if trainConf["readFile"] is True:
            globalLIWCModels = None
            locProfileCollection = None
            globalProfileCollection = {}
        else:
            locProfileCollection = globalProfileCollection[country]
        # loop over all available countries
        for country in globalConfig['twitter']['coordinates']:

            # for all countries we did not get IBM profiles for
            # we will fill profile with trained LIWC model
            filledProfileCollection = trainingSteps.predictPersonalitiesLIWC(
                profileCol=locProfileCollection,
                country=country,
                globalLIWCModels=globalLIWCModels,
                ibmList=globalConfig["preparationProcess"]['countriesIBM'],
                readFiles=trainConf["readFile"],
                writeFiles=trainConf["writeFile"]
            )

            globalProfileCollection[country] = filledProfileCollection

        if globalConfig["preparationProcess"]["printStatistics"] is True:
            # print again statistics
            preparation = helper.PreparationProcess(
                config=None,
                ibm=None
            )
            preparation.print_statistics(globalProfileCollection)

    if globalConfig["process"]["modelTrainingGloVe"] is True:
        trainConf = globalConfig["modelTraining"]
        # init helper class
        trainingSteps = helper.TrainingProcess(
            config=trainConf,
            modelConfig=config_models
        )
        # build GloVe model based on German texts
        globalGloVeModels = trainingSteps.doGloVeModelTraining(
            profileCol=globalProfileCollection['Germany'],
            writePickleFiles=trainConf["writePickleFilesG"],
            readPickleFiles=trainConf["readPickleFilesG"],
            writeONNXModel=trainConf["writeONNXModelG"],
            readONNXModel=trainConf["readONNXModelG"],
            writeFeatureFile=trainConf["writeFeatureFile"],
            readFeatureFile=trainConf["readFeatureFile"],
        )

        # predict whole training set and print statistics
        # do prediction and print statistics
        trainingSteps.do_prediction(
            profileCol=globalProfileCollection['Germany'],
            globalGloVeModels=globalGloVeModels,
            readFeatureFile=trainConf["readFeatureFile"],
        )

    print("Finished")


def initialize():
    """
    TODO Doc String funcInitialize
    """
    # load configuration
    configPath = Path(os.path.dirname(os.path.abspath(__file__)))
    configFullPath = configPath / "config.yml"
    configModelFullPath = configPath / "config_models.yml"
    configHelper = helper.ConfigLoader(
        configPath=configFullPath,
        modelConfigPath=configModelFullPath
    )
    config = configHelper.config
    config_models = configHelper.config_models

    # retrieve API keys and other secrets from environment variables
    apiKeys = configHelper.environmentVars

    return config, config_models, apiKeys


if __name__ == "__main__":
    main()
