from .modelBase import ModelBase
from sklearn import tree


class DecisionTree(ModelBase):
    """
    DecisionTree Subclass of ModelBase
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
                'splitter': ['best'],
                'max_depth': [4],
                'min_samples_split': [2],
                'min_samples_leaf': [50],
                'random_state': [0]
            }

            gridSearch = defaultParams

        super().__init__(
            modelName='DecisionTree',
            model=tree.DecisionTreeRegressor(),
            gridSearchParams=gridSearch
        )

        return
