import googlemaps


class MapsAPI:
    """
    Class for enclosing Google Maps related functions
    """

    def __init__(
        self,
        apiKey,
    ):
        """
        Initialize client with apiKey.

        Parameters
        ----------
        apiKey : string, default=None, required
            Google Places API key.
        """
        self.gmaps = googlemaps.Client(
            key=apiKey
        )

    def get_address(
        self,
        geoString,
    ):
        """
        Return result for search with Google's Place API.

        Parameters
        ----------
        geoString : string, default=None, required
            String with location we are trying to verify. In our case
            mostly Twitter profile locations.

        Returns
        -------
        address_result : dict
            Google result with potential candiates matching the search string.
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
