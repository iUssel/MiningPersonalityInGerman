import os
import logging
import requests
import json
from dotenv import load_dotenv

from .invalidUsage import InvalidUsage
from ..application.modelApplication import ModelApplication
from ..application.predictionErrors import NotASuitableUserError
from ..application.predictionErrors import UserNameError
from ..trainedModels import TrainedModels


class RequestHandler:
    """
    Actual webapplication backend.
    Coordinates request handling and processing.
    """

    # verify captcha
    verify_url_b = 'https://www.google.com/recaptcha/api/siteverify?secret='
    """ReCaptcha base URL"""

    @staticmethod
    def loadKey(
        name
    ):
        """
        Staticmethod to load API keys from environment variables.

        Parameters
        ----------
        name : string, default=None, required
            Name of environment variable to load.

        Returns
        -------
        envKey : string
            Actual API key or configuration value.
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

        # convert string values to booleans
        if envKey == "True":
            envKey = True
        elif envKey == "False":
            envKey = False

        return envKey

    def __init__(
        self,
        config
    ):
        """
        Initialize requestHandler to save config and initialize
        ModelApplication (this will load GloVe and models once).

        Parameters
        ----------
        config : dict, default=None, required
            Configuration from flask app, contains relevant API keys.
        """

        self.config = config

        # identify file path to pass in ModelApplication
        # identify current directory
        directory = os.path.dirname(__file__)
        # glove is in miping root directory, therefore we go two levels up
        # then we are in MiPing repository root level
        glove_file_path = os.path.join(
            # identify current directory
            directory,
            # go two levels up to be at miping root level
            '../../',
            # get relative file path from config
            self.config['glove_file_path'],
        )

        trainedModelPaths = TrainedModels()

        # initialize modelApplication class
        self.modelApplication = ModelApplication(
            twitter_consumer_key=(
                self.config['twitter_consumer_key']
            ),
            twitter_consumer_secret=(
                self.config['twitter_consumer_secret']
            ),
            glove_file_path=glove_file_path,
            dataBaseMode=self.config['glove_database_mode'],
            modelPathDict=trainedModelPaths.get_file_path_dict(),
            use_onnx_models=True
        )

        return

    def validate_username_input(
        self,
        data
    ):
        """
        Takes data as input and checks if the input is a username string.

        Raises exception if no valid username provided

        Parameters
        ----------
        data : dict, default=None
            Data that has been sent with the HTTP request.
        """
        if 'twitterHandle' in data:
            handleData = data['twitterHandle']
            try:
                name = self.modelApplication.validate_username_input(
                    userName=handleData
                )
            except UserNameError as e:
                # user name is not valid
                # reraise exception, so it gets to user
                raise InvalidUsage(str(e), status_code=400)
            return name
        else:
            # key does not exist, invalid request
            raise InvalidUsage('No twitterHandle provided', status_code=400)

        return

    def check_recaptcha(
        self,
        data,
    ):
        """
        Check if recaptcha token is valid. Return False otherwise.

        Raises exception if no or invliad token is provided.

        Parameters
        ----------
        data : dict, default=None
            Data that has been sent with the HTTP request.

        Returns
        -------
        boolean : boolean
            Returns True if token is valid, otherwise False.
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
        Get tweets for username and return Big Five predictions.

        Parameters
        ----------
        username : string, default=None, required
            Username to get personality prediction for.

        Returns
        -------
        personalityDict : dict
            Result dictionary containing the relevant data.
        """

        # create profile object from username
        # call to Twitter API
        try:
            profile = self.modelApplication.create_profile(username)
        except NotASuitableUserError as e:
            # user might be protected or something like this
            # reraise exception, so it gets to user
            raise InvalidUsage(str(e), status_code=400)

        # call prediction in modelApplication, expects list
        try:
            resultDict = self.modelApplication.get_personality([profile])
        except NotASuitableUserError as e:
            # reraise exception, so it gets to user
            raise InvalidUsage(str(e), status_code=400)

        # initialize return dict
        personalityDict = {
            'userName': username
        }
        # build personalityDict for this user
        for dimension in resultDict.keys():
            # take first (and only) value in each
            # dimension's resultList
            resultList = resultDict[dimension]
            personalityDict[dimension] = float(resultList[0])

        # get coverage statistics (first entry)
        coverage = resultDict['coverage'][0]
        personalityDict['coverage'] = coverage
        # word count, also first entry
        coverage = resultDict['wordCount'][0]
        personalityDict['wordCount'] = coverage

        return personalityDict
