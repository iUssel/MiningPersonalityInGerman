import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="miping",
    version="0.0.1",
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
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
