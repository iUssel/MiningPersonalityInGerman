from .modelBase import ModelBase
from sklearn.ensemble import RandomForestRegressor


class RandomForest(ModelBase):
    """
    TODO docstring Class RandomForest
    """

    def __init__(
        self,
        gridSearchParams=None,
    ):
        """
        TODO init func Class RandomForest
        gridSearchParams: dict
        """

        if gridSearchParams is not None:
            gridSearch = gridSearchParams
        else:
            # TODO applying best default parameters
            defaultParams = {
                'criterion': ['mse'],
                'n_estimators': [10, 50, 100, 200],
                'max_depth': [2, 5, 10, None],
                'min_samples_split': [2, 5, 10],
                'min_samples_leaf': [1, 2, 5, 10],
                'max_leaf_nodes': [100, 500, None],
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
