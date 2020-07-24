import numpy as np
import pandas

from sklearn.preprocessing import FunctionTransformer
from sklearn.pipeline import Pipeline
from sklearn.pipeline import FeatureUnion
from sklearn.preprocessing import StandardScaler
from os import path

from ..models.profile import Profile
from ..interfaces.helper import Helper


class Features:
    """
    TODO docstring Class Features
    """

    def __init__(
        self,
        glovePath=None,
    ):
        """
        TODO init func Class Features
        """

        self.glovePath = glovePath

        return

    def featureLIWC(
        self,
        profileCol,
    ):
        """
        TODO func featureLIWC
        from profileCollection as input in pipeline
        extract the relevant LIWC features
        """
        # will contain the LIWC measures for each profile
        outputList = []

        # loop over profileCollection
        for profile in profileCol:
            # create row
            liwc_data = []
            # get names of liwc categories
            for attrName in Profile.liwc_category_list:
                # get value of current category
                attr = getattr(profile, attrName)
                # append to current profile
                # and convert to float
                liwc_data.append(np.float(attr))

            outputList.append(liwc_data)

        # create numpy array, as scikit needs this format
        return np.array(outputList)

    def createLIWCFeaturePipeline(
        self,
    ):
        """
        TODO func createLIWCFeaturePipeline
        create pipeline that can be passed into multiple training procceses
        this is just a blueprint for calculating the features
        no features are calculated yet!
        """

        # Create skicit-learn compatible FunctionTransformers
        # for usage with other sklearn functions
        # featureLIWC is the name of the function to be called to
        # extract features
        liwc_Trans = FunctionTransformer(self.featureLIWC, validate=False)

        # Combine feature(s) with FeatureUnion
        featureTransformer = FeatureUnion([
                                ('liwc', liwc_Trans),
                                ], n_jobs=-1)  # parallelize via multiprocess

        # combine into a pipeline including scaling
        featurePipeline = Pipeline([
                ('features', featureTransformer),
                ("stdScaler", StandardScaler())
        ])

        return featurePipeline

    def loadGloVe(
        self,
    ):
        """
        TODO func featureGloVe
        from profileList as input in pipeline
        extract the relevant GloVe features
        """

        if self.glovePath is None:
            eString = "No GloVe path passed in Features class"
            raise Exception(eString)

        if path.exists(self.glovePath) is False:
            # file does not exist
            eString = "Did not find GloVe file passed in Features class"
            raise Exception(eString)

        print("\nLoading GloVe")

        # file exists, so we load it
        glove_df = pandas.read_csv(
            filepath_or_buffer=self.glovePath,
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

    def _condenseGloVeVectors(
        self,
        vectorList,
    ):
        """
        TODO func condenseGloVeVectors
        min max average
        """

        # convert to np array for mean,max,min functions
        vectorList = np.array(vectorList)

        # for each dimension identify mean,max,min
        # and save in separate vector
        meanVector = vectorList.mean(axis=0)
        maxVector = np.amax(a=vectorList,axis=0)
        minVector = np.amin(a=vectorList,axis=0)

        # combine all 300 dim vectors in 900 dim vector
        returnVector = []
        returnVector.extend(meanVector)
        returnVector.extend(maxVector)
        returnVector.extend(minVector)

        # convert to numpy array for scikit
        returnVector = np.array(returnVector)

        return returnVector

    def featureGloVe(
        self,
        profileList,
    ):
        """
        TODO func featureGloVe
        from profileList as input in pipeline
        extract the relevant GloVe features
        """
        # will contain the GloVe measures for each profile
        outputList = []
        
        # load pre trained GloVe word embedding
        glove_df = self.loadGloVe()

        # initialize progress bar
        helper = Helper()
        numProfiles = len(profileList)
        helper.printProgressBar(
            0,
            numProfiles,
            prefix='Progress:',
            suffix='Complete',
            length=50
        )

        # list for saving coverage statistics
        coverageStatistics = []

        # loop over profileList
        for num, profile in enumerate(profileList):
            # tokenize text in tweets
            # separated by space
            tokens = profile.text.split(' ')

            # for each word lookup glove vector
            # if no match -> ignore it
            profile_vectors = []
            for token in tokens:
                if token in glove_df.index:
                    # token is in glove
                    glove_values = glove_df.loc[token]
                    converted_vals = np.array(glove_values)
                    # add vector to list of this profile's vectors
                    profile_vectors.append(converted_vals)
                else:
                    # token is not in glove
                    continue

            # fill coverage statistics as share of tokens (=words)
            # that exist in glove in comparison to total tokens
            profile_coverage =  len(profile_vectors) / len(tokens)
            # add to global list
            coverageStatistics.append(profile_coverage)

            # after all vectors for this profile are retrieved
            # condense with maximum, minimum, average in 900 dim vector
            final_vector = self._condenseGloVeVectors(profile_vectors)

            # add 900 dim to output list
            outputList.append(final_vector)

            # Update Progress Bar
            helper.printProgressBar(
                num + 1,
                numProfiles,
                prefix='Progress:',
                suffix='Complete',
                length=50
            )

        # save coverage statistics in class attribute to be accessible
        self.coverageStatistics = coverageStatistics

        # create numpy array, as scikit needs this format
        return np.array(outputList)

    def createGloVeFeaturePipeline(
        self,
    ):
        """
        TODO func createGloVeFeaturePipeline
        create pipeline that can be passed into multiple training procceses
        this is just a blueprint for calculating the features
        no features are calculated yet!
        """

        # Create skicit-learn compatible FunctionTransformers
        # for usage with other sklearn functions
        # featureGloVe is the name of the function to be called to
        # extract features
        glove_Trans = FunctionTransformer(self.featureGloVe, validate=False)

        # Combine feature(s) with FeatureUnion
        featureTransformer = FeatureUnion([
                                ('glove', glove_Trans),
                                ], n_jobs=-1)  # parallelize via multiprocess

        # combine into a pipeline, no scaling since GloVe is scaled
        featurePipeline = Pipeline([
                ('features', featureTransformer)
        ])

        return featurePipeline
