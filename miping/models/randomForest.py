from .modelBase import ModelBase
from sklearn.ensemble import RandomForestRegressor


class RandomForest(ModelBase):
    """
    RandomForest Subclass of ModelBase
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
                'criterion': ['mse'],
                'n_estimators': [50],
                'max_depth': [5],
                'min_samples_split': [2],
                'min_samples_leaf': [10],
                'max_leaf_nodes': [None],
                'max_features': [None],  # recommended for Regression
                'random_state': [0]
            }

            gridSearch = defaultParams

        super().__init__(
            modelName='RandomForest',
            model=RandomForestRegressor(),
            gridSearchParams=gridSearch
        )

        return
