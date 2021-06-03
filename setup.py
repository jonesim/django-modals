import setuptools

with open("readme.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="django-nested-modals",
    version="0.0.1",
    author="Ian Jones",
    description="Django app to implement Bootstrap nested modals",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jonesim/django-modals",
    include_package_data = True,
    packages=['django_modals'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
