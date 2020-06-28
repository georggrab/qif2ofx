import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="qif2ofx", # Replace with your own username
    version="0.1.0",
    author="Georg Grab",
    author_email="git@georggrab.net",
    description="Convert from QIF to OXF",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/talkdirty/qif2ofx",
    packages=setuptools.find_packages(),
    scripts=[
        'scripts/qif2ofx',
        'scripts/csv2ofx'
    ],
    install_requires=[
        'ofxtools'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)

