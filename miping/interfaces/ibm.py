import requests
import json

from ..models.profile import Profile


class IbmAPI:
    """
    TODO docstring Class Ibm
    """

    def __init__(
        self,
        apiKey,
        url,
    ):
        """
        TODO init func Class ibm api
        """

        # save as instance variables for later authenticatio
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
        TODO get profile method
        either pass a profile instance or we create one
        """

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

        # check if IBM api returns any warnings
        # e.g. WORD_COUNT_MESSAGE is returned
        # if too few words are used as input
        if len(indata['warnings']) > 0:
            print('Warning during IBM profile generation')
            print(indata['warnings'])

        # fill profile object
        fillProfile.load_ibm_json(
            ibmJson=indata
        )

        return fillProfile
