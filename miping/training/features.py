import numpy as np

from sklearn.preprocessing import FunctionTransformer
from sklearn.pipeline import Pipeline
from sklearn.pipeline import FeatureUnion
from sklearn.preprocessing import StandardScaler

from ..models.profile import Profile


class Features:
    """
    TODO docstring Class Features
    """

    def __init__(
        self,
    ):
        """
        TODO init func Class Features
        """
        pass

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
            for attr in Profile.liwc_category_list:
                # get value of current category
                attr = getattr(profile, attr)
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

    def createGloVeFeaturePipeline(
        self,
    ):
        """
        TODO funct createGloVeFeaturePipeline
        placeholder
        """

        pass
