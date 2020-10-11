from .modelBase import ModelBase
from sklearn import linear_model


class BayesianRidge(ModelBase):
    """
    BayesianRidge Subclass of ModelBase
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
                'n_iterint': [25],
            }

            gridSearch = defaultParams

        super().__init__(
            modelName='BayesianRidge',
            model=linear_model.BayesianRidge(),
            gridSearchParams=gridSearch
        )

        return
