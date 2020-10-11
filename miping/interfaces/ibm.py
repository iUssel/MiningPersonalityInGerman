import requests
import json

from ..models.profile import Profile


class IbmAPI:
    """
    Class for enclosing IbmAPI related functions.
    This is regarding IBM Watson Personality Insight.
    """

    def __init__(
        self,
        apiKey,
        url,
    ):
        """
        Initialize API with custom URL and API key.

        Parameters
        ----------
        apiKey : string, default=None, required
            Private API key.
        url : string, default=None, required
            URL to IBM PI instance.
        """

        # save as instance variables for later authentication
        self.apiKey = apiKey
        self.url = url

        return

    def get_profile(
        self,
        text,
        fillProfile=None,
        language='en',
    ):
        """
        Get personality prediction based on text.

        A HTTP request is made with the given text to the IBM API
        in order to get personality predictions. Warnings
        are printed during the process. If no error is encountered,
        either a new profile is filled with the JSON response, or
        the passed fillProfile is filled.

        Parameters
        ----------
        text : string, default=None, required
            Text for making prediction, at least 100 characters.
            A warning is issued if less than 600 characters.
        fillProfile : Profile, default=None
            If passed, the personality data is saved inside the given
            profile. Otherwise a new profile is created.
        language : string, default='en'
            Full absolute path for file to be loaded via yaml.safe_load().

        Returns
        -------
        config : dict
            The parsed dict containing all config values.
        """
        # used to skip loading, when there is an error
        errorEncounterd = False

        if fillProfile is None:
            fillProfile = Profile()

        # build http request to api
        myobj = text.encode('utf-8')

        # we are transferring plain text
        # already cleansed and in utf-8 encoding
        # we want a json response by the ibm api
        myHeaders = {
            "Content-Type": "text/plain;charset=utf-8",
            "Accept": "application/json"
        }

        response = requests.post(
            self.url,
            data=myobj,
            headers=myHeaders,
            auth=('apiKey', self.apiKey)
        )

        indata = json.loads(response.text)
        responseHeaders = response.headers

        # check if IBM api returns any warnings
        # e.g. WORD_COUNT_MESSAGE is returned
        # if too few words are used as input
        if 'warnings' in indata:
            if len(indata['warnings']) > 0:
                print('Warning during IBM profile generation')
                print(indata['warnings'])
        else:
            # no warnings in indata, seems to be atypical
            # e.g. invalid request or too few word
            print(
                'No warnings key in IBM response.' +
                'Response was:\n' +
                str(indata) +
                '\nHeaders are:\n' +
                str(responseHeaders)
            )
            # skip loading
            errorEncounterd = True

        if errorEncounterd is False:
            # fill profile object
            fillProfile.load_ibm_json(
                ibmJson=indata
            )

        return fillProfile, errorEncounterd
