import os
from setuptools import find_packages, setup

package_name = 'ur5_moveit_py_demo'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
	(os.path.join('share', package_name, 'launch'), ['launch/plan_and_execute.launch.py']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='sahar',
    maintainer_email='sahar.samanipour@gmail.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'plan_and_execute = ur5_moveit_py_demo.plan_and_execute:main',
        ],
    },
)
