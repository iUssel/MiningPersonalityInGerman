import googlemaps


class MapsAPI:
    """
    TODO docstring Class Maps
    """

    def __init__(
        self,
        apiKey,
    ):
        """
        TODO init func Class MapsAPI

        Expects Places Api Key
        """
        self.gmaps = googlemaps.Client(
            key=apiKey
        )

    def get_address(
        self,
        geoString,
    ):
        """
        TODO docstring get_address
        """

        address_result = self.gmaps.find_place(
            input=geoString,
            input_type='textquery',
            fields=['formatted_address'],
            language='en'  # result language should be unified
        )

        return address_result
