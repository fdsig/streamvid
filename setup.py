from setuptools import setup, find_packages

setup(
    name='streamvid',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        # List your project's dependencies here
    ],
    entry_points={
        'console_scripts': [
            # Define command-line scripts here if needed
        ],
    },
    author='Your Name',
    author_email='fdesigleyl@gmail.com',
    description='edge device web ui for video streaming and data labeling',
    url='https://github.com/fdsig/streamvid',  # Update with your project's URL
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
