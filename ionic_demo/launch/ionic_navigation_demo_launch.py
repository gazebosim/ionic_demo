from launch_ros.substitutions import FindPackageShare

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import PathJoinSubstitution, TextSubstitution


def generate_launch_description():

    return LaunchDescription([
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource([
                PathJoinSubstitution([
                    FindPackageShare('nav2_bringup'),
                    'launch',
                    'tb4_simulation_launch.py'
                ])
            ]),
            launch_arguments={
                'map': PathJoinSubstitution([
                   FindPackageShare('ionic_demo'),
                      'maps',
                      'ionic_demo.yaml'
                ]),
                'world': PathJoinSubstitution([
                   FindPackageShare('ionic_demo'),
                      'worlds',
                      'ionic.sdf'
                ]),
                'x_pose': '0.0',
                'y_pose': '0.0',
                'z_pose': '0.0'
            }.items()
        )
    ])
