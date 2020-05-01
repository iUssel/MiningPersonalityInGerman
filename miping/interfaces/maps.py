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
        """
        self.gmaps = googlemaps.Client(
            key=apiKey
        )

    def get_geocode(
        self,
        geoString,
    ):
        """
        TODO docstring get_geocode
        """

        geocode_result = self.gmaps.geocode(
            geoString
        )

        return geocode_result

