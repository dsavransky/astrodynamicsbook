import setuptools
import os, re

with open("README.md", "r") as fh:
    long_description = fh.read()


with open(os.path.join("astrodynamicsbook","__init__.py"), "r") as f:
    version_file = f.read()

version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",\
        version_file, re.M)

if version_match:
    version_string = version_match.group(1)
else:
    raise RuntimeError("Unable to find version string.")


setuptools.setup(
    name="astrodynamicsbook",
    version=version_string,
    author="Dmitry Savransky",
    author_email="ds264@cornell.edu",
    description="An interactive textbook on dynamics, astrodynamics, and celestial mechanics.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dsavransky/astrodynamicsbook",
    packages=['astrodynamicsbook'],
    package_data={'astrodynamicsbook': ['latex_preamble.tex']},
    install_requires=[
          'scipy',
          'numpy',
          'astropy',
          'sympy',
          'notebook',
          'matplotlib',
          'ipynbname',
          'ipympl',
          'tqdm'
    ],
    license="CC BY-NC-SA 4.0",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Operating System :: OS Independent",
    ],
)
