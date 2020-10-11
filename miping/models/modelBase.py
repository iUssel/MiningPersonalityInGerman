import onnxmltools
from skl2onnx.common.data_types import FloatTensorType
from joblib import dump, load


class ModelBase:
    """
    Class meant to be subclassed.
    Every new model should call the construct of ModelBase.
    This ensures a unified interface.
    """

    @staticmethod
    def importModelPickle(
        path
    ):
        """
        Import pickle file from given path.

        Since pickle is binary, be aware of security issues
        when importing from unkown sources. Therefore extra
        user confirmation is required for importing.

        Parameters
        ----------
        path : string, default=None
            Full absolute path for model pickle file.
        """
        print("Do not import pickle models from unknown sources!")
        # import model from pickle file
        print(
            "Importing pickle from path " +
            str(path)
        )
        answer = input("Confirm action by typing yes: ")
        if answer == "yes":
            model = load(path)
            return model
        else:
            print("Import aborted by user")
            return

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
        Init function to set relevant model parameters.

        Parameters
        ----------
        labelName : string, default=""
            Indicates for which Big Five dimension the model is.
        modelName : string, default=""
            Model algorithm type (e.g. linear, SVM etc.).
        model : Python object, default=None
            Any Python object that has fit and predict functions such as
            sklearn models. If only prediction is relevant, only predict
            function is needed (e.g. the case with ONNX).
        params : dict, default=None
            After full training the model parameters can be stored here.
        scores : dict, default=None
            After full training the model scores can be stored here.
        gridSearchParams : dict, default=None
            Parameters to control for during grid search.
        """
        # save all variables in class instance
        self.labelName = labelName
        self.modelName = modelName
        self.model = model
        self.params = params
        self.scores = scores
        self.gridSearchParams = gridSearchParams

        return

    def __str__(self):
        return (self.modelName + " for " + self.labelName)

    def getModel(
        self,
    ):
        """
        Returns saved model.
        """

        return self.model

    def exportModelPickle(
        self,
        path,
    ):
        """
        Export model object to pickle file.

        Parameters
        ----------
        path : string, default=None, required
            Full path for export file.
        """
        print(
            "Exporting pickle of " +
            str(self.__str__()) +
            " to path " +
            str(path)
        )
        dump(self, path)

        return

    def exportModelONNX(
        self,
        path,
        numDim,
        inputName,
    ):

        """
        Export model object to ONNX file.

        Parameters
        ----------
        path : string, default=None, required
            Full path for export file.
        numDim : integer, default=None, required
            Number of dimensions in features used to
            train this model. For LIWC 93, for
            GloVe 300.
        inputName : string, default=None, required
            Name for Input, e.g. liwc_input. Can be any string.
        """
        print(
            "Exporting ONNX of " +
            str(self.__str__()) +
            " to path " +
            str(path)
        )

        # The following line means for example we have a 93-Dimensional
        # float feature vector (-> the LIWC values)
        # and its name is "liwc_input" in ONNX.
        # depends on input variables
        initial_type = [(inputName, FloatTensorType([None, numDim]))]

        # Convert model to ONNX format
        onnx_model = onnxmltools.convert_sklearn(
            model=self.model,
            initial_types=initial_type
        )

        # export model to file
        onnxmltools.utils.save_model(onnx_model, path)

        return onnx_model
