from setuptools import setup, find_packages

setup(
    name="pydrodesign",
    version="1.0.0",
    author="Joaquin S. Segura Ellis",
    author_email="joaquin.segura.ellis@mi.unc.edu.ar",
    url="",
    description="",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=["click", "pytz"],
    entry_points={"console_scripts": ["cloudquicklabs1 = src.main:main"]},
)
