# Copyright (C) 2024 Open Source Robotics Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from pathlib import Path

from ament_index_python.packages import get_package_share_directory, get_package_prefix
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare, FindPackagePrefix
from launch_xml.launch_description_sources import XMLLaunchDescriptionSource

from launch import LaunchDescription
from launch.actions import AppendEnvironmentVariable, DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, FindExecutable, LaunchConfiguration, PathJoinSubstitution, TextSubstitution

def generate_launch_description():
    ionic_demo_dir = Path(get_package_share_directory('ionic_demo'))
    rmf_demos_dir = Path(get_package_share_directory('rmf_demos'))
    ionic_maps_dir = Path(get_package_share_directory('ionic_demo_building_maps'))
    fleet_adapter_dir = Path(get_package_share_directory('fleet_adapter_nav2'))
    server_uri = LaunchConfiguration('server_uri')
    declare_server_uri_cmd = DeclareLaunchArgument(
        'server_uri', default_value='', description='Open-RMF API server URI'
    )

    teleport_ingestor_string = \
    '''
    <sdf version="1.6">
        <include>
            <name>coke_ingestor</name>
            <uri>
                model://TeleportIngestor
            </uri>
        </include>
    </sdf>
    '''

    # URDF
    _robot_description_xml = Command(
        [
            PathJoinSubstitution([FindExecutable(name="xacro")]),
            " ",
            PathJoinSubstitution(
                [FindPackageShare('panda_description'), 'urdf', 'panda.urdf.xacro']
            ),
            " ",
            "name:=",
            'panda',
        ]
    )
    robot_description = {"robot_description": _robot_description_xml}

    # SRDF
    _robot_description_semantic_xml = Command(
        [
            PathJoinSubstitution([FindExecutable(name="xacro")]),
            " ",
            PathJoinSubstitution(
                [
                    FindPackageShare('panda_moveit_config'),
                    "srdf",
                    "panda.srdf.xacro",
                ]
            ),
            " ",
            "name:=",
            'panda',
        ]
    )
    robot_description_semantic = {
        "robot_description_semantic": _robot_description_semantic_xml
    }
    tb4_namespace = '/tb4'

    return LaunchDescription([
        declare_server_uri_cmd,
        Node(
            # Spawn the ingestor for delivery
            package="ros_gz_sim",
            executable="create",
            output="log",
            arguments=[
                "-string", teleport_ingestor_string,
                "-x", "-0.75",
                "-y", "2.55",
                "-z", "0.75",
            ],
            parameters=[{"use_sim_time": True}],
        ),
        Node(
            # Dispenser node to control moveit arm
            package="ionic_demos_rmf",
            executable="moveit_dispenser",
            output="log",
            parameters=[
                robot_description,
                robot_description_semantic,
                {"use_sim_time": True},
            ],
        ),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                str(ionic_demo_dir / 'launch' / 'ionic_navigation_demo_launch.py')
            ),
            launch_arguments={
                'run_gazebo': 'False',
                'use_namespace': 'True',
                'namespace': '/tb4',
            }.items(),
        ),
        # Launch RMF and RMF fleet adapter
        IncludeLaunchDescription(
            XMLLaunchDescriptionSource(
                str(rmf_demos_dir / 'common.launch.xml')
            ),
            launch_arguments={
                'use_sim_time': 'True',
                'headless': 'True',
                'config_file': str(ionic_maps_dir / 'ionic_demo' / 'ionic_demo.building.yaml'),
            }.items(),
        ),
        Node(
            package="fleet_adapter_nav2",
            executable="fleet_adapter",
            output="log",
            arguments=[
                "-c", str(fleet_adapter_dir / 'config' / 'tb4_config.yaml'),
                "-n", str(ionic_maps_dir / 'maps' / 'ionic_demo' / 'nav_graphs' / '0.yaml')
            ],
            parameters=[{
                "use_sim_time": True,
                "server_uri": server_uri
            }],
            remappings=[
                ('/tf', '/tb4/tf'),
                ('/tf_static', '/tb4/tf_static'),
            ]
        ),
    ])


