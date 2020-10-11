
import onnxruntime as oonxrt
import numpy

from .modelBase import ModelBase


class OnnxModel(ModelBase):
    """
    OnnxModel Subclass of ModelBase
    Used when reimporting ONNX models and used just for prediction
    not for training, since ONNX models do not offer the full features
    their original models had.
    """

    def importModelONNX(
        self,
        path
    ):
        """
        Import model from ONNX file.

        Parameters
        ----------
        path : string, default=None, required
            Full path for ONNX file to import.
        """
        # import model from onnx file
        print(
            "Importing ONNX model from path " +
            str(path)
        )
        with open(path, "rb") as in_file:
            # onnx model is needed as bytes
            data = in_file.read()

        self._trainedOnnxModel = data

        return

    def __init__(
        self,
        modelName,
        labelName,
        trainedOnnxModel=None,
    ):
        """
        Init function where super constrcutor is passed with reference
        to own object.

        Parameters
        ----------
        modelName : string, default=None, required
            Model algorithm type (e.g. linear, SVM).
        labelName : string, default=None, required
            Big Five dimension this model was trained for.
        trainedOnnxModel : string, default=None
            Full absolute path for file to be loaded via yaml.safe_load().
        """
        # onnx model just for internal use
        self._trainedOnnxModel = trainedOnnxModel

        super().__init__(
            modelName=modelName,
            labelName=labelName,
            # passing self, so that when predict function is called on
            # model, this will call the predict function we implemented
            # here
            model=self,
        )

        return

    def predict(
        self,
        X
    ):
        """
        Make prediction based on input X and return numpy array.

        Prediction with ONNX models works differently, therefore
        this wrapper function was created. So on the outside,
        the ONNX model works the same as a sklearn model.

        Parameters
        ----------
        X : features, default=None, required
            Features need to match the shape this model was originally
            trained with (e.g. LIWC 93 dimensions).

        Returns
        -------
        pred_onx_flat : numpy array
            Array containing the Big Five dimension predictions based on
            input X.
        """
        if self._trainedOnnxModel is None:
            raise Exception("Empty ONNX Model")

        # prepare sessions for onnx
        sess = oonxrt.InferenceSession(self._trainedOnnxModel)
        input_name = sess.get_inputs()[0].name
        label_name = sess.get_outputs()[0].name
        # perform prediction with onnx model
        pred_onx = sess.run(
            [label_name], {input_name: X.astype(numpy.float32)}
        )[0]

        pred_onx_flat = pred_onx.flatten()

        return pred_onx_flat

    def fit(
        self,
        X,
        y
    ):
        """
        To prevent false usage of ONNX models, fit function is
        implemented but raises an error, since ONNX models cannot
        be trained the same way sklearn models are trained.
        """
        raise Exception(
            "ONNX models are only for prediction" +
            "Training via fit function not possible."
        )
