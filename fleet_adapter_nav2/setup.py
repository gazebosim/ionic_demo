from glob import glob
import os

from setuptools import find_packages
from setuptools import setup

package_name = 'fleet_adapter_nav2'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        (
            'share/ament_index/resource_index/packages',
            ['resource/' + package_name],
        ),
        ('share/' + package_name, ['package.xml']),
        (
            os.path.join('share', package_name, 'config'),
            glob('config/*.yaml'),
        ),
        (
            os.path.join('share', package_name, 'launch'),
            glob('launch/*.launch.xml'),
        ),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='xiyuoh',
    maintainer_email='xiyu@openrobotics.org',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'fleet_adapter=fleet_adapter_nav2.fleet_adapter_nav2:main',
        ],
    },
)
