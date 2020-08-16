import miping.models as mipingModels

from pathlib import Path
import numpy as np

from miping.training.features import Features
from miping.training.modelTraining import ModelTraining
from miping.models.profileCollection import ProfileCollection
from miping.interfaces.helper import Helper
from miping.application import ModelApplication
from .preparationProcess import PreparationProcess
from scipy.stats.stats import pearsonr


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

    def createModels(
        self,
        step='LIWC',
    ):
        """
        TODO docstring createModels

        returns modelList
        """

        if step == 'LIWC':
            configString = 'liwcModelSelection'
        elif step == 'glove':
            # glove
            configString = 'gloveModelSelection'
        else:
            raise Exception("Unknown step in createModels")

        # this will contain all model instances that we want to train
        modelList = []

        # get model names from config
        # list of models to be created
        # not safe, but this is
        loadModels = []
        for model in self.modelConfig[configString]:
            loadModels.append(model)

        # gridsearch parameters from config
        gridParams = self.modelConfig[configString]

        # create model instances with grid search parameters
        # loaded from config
        for loadModel in loadModels:
            # load config for this model
            params = gridParams[loadModel]
            # check if model class exists
            if hasattr(mipingModels, loadModel) is False:
                exceptString = (
                    "Model " +
                    str(loadModel) +
                    " does not exist in MiPInG." +
                    "Check config_models.yml."
                )
                raise Exception(exceptString)
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
        profileCol,
        writePickleFiles=False,
        readPickleFiles=False,
        writeONNXModel=False,
        readONNXModel=False,
    ):
        """
        TODO doLIWCModelTraining
        """

        if writePickleFiles is True and readPickleFiles is True:
            raise Exception(
                "readFiles and writeFiles cannot be True at the same time."
            )

        if writeONNXModel is True and readONNXModel is True:
            raise Exception(
                "writeONNXModel and readONNXModel cannot be " +
                "True at the same time."
            )

        if readPickleFiles is True and readONNXModel is True:
            raise Exception(
                "readPickleFiles and readONNXModel cannot be " +
                "True at the same time."
            )

        if readPickleFiles is True:
            print("\nReading files for LIWC model training from pickle")
            # load models in this dict
            globalTrainedModels = {}
            # load models (one for each label (big 5 dimension))
            for label in self.config['labelsGlobalList']:
                # path for saved trained models
                file_directory_string = (
                    'data/trainedModels/'
                )
                # concatenate file path
                file_path = Path(
                    file_directory_string +
                    label +
                    ".pickle"
                )
                # call import function for model
                impModel = mipingModels.ModelBase.importModelPickle(
                    file_path
                )
                globalTrainedModels[label] = impModel

            for model in globalTrainedModels.values():
                # print model names to confirm which models are loaded
                print(model.__str__())
            print("Pickle import finished")

        elif readONNXModel is True:
            print("\nReading files for LIWC model training from ONNX")
            # load models in this dict
            globalTrainedModels = {}
            # load models (one for each label (big 5 dimension))
            for label in self.config['labelsGlobalList']:
                # path for saved trained models
                file_directory_string = (
                    'data/trainedModels/'
                )
                # concatenate file path
                file_path = Path(
                    file_directory_string +
                    label +
                    ".ONNX"
                )
                # import onnx model
                onnx = mipingModels.OnnxModel(
                    modelName="ONNX Model",
                    labelName=label,
                )
                onnx.importModelONNX(file_path)
                globalTrainedModels[label] = onnx

            for model in globalTrainedModels.values():
                # print model names to confirm which models are loaded
                print(model.__str__())

            print("ONNX import finished")
        else:
            print("\nStart of LIWC Model Training")

            # create feature pipeline
            features = Features()
            liwcFeaturePipeline = features.createLIWCFeaturePipeline()

            # create list of models with parameters
            # this list will be used for model selection
            modelList = self.createModels(step='LIWC')

            # begin training
            modelTraining = ModelTraining(
                labelsGlobalList=self.config['labelsGlobalList'],
                printIntermediateResults=self.config['printDetailResults']
            )
            globalBestModels = modelTraining.startModelSelection(
                modelObjList=modelList,
                featurePipeline=liwcFeaturePipeline,
                profileColTraining=profileCol,
            )

            # fully train model in different method of modelTraining
            print("\nFull model training for selected models")
            globalTrainedModels = modelTraining.completeModelTraining(
                modelCollection=globalBestModels,
                featurePipeline=liwcFeaturePipeline,
                profileColTraining=profileCol,
            )

            # only export models if specified
            if writePickleFiles is True:
                # create new line
                print("")
                # path for saving trained models
                file_directory_string = (
                    'data/trainedModels/'
                )

                # save models
                for model in globalTrainedModels.values():
                    # concatenate file path
                    file_path = Path(
                        file_directory_string +
                        model.labelName +
                        ".pickle"
                    )
                    # call export function for model
                    model.exportModelPickle(
                        file_path
                    )

            # export to ONNX
            if writeONNXModel is True:
                # create new line
                print("")
                # path for saving trained models
                file_directory_string = (
                    'data/trainedModels/'
                )

                # save models
                for model in globalTrainedModels.values():
                    # concatenate file path
                    file_path = Path(
                        file_directory_string +
                        model.labelName +
                        ".ONNX"
                    )
                    # call export function for model
                    # since it's LIWC model, 93 is input dimension
                    model.exportModelONNX(
                        path=file_path,
                        numDim=93,
                        inputName='liwc_input',
                    )

            print("\nEnd of LIWC Model Training\n")

        return globalTrainedModels

    def predictPersonalitiesLIWC(
        self,
        profileCol,
        country,
        globalLIWCModels,
        ibmList,
        readFiles=False,
        writeFiles=False,
    ):
        """
        TODO predictPersonalities
        ibmList list of countries we already got profiles
        """
        if writeFiles is True and readFiles is True:
            raise Exception(
                "readFiles and writeFiles cannot be True at the same time."
            )

        returnProfileCol = ProfileCollection()

        if readFiles is True:
            print("\nReading files for predict personalities with LIWC")
            print(
                "Loading for country: " +
                country
            )

            # path for saved profiles
            file_directory_string = (
                'data/07' +
                country +
                'full_profiles.csv'
            )
            file_path = Path(file_directory_string)

            returnProfileCol.read_profile_list_file(
                full_path=file_path
            )

            print("Files successfully loaded")
        else:
            print("\nBegin predicting personalities with LIWC")
            print(
                "Country: " +
                country
            )

            # check if already predicted via IBM
            if country in ibmList:
                print("Personalities already retrieved via IBM")
                # just return passed collection
                returnProfileCol = profileCol

            else:
                # for the remaining countries do prediction

                # create feature pipeline
                features = Features()
                liwcFeaturePipeline = features.createLIWCFeaturePipeline()
                profileList = profileCol.profileList
                features = liwcFeaturePipeline.fit_transform(profileList)
                print(
                    "Feature shape " +
                    str(features.shape)
                )

                # initialize progress bar
                helper = Helper()
                numProfiles = len(profileCol.profileList)
                helper.printProgressBar(
                    0,
                    numProfiles,
                    prefix='Progress:',
                    suffix='Complete',
                    length=50
                )

                # iterate over all profiles
                # and enrich profiles with prediction
                for num, profile in enumerate(profileCol.profileList):
                    # we just take the row with this profile's features
                    singleFeature = np.array([features[num]])
                    # for each dimension use respective model
                    for dimension, modelBase in globalLIWCModels.items():
                        profile = self.predict_profile(
                            profile=profile,
                            features=singleFeature,
                            dimension=dimension,
                            model=modelBase.model
                        )

                    # add filled profile to collection
                    returnProfileCol.add_profile(profile)

                    # Update Progress Bar
                    helper.printProgressBar(
                        num + 1,
                        numProfiles,
                        prefix='Progress:',
                        suffix='Complete',
                        length=50
                    )

            # only write file if specified
            if writeFiles is True:
                # path for saving profileCollection
                file_directory_string = (
                    'data/07' +
                    country +
                    'full_profiles.csv'
                )
                file_path = Path(file_directory_string)

                returnProfileCol.write_profile_list_file(
                    full_path=file_path
                )
            print("End predicting personalities")

        return returnProfileCol

    def predict_profile(
        self,
        profile,
        features,
        dimension,
        model,
    ):
        """
        TODO doc predict_profile
        """

        result = model.predict(features)
        setattr(profile, dimension, float(result))

        return profile

    def writeReadChecker(
        self,
        boolListRead,
        boolListWrite,
    ):
        """
        TODO writeReadChecker
        helps checking write read variables
        readVar contains names and values of readVar
        writeVar contains name and values of writeVar
        function compares based on index
        only on of 2 variable is allowed to be true
        boolListRead = [('readPickleFiles',False),('readONNXModel',False)]
        boolListWrite = [('writePickleFiles',False,),('writeONNXModel',False)]
        """
        # length must be same
        if len(boolListRead) != len(boolListWrite):
            raise ValueError("Bool Lists must have same length.")

        # iterate from 0 to length of list
        # for each index do comparison
        for i in range(0, len(boolListRead)):
            if boolListRead[i][1] is True and boolListWrite[i][1] is True:
                eString = (
                    str(boolListRead[i][0]) +
                    " and " +
                    str(boolListWrite[i][0]) +
                    " cannot be True at the same time."
                )
                raise ValueError(eString)
        return

    def importGloVeModelPickle(
        self,
    ):
        """
        TODO importModelPickle
        """
        print("\nReading files for GloVe model training from pickle")
        # load models in this dict
        globalTrainedModels = {}
        # load models (one for each label (big 5 dimension))
        for label in self.config['labelsGlobalList']:
            # path for saved trained models
            file_directory_string = ('data/trainedModels/glove')
            # concatenate file path
            file_path = Path(
                file_directory_string +
                label +
                ".pickle"
            )
            # call import function for model
            impModel = mipingModels.ModelBase.importModelPickle(
                file_path
            )
            globalTrainedModels[label] = impModel

        for model in globalTrainedModels.values():
            # print model names to confirm which models are loaded
            print(model.__str__())
        print("Pickle import finished")

        return globalTrainedModels

    def importGloVeModelONNX(
        self,
    ):
        """
        TODO importModelONNX
        """
        print("\nReading files for GloVe model training from ONNX")
        # load models in this dict
        globalTrainedModels = {}
        # load models (one for each label (big 5 dimension))
        for label in self.config['labelsGlobalList']:
            # path for saved trained models
            file_directory_string = ('data/trainedModels/glove')
            # concatenate file path
            file_path = Path(
                file_directory_string +
                label +
                ".ONNX"
            )
            # import onnx model
            onnx = mipingModels.OnnxModel(
                modelName="ONNX Model",
                labelName=label,
            )
            onnx.importModelONNX(file_path)
            globalTrainedModels[label] = onnx

        for model in globalTrainedModels.values():
            # print model names to confirm which models are loaded
            print(model.__str__())

        print("ONNX import finished")

        return globalTrainedModels

    def prepareFeaturesGloVe(
        self,
        readFeatureFile,
    ):
        """
        TODO prepareFeaturesGloVe
        """
        if readFeatureFile is True:
            print("reading featureFile")
            print("\nImporting calculated features")
            # path for saved features
            file_directory_string = (
                'data/08gloveFeatures'
            )
            # concatenate file path
            file_path = Path(
                file_directory_string +
                ".npy"
            )
            # call numpy load function
            calc_features = np.load(
                file=file_path,
                allow_pickle=False
            )
            print("Feature shape: " + str(calc_features.shape))
            gloveFeaturePipeline = None
            features = None
        else:
            # set to None
            calc_features = None
            # path for GloVe vectors
            file_path = Path(
                self.config["glove_path"]
            )
            # create feature pipeline
            features = Features()
            gloveFeaturePipeline = features.createGloVeFeaturePipeline(
                glovePath=file_path,
                dataBaseMode=self.config["glove_database"]
            )
        return calc_features, gloveFeaturePipeline, features

    def doGloVeModelTraining(
        self,
        profileCol,
        writePickleFiles=False,
        readPickleFiles=False,
        writeONNXModel=False,
        readONNXModel=False,
        writeFeatureFile=False,
        readFeatureFile=False,
    ):
        """
        TODO doGloVeModelTraining
        """

        # check that only one of read/write is True
        self.writeReadChecker(
            boolListRead=[
                ('readPickleFiles', readPickleFiles),
                ('readONNXModel', readONNXModel),
                # two times due to comparison with read pickle
                ('readONNXModel1', readONNXModel),
                ('readFeatureFile', readFeatureFile),
            ],
            boolListWrite=[
                ('writePickleFiles', writePickleFiles),
                ('writeONNXModel', writeONNXModel),
                ('readPickleFiles', readPickleFiles),
                ('writeFeatureFile', writeFeatureFile),
            ]
        )

        if readPickleFiles is True:
            # load models from pickle files
            globalTrainedModels = self.importGloVeModelPickle()

        elif readONNXModel is True:
            # load models from ONNX files
            globalTrainedModels = self.importGloVeModelONNX()

        else:
            print("\nStart of GloVe Model Training")

            # depending on configuration load pre calculated
            # features from file or prepare feature pipeline
            calc_features, gloveFeaturePipeline, featuresClass = (
                self.prepareFeaturesGloVe(
                    readFeatureFile
                )
            )

            # create list of models with parameters
            # this list will be used for model selection
            modelList = self.createModels(step='glove')

            # begin training
            modelTraining = ModelTraining(
                labelsGlobalList=self.config['labelsGlobalList'],
                printIntermediateResults=self.config['printDetailResults'],
                printCoefficients=False,
            )
            globalBestGloVeModels = modelTraining.startModelSelection(
                modelObjList=modelList,
                featurePipeline=gloveFeaturePipeline,
                profileColTraining=profileCol,
                saveFeatures=writeFeatureFile,
                precalculatedFeatures=calc_features,
            )

            # fully train model in different method of modelTraining
            print("\nFull model training for selected models")
            globalTrainedModels = modelTraining.completeModelTraining(
                modelCollection=globalBestGloVeModels,
                featurePipeline=gloveFeaturePipeline,
                profileColTraining=profileCol,
                saveFeatures=False,
                precalculatedFeatures=calc_features,
            )

            # coverage statistics is only calculated during
            # feature generation, which is only true
            # if features are not read from file
            if readFeatureFile is False:
                # average word coverage
                print(
                    "Average word coverage: " +
                    str(np.mean(featuresClass.coverageStatistics))
                )
                # max word coverage
                print(
                    "Maximum word coverage: " +
                    str(np.max(featuresClass.coverageStatistics))
                )
                # min word coverage
                print(
                    "Minimum word coverage: " +
                    str(np.min(featuresClass.coverageStatistics))
                )

            # write feature file
            if writeFeatureFile is True:
                print("\nExporting calculated features")
                calc_features = modelTraining.features
                # path for saving features
                file_directory_string = (
                    'data/08gloveFeatures'
                )
                # concatenate file path
                file_path = Path(
                    file_directory_string +
                    ".npy"
                )
                # call numpy save function
                np.save(
                    file=file_path,
                    arr=calc_features,
                    allow_pickle=False
                )

            # only export models if specified
            if writePickleFiles is True:
                # create new line
                print("")
                # path for saving trained models
                file_directory_string = (
                    'data/trainedModels/glove'
                )

                # save models
                for model in globalTrainedModels.values():
                    # concatenate file path
                    file_path = Path(
                        file_directory_string +
                        model.labelName +
                        ".pickle"
                    )
                    # call export function for model
                    model.exportModelPickle(
                        file_path
                    )

            # export to ONNX
            if writeONNXModel is True:
                # create new line
                print("")
                # path for saving trained models
                file_directory_string = (
                    'data/trainedModels/glove'
                )

                # save models
                for model in globalTrainedModels.values():
                    # concatenate file path
                    file_path = Path(
                        file_directory_string +
                        model.labelName +
                        ".ONNX"
                    )
                    # call export function for model
                    # since it's GloVe model, 900 is input dimension
                    model.exportModelONNX(
                        path=file_path,
                        numDim=900,
                        inputName='glove_input',
                    )

            print("\nEnd of GloVe Model Training\n")

        return globalTrainedModels

    def do_prediction(
        self,
        profileCol,
        globalGloVeModels,
        readFeatureFile=False,
    ):
        """
        TODO do_prediction
        """
        print("Now doing prediction")
        # depending on configuration load pre calculated
        # features from file or prepare feature pipeline
        calc_features, gloveFeaturePipeline, featuresClass = (
            self.prepareFeaturesGloVe(
                readFeatureFile
            )
        )

        # extract profile list
        profileList = profileCol.profileList

        if calc_features is None:
            # no features loaded from file
            # we calculate them now
            print("Calculating features for complete prediction")
            calc_features = gloveFeaturePipeline.fit_transform(profileList)

        # dimensions to predict
        labelsGlobalList=self.config['labelsGlobalList']

        # return dict
        prediction = {}

        for labelName in labelsGlobalList:
            print(
                "Prediction currently for label: " +
                str(labelName)
            )

            # select the model for this trait
            baseModel = globalGloVeModels[labelName]
            model = baseModel.model

            # for each model, we will get prediction
            prediction[labelName] = model.predict(calc_features)

        # print statistics
        print("\nStatistics for predicted values")
        dataPrep = PreparationProcess(config=None)
        for label in labelsGlobalList:
            print(label)
            dataPrep.print_min_max_mean_std(prediction[label])

        # calculate pearson correlation between prediction and actual value
        # average over each dimension
        print("\nCalculate Pearson correlation")
        pearson = {}
        for label in labelsGlobalList:
            print(label)
            predictionVal = prediction[label]
            # extract labels (e.g. values for Extraversion)
            labels = self.extractLabels(
                profileList=profileList,
                labelName=label
            )
            actualVal = labels
            pearson[label] = pearsonr(predictionVal, actualVal)
            print(
                "Correlation is " +
                str(pearson[label][0]) +
                " and p-value " +
                str(pearson[label][1])
            )

        return prediction

    def extractLabels(
        self,
        profileList,
        labelName,
    ):
        """
        TODO func extractLabels
        extract values for one specific labelName
        labels are the percentages value to predict
        e.g. for Extraversion value
        """
        # initialize return variable
        labels = []

        # loop over profile collection
        for profile in profileList:
            value = getattr(profile, labelName)
            labels.append(np.float(value))

        return labels

