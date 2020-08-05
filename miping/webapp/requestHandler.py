import os
import re
import logging
import requests
import json
from dotenv import load_dotenv
from pathlib import Path
from flask import current_app

from .invalidUsage import InvalidUsage
from ..training.dataPreparation import DataPreparation
from ..models import OnnxModel, Profile
from ..interfaces import TwitterAPI, GloVe
from ..training.features import Features


class RequestHandler:
    """
    TODO docstring Class Requesthandler -
    handle flask app stuff
    captcha
    IP tracking
    """

    # verify captcha
    verify_url_b = 'https://www.google.com/recaptcha/api/siteverify?secret='

    @staticmethod
    def loadKey(
        name
    ):
        """
        TODO loadCaptchaKey staticmethod
        """
        # load .env vars in environment variables
        load_dotenv()
        
        # load key from environment variables
        envKey = (
            os.environ.get(name)
        )

        # special for captcha
        if envKey is None and name == 'google_recaptcha':
            logging.info("No recaptcha key passed. Will ignore recaptcha.")
            envKey = ""

        return envKey

    def __init__(
        self,
        config
    ):
        """
        TODO init func Class Requesthandler
        save config from app
        """

        self.config = config

        return

    def get_twitter(
        self
    ):
        """
        TODO initializes twitter api if not happened yet
        """
        if not hasattr(self, 'twitter'):
            self.twitter = TwitterAPI(
            consumer_key=current_app.config['twitter_consumer_key'],
            consumer_secret=current_app.config['twitter_consumer_secret'],
            wait_on_rate_limit_notify=True,
            removeNewLineChar=True,
            ignoreRetweets=True
        )
        return self.twitter

    def validate_username_input(
        self,
        data
    ):
        """
        TODO func validate_username_input
        takes data as input and checks if the input is a username string
        """
        if 'twitterHandle' in data:
            handleData = data['twitterHandle']
            # key exists, now check format
            minlength = 1
            maxlength = 30
            pattern = re.compile('^[A-Za-z0-9_]+$')

            # check length
            if len(handleData) < minlength or len(handleData) > maxlength:
                # length does not match twitter handle
                eString = 'TwitterHandle length not valid'
                raise InvalidUsage(eString, status_code=400)
            else:
                # valid length
                # check pattern
                match = pattern.match(handleData)
                if match is None:
                    # invalid
                    eString = 'TwitterHandle contains illegal characters'
                    raise InvalidUsage(eString, status_code=400)
                else:
                    # string is valid
                    return handleData
        else:
            # key does not exist, invalid request
            raise InvalidUsage('No twitterHandle provided', status_code=400)

        return

    def get_glove_pipeline(
        self
    ):
        """
        TODO initializes glove pipeline
        """
        # identify current directory
        dir = os.path.dirname(__file__)
        # make absolute file path
        file_path = os.path.join(dir, '../../data/glove/glove.db')
        if not hasattr(self, 'glove_pipeline'):
            features = Features()
            self.glove_pipeline = features.createGloVeFeaturePipeline(
                glovePath=file_path,
                dataBaseMode=True
            )# TODO!!! config

        return self.glove_pipeline

    def check_recaptcha(
        self,
        data,
    ):
        """
        TODO check_recaptcha
        """
        # check if token is passed
        if 'token' not in data.keys():
            print(data)
            # error no token provided
            raise InvalidUsage('No reCaptcha', status_code=400)
        else:
            # token field exists
            captcha_token = data["token"]

            # concatenate url
            verify_url = (
                self.verify_url_b +
                self.config['CAPTCHAKEY'] +
                '&response=' +
                str(captcha_token)
            )

            # query google service
            google_response = requests.post(verify_url)

            responseObj = json.loads(google_response.text)
            if responseObj["success"] is True:
                # valid
                return True
            else:
                # not valid
                raise InvalidUsage('Invalid reCaptcha', status_code=400)

        return False

    def get_personality(
        self,
        username,
    ):
        """
        TODO get_personality
        """

        # get twitter api instance
        twitter = self.get_twitter()

        # get user id of user name
        userID = twitter.funcGetUserID(username)

        # get tweets for given user
        tweetCol = twitter.funcGetTweetListByUser(
                userID,
                limit=200 # TODO flexible?
        )
        # total number of tweets
        totalTweets = len(tweetCol.tweetList)

        # check if there are any tweets
        # possible that a user only posts retweets
        if totalTweets == 0:
            raise InvalidUsage('User has no suitable tweets', status_code=400)

        # combine all tweets into one string
        textString = tweetCol.combine_tweet_text()
        # call data cleansing for combined string
        dataPre = DataPreparation()
        textString = dataPre.clean_text(
            textString=textString
        )
        # save string in profile
        profile = Profile(
            userID=userID,
            text=textString
        )

        # feature pipeline
        # create feature pipeline
        pipeline = self.get_glove_pipeline()

        # calculate features
        features = pipeline.fit_transform([profile])

        # load model (probably static)
        # path for saved trained models
        file_directory_string = (
            '../../data/trainedModels/glovebig5_extraversion.ONNX'
        )

        # identify current directory
        dir = os.path.dirname(__file__)
        # make absolute file path
        file_path = os.path.join(dir, file_directory_string)
        
        # import onnx model
        onnx = OnnxModel(
            modelName="ONNX Model",
            labelName='big5_extraversion',
        )
        onnx.importModelONNX(file_path)

        # apply prediction
        extraversion = onnx.predict(features)

        # build return dict
        returnDict = {
            'userName': username,
            'big5_openness': 0.999,
            'big5_conscientiousness': 0.999,
            'big5_extraversion': float(extraversion),
            'big5_agreeableness': 0.999,
            'big5_neuroticism': 0.999
        }
        print("Finished")

        return returnDict