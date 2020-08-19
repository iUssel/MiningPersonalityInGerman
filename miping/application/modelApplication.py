import re
import logging

from ..interfaces.twitter import TwitterAPI
from ..training.features import Features
from ..training.dataPreparation import DataPreparation
from ..models import OnnxModel, Profile, ModelBase

from tweepy import TweepError
from .predictionErrors import UserNameError, NotASuitableUserError
from ..training.features import NoGloveValueError


class ModelApplication:
    """
    TODO docstring Class ModelApplication
    central class for prediction
    """

    # will hold twitter api object for class
    twitter = None
    # glove pipeline object for class
    glove_pipeline = None

    # useful for coverage statistics
    featuresObj = None

    # trained and imported models
    big5_openness = None
    big5_conscientiousness = None
    big5_extraversion = None
    big5_agreeableness = None
    big5_neuroticism = None
    # big 5 list for loops
    big5List = [
        'big5_openness',
        'big5_conscientiousness',
        'big5_extraversion',
        'big5_agreeableness',
        'big5_neuroticism',
    ]

    def __init__(
        self,
        twitter_consumer_key,
        twitter_consumer_secret,
        glove_file_path,
        dataBaseMode,
        modelPathDict,
        use_onnx_models=True,
    ):
        """
        TODO init func Class ModelApplication
        modelPathDict = {
            'big5_openness': {
                'onnx': /miping/trainedModels/glovebig5_openness.ONNX,
                'pickle': /miping/trainedModels/glovebig5_openness.pickle
            },
            ...
        }
        modelPathDict as returned from TrainedModels class
        """

        # initialize twitter api
        self.get_twitter(
            twitter_consumer_key,
            twitter_consumer_secret
        )

        # initialize glove_pipeline
        self.get_glove_pipeline(
            file_path=glove_file_path,
            dataBaseMode=dataBaseMode
        )

        # import models once
        self.importModels(
            modelPathDict=modelPathDict,
            use_onnx_models=use_onnx_models
        )

        return

    def importModels(
        self,
        modelPathDict,
        use_onnx_models,
    ):
        """
        TODO importModels
        """
        for dimension in self.big5List:
            # check if already loaded
            if getattr(ModelApplication, dimension) is None:
                # import model
                model = None
                if use_onnx_models is True:
                    # path for saved trained models
                    filepath = modelPathDict[dimension]['onnx']
                    # import onnx model
                    onnx = OnnxModel(
                        modelName="ONNX Model",
                        labelName=dimension,
                    )
                    onnx.importModelONNX(filepath)
                    model = onnx
                else:
                    # path for saved trained models
                    filepath = modelPathDict[dimension]['pickle']
                    # import pickle model
                    # call import function for model
                    model = ModelBase.importModelPickle(filepath)
                    # get scikit model from imported pickle
                    model = model.model
                # assign loaded model to class variable
                setattr(ModelApplication, dimension, model)

        return

    def get_twitter(
        self,
        twitter_consumer_key,
        twitter_consumer_secret
    ):
        """
        TODO initializes twitter api if not happened yet
        """
        if ModelApplication.twitter is None:
            # set Class attribute, not instance attribute
            # so API is only initialized once
            ModelApplication.twitter = TwitterAPI(
                consumer_key=twitter_consumer_key,
                consumer_secret=twitter_consumer_secret,
                wait_on_rate_limit_notify=True,
                removeNewLineChar=True,
                ignoreRetweets=True
            )
        return ModelApplication.twitter

    def validate_username_input(
        self,
        userName
    ):
        """
        TODO func validate_username_input
        takes data as input and checks if the input is a username string
        """
        # check format
        minlength = 1
        maxlength = 30
        pattern = re.compile('^[A-Za-z0-9_]+$')

        # check length
        if len(userName) < minlength or len(userName) > maxlength:
            # length does not match twitter handle
            eString = 'Username length not valid'
            raise UserNameError(eString)
        else:
            # valid length
            # check pattern
            match = pattern.match(userName)
            if match is None:
                # invalid
                eString = 'Username contains illegal characters'
                raise UserNameError(eString)
            else:
                # string is valid
                return userName

        return

    def get_glove_pipeline(
        self,
        file_path,
        dataBaseMode,
    ):
        """
        TODO initializes glove pipeline
        """
        # if already created, skip init
        if ModelApplication.glove_pipeline is None:
            features = Features()
            pipeline = features.createGloVeFeaturePipeline(
                glovePath=file_path,
                dataBaseMode=dataBaseMode
            )
            # assign to class
            ModelApplication.glove_pipeline = pipeline
            ModelApplication.featuresObj = features

        return ModelApplication.glove_pipeline

    def create_profile(
        self,
        username,
    ):
        """
        TODO create_profile
        does not validate user name
        """

        # get twitter api instance
        twitter = ModelApplication.twitter

        # get user id of user name
        try:
            userID = twitter.funcGetUserID(username)
        except TweepError:
            # multiple reasons for error
            # user not found, user suspended
            raise NotASuitableUserError('User not found or suspended.')

        # get tweets for given user
        try:
            tweetCol = twitter.funcGetTweetListByUser(
                    userID,
                    limit=200,
                    reRaiseExceptions=True
            )
        except TweepError:
            eString = "Could not load user's tweets. User is maybe protected."
            raise NotASuitableUserError(eString)

        # total number of tweets
        totalTweets = len(tweetCol.tweetList)

        # check if there are any tweets
        # possible that a user only posts retweets
        if totalTweets == 0:
            raise NotASuitableUserError('User has no suitable tweets')

        # combine all tweets into one string
        textString = tweetCol.combine_tweet_text()
        # check if any words exist inside tweets
        if len(textString) == 0:
            raise NotASuitableUserError("No text inside user's tweets")
        # call data cleansing for combined string
        dataPre = DataPreparation()
        textString = dataPre.clean_text(
            textString=textString
        )
        if len(textString) == 0:
            eString = "No text inside user's tweets after cleansing"
            raise NotASuitableUserError(eString)

        # save string in profile
        profile = Profile(
            userID=userID,
            text=textString
        )

        return profile

    def get_personality(
        self,
        profileList,
    ):
        """
        TODO get_personality by profile list
        enables to predict multiple user's at once
        """

        # feature pipeline
        pipeline = ModelApplication.glove_pipeline

        # calculate features
        try:
            features = pipeline.fit_transform(profileList)
        except NoGloveValueError:
            # this means, that the user's tweets
            # are not compatible with the used GloVe values
            # no words had a match -> therefore user not suitable
            eString = "User's tweets have no matching words."
            raise NotASuitableUserError(eString)

        # build return dict
        returnDict = {
            'big5_openness': None,
            'big5_conscientiousness': None,
            'big5_extraversion': None,
            'big5_agreeableness': None,
            'big5_neuroticism': None,
            'coverage': ModelApplication.featuresObj.coverageStatistics,
            'wordCount': ModelApplication.featuresObj.wordCounts
        }

        # for every big5 dimension apply prediction
        for dimension in self.big5List:
            model = getattr(ModelApplication, dimension)
            # apply prediction
            big5result = model.predict(features)
            # save result in returnDict
            # contains predictions for all profiles
            returnDict[dimension] = big5result

        # instead of print, do log
        logging.log(level=logging.INFO, msg="Finished prediction")

        return returnDict
