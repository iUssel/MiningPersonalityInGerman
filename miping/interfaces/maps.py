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

        try:
            address_result = self.gmaps.find_place(
                input=geoString,
                input_type='textquery',
                fields=['formatted_address'],
                language='en'  # result language should be unified
            )
        except googlemaps.exceptions.ApiError as e:
            # some times there are maps errors
            # to help debugging we will print the geoString
            print("GeoString for address was:")
            print(str(geoString))
            raise e

        return address_result
