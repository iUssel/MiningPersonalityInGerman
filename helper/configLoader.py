import yaml
import os
from dotenv import load_dotenv


class ConfigLoader:
    """
    Assembles methods to read information from environment variables
    and YML-Config files.
    """

    def __init__(
        self,
        configPath="",
        modelConfigPath="",
    ):
        """
        Init Function of ConfigLoader Class for setting Configfile paths.

        Loads environment variable from .env file and checks if given
        parameters are set. If not an exception is raised.
        Afterwards functions for actually loading the values from YML and
        .env are called. Variable values are saved in object variables
        config, config_models and environmentVars.

        Parameters
        ----------
        configPath : string, default=""
            Full path for the config YML file which controls the program flow.
            Ideally, the string is passed from a pathlib.Path() object, that
            manages path string regardsless of the platform OS.
        modelConfigPath : string, default=""
            Full path for the model config YML file which
            contains the grid search and tuning parameters for each
            model type.
            Ideally, the string is passed from a pathlib.Path() object, that
            manages path string regardsless of the platform OS.
        """

        # .env variables are loaded from file
        load_dotenv()

        if configPath != "" and modelConfigPath != "":
            self.config = self._funcReadConfig(configPath)

            # load model parameters config
            self.config_models = self._funcReadConfig(modelConfigPath)
        else:
            raise _InputError(
                "No configPath given. " +
                "You need to pass the full path to config.yml and " +
                "config_model_parameters.yml."
            )

        self.environmentVars = self._funcReadEnvironmentVars()

    def _funcReadConfig(
        self,
        path,
    ):
        """
        Read YML file in given path.

        Parameters
        ----------
        path : string, default=None
            Full absolute path for file to be loaded via yaml.safe_load().

        Returns
        -------
        config : dict
            The parsed YML as dict containing all config values.
        """

        with open(path, "r") as ymlfile:
            config = yaml.safe_load(ymlfile)

        return config

    def _funcReadEnvironmentVars(
        self,
    ):
        """
        Read relevant environment variables.

        Due to the .env functionality, environment variables are read
        from system and from all .env files in the higher-level directories.
        Some keys are optional, but Twitter consumer tokens are required.

        Returns
        -------
        apiKeys : dict
            All API keys are stored inside that dictionary.
        """

        # retrieve API keys and other secrets from environment variables
        # initialize dict
        apiKeys = {
            'twitter': {},
            'ibm': {},
            'google': {},
        }

        apiKeys['twitter']['ConsumerKey'] = (
            os.environ.get("twitter_consumer_key")
        )
        if apiKeys['twitter']['ConsumerKey'] is None:
            raise _InputError(
                "No Twitter consumer key in environment variables. " +
                "See README file."
            )

        apiKeys['twitter']['ConsumerSecret'] = (
            os.environ.get("twitter_consumer_secret")
        )
        if apiKeys['twitter']['ConsumerSecret'] is None:
            raise _InputError(
                "No Twitter consumer secret in environment variables. " +
                "See README file."
            )

        apiKeys['twitter']['AccessToken'] = (
            os.environ.get("twitter_access_token")
        )
        if apiKeys['twitter']['AccessToken'] is None:
            print(
                'No Twitter access token supplied. ' +
                'Streaming will be disabled.'
            )

        apiKeys['twitter']['AccessTokenSec'] = (
            os.environ.get("twitter_access_token_sec")
        )
        if apiKeys['twitter']['AccessTokenSec'] is None:
            print(
                'No Twitter access token secret supplied. ' +
                'Streaming will be disabled.'
            )

        apiKeys['google']['maps'] = (
            os.environ.get("google_places_api")
        )
        if apiKeys['google']['maps'] is None:
            print(
                'No Google Places API key supplied. ' +
                'Locations lookup will be disabled. ' +
                'Only necessary if scraping is True.'
            )

        apiKeys['ibm']['url'] = (
            os.environ.get("IBM_URL")
        )
        if apiKeys['ibm']['url'] is None:
            print('No IBM URL in .env')
        apiKeys['ibm']['api'] = (
            os.environ.get("IBM_IAM_APIKEY")
        )
        if apiKeys['ibm']['api'] is None:
            print('No IBM API key in .env')

        return apiKeys


class _InputError(Exception):
    """
    Internal exception raised for errors in the input.

    Parameters
    ----------
    message : string, default=None
        Additional message to be passed to Exception.
    """

    def __init__(self, message):
        self.message = message
