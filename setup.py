from setuptools import setup

setup(
    name="pydrodesign-joaquin.segura.ellis",
    version="1.0.0",
    author="Joaquin Sebastian Segura Ellis",
    author_email="joaquin.segura.ellis@mi.unc.edu.ar",
    url="https://github.com/JoaquinSeguElli/pydrodesign",
    description="Tools for Hydrology Design.",
    packages=find_packages(),
    classifiers=[
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Hydrology",
    ],
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
)
