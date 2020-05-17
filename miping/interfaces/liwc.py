import csv

from decimal import Decimal

from ..models.profile import Profile


class LiwcAPI:
    """
    TODO docstring Class Liwc
    """

    def __init__(
        self,
    ):
        """
        TODO init func Class Liwc
        """
        pass

    def import_liwc_result(
        self,
        fullPath,
        profileCol,
    ):
        """
        TODO docstring import_liwc_result
        """

        # read csv file
        with open(fullPath, "r", newline='', encoding='utf-8') as infile:
            # initialize csv reader
            reader = csv.reader(
                infile,
                delimiter=',',
                quotechar='"',
                quoting=csv.QUOTE_MINIMAL
            )
            # we will load only LIWC categories
            # and skip everything else
            columnHeader = next(reader)

            for rowNum, row in enumerate(reader):
                # due to next(), we do not need
                # to explicitly skip the reader

                # first column must contain userID
                userID = row[0]

                # get profile from collection based on userID
                # this profile will be enriched with LIWC data
                profileInst = profileCol.get_profile_by_user_id(
                    userID=userID
                )

                # we will read csv file column by column
                # if one header matches the LIWC category
                # list we will set this attribute
                # otherwise we will not load this column
                # read liwc categories column by column
                for colIdx, columnName in enumerate(columnHeader):
                    # via index we find the description of the column
                    # and check if it exists in list
                    if columnName in Profile.liwc_category_list:
                        # column is a liwc category, so we assign
                        # the value to the profile
                        # this modifies the profile directly in
                        # the collection

                        # replace comma with dot, for american number format
                        value = row[colIdx].replace(',', '.')
                        # convert value to decimal
                        setattr(profileInst, columnName, Decimal(value))

        return profileCol
