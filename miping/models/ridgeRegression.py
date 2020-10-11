from .modelBase import ModelBase
from sklearn import linear_model


class RidgeRegression(ModelBase):
    """
    RidgeRegression Subclass of ModelBase
    """

    def __init__(
        self,
        gridSearchParams=None,
    ):
        """
        Init function calling super constructor and setting the model.

        Parameters
        ----------
        gridSearchParams : dict, default=None
            Dictionary containing all parameters that should be
            considered during grid search.
        """
        if gridSearchParams is not None:
            gridSearch = gridSearchParams
        else:
            # applying default parameters
            defaultParams = {
                'alpha': [20],
                'random_state': [0]
            }
            gridSearch = defaultParams

        super().__init__(
            modelName='RidgeRegression',
            model=linear_model.Ridge(),
            gridSearchParams=gridSearch
        )

        return
