import miping.models as mipingModels

from miping.training.features import Features
from miping.training.modelTraining import ModelTraining


class TrainingProcess:
    """
    TODO docstring Class trainingProcess
    """

    def __init__(
        self,
        config,
        modelConfig,
    ):
        """
        TODO init func Class trainingProcess
        """

        self.config = config
        self.modelConfig = modelConfig

        return

    def createLIWCModels(
        self,
    ):
        """
        TODO docstring createModels

        returns modelList
        """
        # this will contain all model instances that we want to train
        modelList = []

        # list of models to be created
        # easier to do it dynamically
        loadModels = [
            'BayesianRidge',
            'DecisionTree',
            'GaussianProcessRegressor',
            'RandomForest',
            'RidgeRegression',
            'SupportVectorMachine'
        ]

        # gridsearch parameters from config
        gridParams = self.modelConfig['liwcModelSelection']

        # create model instances with grid search parameters
        # loaded from config
        for loadModel in loadModels:
            # load config for this model
            params = gridParams[loadModel]
            # get model class
            class_ = getattr(mipingModels, loadModel)
            modelInstance = class_(
                gridSearchParams=params
            )
            # add model to list
            modelList.append(modelInstance)

        return modelList

    def doLIWCModelTraining(
        self,
        profileCol
    ):
        """
        TODO doLIWCModelTraining
        """
        print("\nStart of LIWC Model Training")

        # create feature pipeline
        features = Features()
        liwcFeaturePipeline = features.createLIWCFeaturePipeline()

        # create list of models with parameters
        # this list will be used for model selection
        modelList = self.createLIWCModels()

        # begin training
        modelTraining = ModelTraining(
            labelsGlobalList=self.config['labelsGlobalList']
        )
        globalBestModels = modelTraining.startModelSelection(
            modelObjList=modelList,
            featurePipeline=liwcFeaturePipeline,
            profileColTraining=profileCol,
        )

        # fully train model in different method of modelTraining
        print("\nFull model training for selected models")
        print("Auskommentiert")
        # globalTrainedModels = modelTraining.completeModelTraining(
        #    modelCollection=globalBestModels,
        #    featurePipeline=liwcFeaturePipeline,
        #    profileColTraining=profileCol,
        # )

        print("\nEnd of LIWC Model Training\n")

        return
