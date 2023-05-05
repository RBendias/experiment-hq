import os
import setuptools

VERSION = '0.1.0'
DESCRIPTION = 'A Python package for tracking experiments in Notion'
URL = "https://github.com/EperimentHQ/experiment-hq"
WEBSITE = "https://ml-notion-tracking-ui-vs3h.vercel.app/"



# Import the README and use it as the long-description.
PWD = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(PWD, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setuptools.setup(
    name="experimenthq",
    version=VERSION,
    author="ExperimentHQ",
    author_email="notiontracking@email.com",
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=URL,
    packages=setuptools.find_packages(),
    packages=setuptools.find_packages(where="src", exclude=("tests", "test", "examples", "docs")),
    package_dir={"": "src"},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Natural Language :: English",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Information Technology",
        "Topic :: Scientific/Engineering",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Utilities",

    ],
    project_urls={
        "Changelog": URL + "/releases",
        "Issue Tracker": URL + "/issues",
        "Documentation": URL + "#documentation",
        "Source": URL,
        "Website": WEBSITE,
    },
    keywords=["notion", "tracking", "ml", "machine learning", "experiment", "experimentation", "experiment tracking", 
              "python", "sync",]
    python_requires=">=3.6",
    install_requires=[
        "requests",
    ],
    extras_require={
        "dev": [
            "pytest",
            "pytest-cov",
            "flake8",
            "black",
            "isort",
            "mypy",
            "twine",
            "wheel",
            "setuptools",
            "build",
        ]
    },
)