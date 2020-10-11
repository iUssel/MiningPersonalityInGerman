from .modelBase import ModelBase
from sklearn.svm import SVR


class SupportVectorMachine(ModelBase):
    """
    SupportVectorMachine Subclass of ModelBase
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
                'kernel': ['linear'],
                'C': [0.01],
                'epsilon': [0.1],
                'max_iter': [300],
            }

            gridSearch = defaultParams

        super().__init__(
            modelName='SupportVectorMachine',
            model=SVR(),
            gridSearchParams=gridSearch
        )

        return
