class ModelBase:
    """
    TODO docstring Class ModelBase
    """

    def __init__(
        self,
        labelName="",
        modelName="",
        model=None,
        params=None,
        scores=None,
        gridSearchParams=None,
    ):
        """
        TODO init func Class ModelBase
        """
        # save all variables in class instance
        self.labelName = labelName
        self.modelName = modelName
        self.model = model
        self.params = params
        self.scores = scores
        self.gridSearchParams = gridSearchParams

        return

    def getModel(
        self,
    ):
        """
        TODO func getModel
        returns saved model
        """

        return self.model
