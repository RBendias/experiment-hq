import setuptools


setuptools.setup(
    name="experiment-hq",
    version="0.1.0",
    author="ExperimentHQ",
    author_email="notiontracking@email.com",
    description="A Python SDK for tracking experiments in Notion",
    url="https://github.com/ExperimentHQ/experiment-hq",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "requests",
        "uvicorn",
        "python-dotenv"
    ],
    extras_require={
        "dev": [
            "pytest"
        ]
    },
)