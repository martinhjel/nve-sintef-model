import setuptools

with open("README.md", "r") as f:
    long_description = f.read()

with open("requirements.txt", "r") as f:
    requirements = [line.strip() for line in f]

setuptools.setup(
    name="nve_sintef_model",
    version="0.0.1",
    author="NVE",
    author_email="alro@nve.no",
    description="A python library of functions for using SINTEF models.",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=requirements,
)