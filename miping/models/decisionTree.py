from .modelBase import ModelBase
from sklearn import tree


class DecisionTree(ModelBase):
    """
    TODO docstring Class DecisionTree
    """

    def __init__(
        self,
        gridSearchParams=None,
    ):
        """
        TODO init func Class DecisionTree
        gridSearchParams: dict
        """

        if gridSearchParams is not None:
            gridSearch = gridSearchParams
        else:
            # TODO applying best default parameters
            defaultParams = {
                'criterion': ['mse'],
                'splitter': ['best'],
                'max_depth': [10],
                'min_samples_split': [2],
                'min_samples_leaf': [1],
                'random_state': [0]
            }

            gridSearch = defaultParams

        super().__init__(
            modelName='DecisionTree',
            model=tree.DecisionTreeRegressor(),
            gridSearchParams=gridSearch
        )

        return
