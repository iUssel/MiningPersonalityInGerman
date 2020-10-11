import miping.models as mipingModels

from pathlib import Path
import numpy as np

from miping.training.features import Features
from miping.training.modelTraining import ModelTraining
from miping.models.profileCollection import ProfileCollection
from miping.interfaces.helper import Helper
from .preparationProcess import PreparationProcess
from scipy.stats.stats import pearsonr


class TrainingProcess:
    """
    Wrapper class for training process (3rd step).
    Contains all functions needed for training and evaluation.
    Calls mostly miping module functions and allows imports
    and exports of data via csv.
    """

    def __init__(
        self,
        config,
        modelConfig,
    ):
        """
        Init function for configurations.

        Parameters
        ----------
        config : dict, default=None, required
            Configuration object as returned from ConfigLoader class.
        modelConfig : dict, default=None, required
            Configuration object for model training and grid search
            as returned from ConfigLoader class.
        """

        self.config = config
        self.modelConfig = modelConfig

        return

    def createModels(
        self,
        step='LIWC',
    ):
        """
        Initialize models with grid search parameters and create a model list.

        Step decides which grid search parameters to select
        from model configuration. Based on the model configuration
        it will be checked if miping.models has fitting classes for
        the given model names (if not an exception is raised).
        If it has, an instance of that class is created with
        the corresponding grid search parameters as input.
        All model instances are collected in a list.

        Parameters
        ----------
        step : string, default='LIWC'
            Indicates if LIWC or glove models should be created.

        Returns
        -------
        modelList : list
            List of created models with grid search parameters.
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
        Return trained and selected LIWC models.

        Based on the given profile collection do LIWC model training.
        First initialize LIWC feature pipeline. Then create model list.
        Select best models and in the end do a complete training
        for the best models.
        Models can be imported and exported via pickle and ONNX files.
        Pickle files are binaries and therefore should be treated with
        care in terms of security.
        Expected paths are:
        'data/trainedModels/' + label + ".pickle"
        'data/trainedModels/' + label + ".ONNX"

        Parameters
        ----------
        profileCol : ProfileCollection, default=None, required
            ProfileCollection to use as training input.
        writePickleFiles : boolean, default=False
            Export trained models as pickle files if True.
        readPickleFiles : boolean, default=False
            Import trained models from pickle file.
        writeONNXModel : boolean, default=False
            Export trained models to ONNX file.
        readONNXModel : boolean, default=False
            Import trained models from ONNX file.

        Returns
        -------
        globalTrainedModels : dict
            Trained, tuned, and selected models for LIWC predictions.
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

            # extract USA from profile collection
            profileCol = profileCol['USA']

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
        Predict Big Five personality scores for profiles based on LIWC models.

        Allows imports and exports of results via CSV. Expected path is
        'data/07' + country + 'full_profiles.csv'.
        If the given country exists in the ibmList the ProfileCollection
        is returned unmodified, as the Big Five score have been retrieved
        via IVM API. Otherwise, the LIWC feature pipeline is
        initialized and features are calculated for all profiles.
        With these features predictions will be carried out per profile
        and Big Five dimension. Profiles will be enriched with Big Five
        information and returned.
        During the predictions a progress bar is shown.

        Parameters
        ----------
        profileCol : ProfileCollection, default=None, required
            ProfileCollection containing profiles to do LIWC based predictions
            for.
        country : string, default=None, required
            Country name of where the passed users are collected from
            (as specified in config)
        globalLIWCModels : dict, default=None, required
            Fully trained LIWC models ready for making predictions.
        ibmList : string, default=None, required
            List of countries for which Big Five scores have been
            retrieved via IBM API. For those no prediction is carried out.
        readFiles : boolean, default=False
            If True, CSV files will be read instead of following program
            logic.
        writeFiles : boolean, default=False
            Can only be True, if readFiles is False. If True, will export
            results to CSV files. Allows to read files in the next program
            run.

        Returns
        -------
        returnProfileCol : ProfileCollection
            ProfileCollection enriched with Big Five personality information
            based on LIWC model predictions.
            If country was in IBM list, the Big Five information already
            existed and are not modified.
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
        Return profile with filled, predicted Big Five value for dimension.

        Parameters
        ----------
        profile : Profile, default=None, required
            User profile for which prediction should be carried out.
        features : numpy.array, default=None, required
            Calculated features for this profile on which prediction
            is based.
        dimension : string, default=None, required
            Big Five dimension name. This is the attribute name
            under which the value will be saved in the profile.
        model : miping.models.ModelBase.model, default=None, required
            Trained model with function predict to predict the given
            Big Five dimension.

        Returns
        -------
        profile : Profile
            Profile with set dimension attribute.
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
        Check if given lists fulfill consistency criteria.

        For most functions we allow to either import or export results.
        It is not possible to both import and export at the same time.
        Therefore we check the variables with this function.
        The function compares based on index.
        So e.g. index 0 of boolListRead and boolListWrite cannot be True at
        the same time. Both parameters need to be list of the same length.
        Each list element consists of a tuple, where 1st tupel element
        is the variable name and the second is its Boolean value.
        An example:
        boolListRead = [('readPickleFiles',False),('readONNXModel',True)]
        boolListWrite = [('writePickleFiles',False,),('writeONNXModel',True)]
        If these were passed in the function an exception would be raised,
        because the second item in the lists is True in both lists.

        Parameters
        ----------
        boolListRead : list, default=None, required
            List of tuples (name, boolean) for read values to check.
        boolListWrite : boolean, default=None, required
            List of tuples (name, boolean) for write values to check.
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
        Import and return GloVe models from pickle file.

        Import previously exported models. The expected path is:
        'data/trainedModels/glove' + label + ".pickle".
        For actual import `mipingModels.ModelBase.importModelPickle` is
        called and the resulting model objects are captured in a
        dictionary with Big Five dimension names as keys.

        Returns
        -------
        globalTrainedModels : dict
            Dictionary containing the imported trained GloVe models.
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
        Import and return GloVe models from ONNX file.

        Import previously exported models. The expected path is:
        'data/trainedModels/glove' + label + ".ONNX".
        For actual import `mipingModels.OnnxModel.importModelONNX` is
        called and the resulting model objects are captured in a
        dictionary with Big Five dimension names as keys.

        Returns
        -------
        globalTrainedModels : dict
            Dictionary containing the imported trained GloVe models.
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
        Depending on parameter import precalculated features or prepare
        feature pipeline.

        To save time precalculated features (exported in a previous run),
        can be imported. Expected path is 'data/08gloveFeatures.npy'.
        If those are not imported the glove feature pipeline is created
        and returned.
        For glove feature pipeline "glove_path" and "glove_database"
        have to be set in the global configuration to point to the glove
        vector file.
        All variables are returned, but might be empty depending on flag.

        Parameters
        ----------
        readFeatureFile : boolean, default=None, required
            Flag to indicate if precalculated features should be read
            or only pipeline should be prepared.

        Returns
        -------calc_features, gloveFeaturePipeline, features
        calc_features : numpy.array
            Imported precalculated features or empty (depending on flag).
        gloveFeaturePipeline : Pipeline
            If flag is true, then pipeline is none. If flag is false,
            pipeline is created glove feature pipeline.
        features : Features
            If flag is true, then features is none. If flag is false,
            its Features object instance used to create pipeline.
            Later relevant for word coverage statistics.
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
        Based on given profile collection do GloVe model training.

        Multiple import and export options are available.
        Trained models can be imported and exported via pickle or ONNX.
        This is controlled via parameters, but you can only import via
        ONNX or pickle, not both at the same time, otherwise an exception
        will be thrown. On the other hand, it is possible to simultaneously
        export to both pickle and ONNX.
        Expected paths are defined in `TrainingProcess.importGloVeModelPickle`
        and `TrainingProcess.importGloVeModelONNX`.
        At first, depending on the readFeatureFile flag, the glove feature
        pipeline is imported or precalculated features are imported via
        `TrainingProcess.prepareFeaturesGloVe`.
        Afterwards the modelList is created to start modelselection
        afterwards. This results in the best models which will be completely
        trained in the end. If features were not imported, the word coverage
        statistics is printed.

        Parameters
        ----------
        profileCol : string, default=None, required
            ProfileCollection as input for GloVe model training.
        writePickleFiles : boolean, default=False
            If True, final models will be exported to pickle files.
        readPickleFiles : boolean, default=False
            If True, instead of training trained models will be imported
            from pickle files.
        writeONNXModel : boolean, default=False
            If True, final models will be exported to ONNX files.
        readONNXModel : boolean, default=False
            If True, instead of training trained models will be imported
            from ONNX files.
        writeFeatureFile : boolean, default=False
            Calculated features will be exported via numpy.dump function
            if True.
        readFeatureFile : boolean, default=False
            Previously exported features can be imported if True.

        Returns
        -------
        globalTrainedModels : dict
            Selected, tuned, and trained GloVe models.
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
        Do GloVe based prediction for profile collection and return result.

        This function is for comparing true with predicted values via
        Pearson correlation.
        At first import or calculate features. Then do prediction for
        each dimension. Descriptive statistics for prediction values
        are printed. Pearson correlation coefficients are calculated.

        Parameters
        ----------
        profileCol : ProfileCollection, default=None, required
            ProfileCollection to do GloVe prediction for.
        globalGloVeModels : dict, default=None, required
            Dictionary with fully trained GloVe models.
        readFeatureFile : boolean, default=False
            If True features are read from file.

        Returns
        -------
        prediction : dict
            Dictionary containing the predicted numeric values for each
            Big Five dimension.
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
        labelsGlobalList = self.config['labelsGlobalList']

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
        Extract and return list of attribute values from objects in
        profileList.

        Parameters
        ----------
        profileList : list, default=None, required
            List of Profile objects for which to extract the label values.
        labelName : string, default=None, required
            Attribute value to extract from profileList. Usually a Big Five
            dimension

        Returns
        -------
        labels : list
            List of float values for one Big Five dimension.
        """
        # initialize return variable
        labels = []

        # loop over profile collection
        for profile in profileList:
            value = getattr(profile, labelName)
            labels.append(np.float(value))

        return labels
