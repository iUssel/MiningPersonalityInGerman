import os


class TrainedModels:
    """
    TODO docstring Class TrainedModels
    provides paths for trained model files
    """

    # big 5 list for loops
    big5List = [
        'big5_openness',
        'big5_conscientiousness',
        'big5_extraversion',
        'big5_agreeableness',
        'big5_neuroticism',
    ]

    def __init__(
        self,
    ):
        """
        TODO init func Class TrainedModels
        precalculate path for folder in which models are saved
        MiningPersonalityInGerman/miping/trainedModels/...
        file_path_dict = {
            'big5_openness': {
                'onnx': /miping/trainedModels/glovebig5_openness.ONNX,
                'pickle': /miping/trainedModels/glovebig5_openness.pickle
            },
            ...
        }
        """

        # identify current directory
        # in this directory are all trained models
        directory = os.path.dirname(__file__)

        # save paths in dict
        self.file_path_dict = {}

        # build dict with file paths
        for dimension in self.big5List:
            # set key
            self.file_path_dict[dimension] = {}
            # set file path to onnx
            self.file_path_dict[dimension]['onnx'] = os.path.join(
                directory,
                ('glove' + str(dimension) + '.ONNX')
            )
            # set file path to pickle
            self.file_path_dict[dimension]['pickle'] = os.path.join(
                directory,
                ('glove' + str(dimension) + '.pickle')
            )

        return

    def get_file_path_dict(
        self,
    ):
        """
        TODO get_file_path_dict
        """

        return self.file_path_dict
