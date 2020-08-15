import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setuptools.setup(
    name="miping",
    version="0.1.1",
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
            'webapp/webfiles/sites-available/*',
            'webapp/webfiles/www/*',
            'webapp/webfiles/www/js/*',
            'webapp/webfiles/www/images/*',
            'webapp/webfiles/www/html/*',
            'webapp/webfiles/www/downloads/*',
            'webapp/webfiles/www/css/*',
        ]
    },
    include_package_data=True
)
