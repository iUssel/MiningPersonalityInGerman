import sqlite3
import pandas
from os import path
# this line logs an error, because the module contains a C libray
# which is not inspected, but the code works as it is
from sqlite3 import Error


class GloVe:
    """
    GloVe API class encloses communication related to GloVe data.
    Either GloVe SQLite database or direct flat file.
    """

    def __init__(
        self,
        filePath,
        dataBaseMode=True,
    ):
        """
        Initialization of GloVe to establish DB connection
        or load flat file into memory. DB connection is more
        memory efficient.

        Parameters
        ----------
        filePath : string, default=None, required
            Full path to GloVe vector file (either database or
            plain text file).
        dataBaseMode : boolean, default=True
            If True, glove_file_path points to SQLite database file.
            If False, flat vector file.
        """
        # save in instance
        self.dataBaseMode = dataBaseMode

        if path.exists(filePath) is False:
            # file does not exist
            eString = "Did not find GloVe file passed in GloVe class"
            raise Exception(eString)

        if dataBaseMode is True:
            print("Using GloVe database")
            self.connection = self._create_connection(
                # sql lite needs string as path
                db_file=str(filePath)
            )
        else:
            print("Using GloVe file")
            # load pre trained GloVe word embedding
            glove_df = self.loadGloVeFile(
                glovePath=filePath
            )

            self.glove_df = glove_df

        return

    def getGloVeByWordList(
        self,
        wordList
    ):
        """
        For each word in wordList get the corresponding GloVe vector.

        If none exists just ignore the word. Since SQLite database
        is limited in query length, the query is split into 999er chunks.
        If flat file is use, the approach is more simple.
        The returned DataFrame includes duplicates, to represent the
        input list as close as possible (for personality prediciton this
        is usually the preferred approach, because it caputes word
        reptitions).

        Parameters
        ----------
        wordList : list, default=None, required
            List of words to get GloVe vector values for.

        Returns
        -------
        glove_val_df : DataFrame
            Pandas Dataframe containing the glove vector values for
            the given word list.
        """

        if self.dataBaseMode is True:
            # since sqlite is limited in its query length
            # 999 chunks
            apiChunks = 999
            chunks = [
                wordList[
                    x:x+apiChunks
                ] for x in range(0, len(wordList), apiChunks)
            ]
            chunkCollectionDF = pandas.DataFrame()
            # for each 999er chunk, we will perform an SQL request
            for chunkList in chunks:
                # compose sql with length of chunk of word list
                # so that question marks ? can be added
                sql = "SELECT * FROM glove WHERE words IN ({seq})".format(
                        seq=','.join(['?']*len(chunkList))
                    )
                # query database and get data frame with unique values
                unique_glove_df = pandas.read_sql_query(
                    con=self.connection,
                    sql=sql,
                    params=chunkList,
                    index_col='words'
                )
                # add to data frame
                chunkCollectionDF = chunkCollectionDF.append(unique_glove_df)
            # make returned rows unique
            # due to chunks some duplicates are possible
            completeUniqueDF = chunkCollectionDF.drop_duplicates()
            # since returned values are unique we have to get the intersection
            # including duplicates now
            glove_val_df = (
                completeUniqueDF.loc[
                    completeUniqueDF.index.intersection(wordList)
                ]
            )
        else:
            # get values from loaded glove
            glove_val_df = (
                self.glove_df.loc[self.glove_df.index.intersection(wordList)]
            )

        return glove_val_df

    def get_index_list(
        self,
    ):
        """
        Return words existing in GloVe.

        This helps to make more efficient queries, by sorting out
        words that do not have a vector value before getting
        the actual values.

        Returns
        -------
        index_list : list
            List containing only the words existing in GloVe.
        """

        # depending on data if data base mode or not
        if self.dataBaseMode is True:
            # get index as list from data base
            sql = "SELECT words FROM glove;"
            dataFrame = pandas.read_sql_query(
                con=self.connection,
                sql=sql,
                index_col='words'
            )
            # convert to list
            index_list = list(dataFrame.index)
        else:
            # get index from fully loaded glove
            index_list = list(self.glove_df.index)

        return index_list

    def _create_connection(
        self,
        db_file
    ):
        """
        Initialize database connection based on file path.

        Parameters
        ----------
        db_file : string, default=None, required
            File path to SQLite database file.

        Returns
        -------
        conn : sqlite3 connection
            Initialized connection ready for queries.
        """
        conn = None
        try:
            conn = sqlite3.connect(db_file)
            conn.row_factory = sqlite3.Row
            return conn
        except Error as e:
            print(e)

        return conn

    def loadGloVeFile(
        self,
        glovePath
    ):
        """
        Load GloVe from flat file and return DataFrame.

        Parameters
        ----------
        glovePath : string, default=None, required
            Full path to glove flat vector file.

        Returns
        -------
        glove_df : DataFrame
            Pandas DataFrame containing all words and vectors.
        """

        print("\nLoading GloVe")

        # file exists, so we load it
        glove_df = pandas.read_csv(
            filepath_or_buffer=glovePath,
            sep=" ",
            header=None,
            encoding='utf_8',
        )
        # set words as index
        glove_df.set_index(0, inplace=True)
        glove_df.rename_axis("words", axis="index", inplace=True)

        print(
            "GloVe loaded with " +
            str(len(glove_df)) +
            " as count of words."
        )

        return glove_df
