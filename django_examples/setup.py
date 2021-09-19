import setuptools

setuptools.setup(
    name="modal-examples",
    version="0.0.1",
    author="Ian Jones",
    description="Modal examples",
    include_package_data = True,
    packages=['modal_examples'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
