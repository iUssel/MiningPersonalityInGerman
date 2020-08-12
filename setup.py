import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setuptools.setup(
    name="miping",
    version="0.0.4",
    author="Henning Usselmann",
    author_email="miping@uber.space",
    description=(
        "MiningPersonalityInGerman enables users to train and apply " +
        "machine learning models on tweets to predict a user's " +
        "Big 5 personality."
    ),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/iUssel/MiningPersonalityInGerman",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: Unix",
    ],
    python_requires='>=3.6',
    install_requires=requirements,
    setup_requires=['flake8'],
    package_data={
        'miping': [
            '.env.example',
            'trainedModels/*.ONNX',
            'webapp/webfiles/*',
        ]
    },
    include_package_data=True
)
