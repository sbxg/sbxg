from setuptools import setup

setup(
    name = "sbxg",
    version = "0.2.99",
    author = "SBXG Team",
    author_email = "jean@guyomarch.bzh",
    description = ("A build system generator for low-level software"),
    license = "MIT",
    keywords = "build kernel bootloader hypervisor",
    url = "https://sbxg.readthedocs.io",
    packages=['sbxg', 'sbxg.lib', 'sbxg.boards'],

    # This package is not zip safe! It packages a full file hierarchy, that is
    # not explicitely enumerated over in SBXG core. It is MANDATORY for this
    # parameter to be set to False, so the Egg will be installed as an unzipped
    # directory, and will not try to query its contents on-demand.
    zip_safe=False,
    package_data={
        'sbxg': [
            'templates/*.j2',
        ],
        'sbxg.lib': [
            'toolchains/*.yml',
            'configs/*/*',
            'sources/*/*.yml',
        ],
        'sbxg.boards': [
            '*/*.yml',
            'bootscripts/*.j2',
            'images/*.j2',
        ],
    },
    install_requires=['jinja2', 'cerberus', 'pyyaml'],
    python_requires='>=3.6.*',
    entry_points={
        'console_scripts': [
            'sbxg = sbxg.cli:main',
        ],
    },
    long_description="""
SBXG is a **build system generator** specialized in building from sources
low-level components that are the foundation of Linux-based embedded devices,
such as U-Boot, Linux and Xen.

It is designed to offer a **high level of reproductibility and tracability**.
Given that the URLs pointing to the different components are always available,
SBXG should always generate the same outputs for a given set of inputs. No
surprise to be expected.""",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
    ],
)
