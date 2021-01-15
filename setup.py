from setuptools import setup, find_packages


setup(
    name="archipel_client",
    version="0.0.1",
    install_requires=[
        "msgpack==1.0.0",
        "numpy==1.19.4",
        "opencv-python==4.5.1.48",
        "websockets==8.1",
    ],
    packages=find_packages(),
    python_requires=">=3.8",
)
