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

from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare, FindPackagePrefix
from launch_xml.launch_description_sources import XMLLaunchDescriptionSource

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, FindExecutable, PathJoinSubstitution, TextSubstitution


def generate_launch_description():
    coke_can_string = \
    '''
    <sdf version="1.6">
        <include>
            <static>false</static>
            <uri>
                https://fuel.gazebosim.org/1.0/OpenRobotics/models/Coke
            </uri>
        </include>
    </sdf>
    '''

    return LaunchDescription([
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource([
                PathJoinSubstitution([
                    FindPackageShare('panda'),
                    'launch',
                    'gz.launch.py'
                ])
            ]),
            launch_arguments={
                'world': PathJoinSubstitution([
                   FindPackageShare('ionic_demo'),
                      'worlds',
                      'ionic.sdf'
                ]),
                'panda_x': '4.3',
                'panda_y': '0.3',
                'panda_z': '1.2',
            }.items()
        ),
        Node(
            # Spawn a can for delivery
            package="ros_gz_sim",
            executable="create",
            output="log",
            arguments=[
                "-string", coke_can_string,
                "-x", "4.9",
                "-y", "0.37",
                "-z", "1.2",
            ],
            parameters=[{"use_sim_time": True}],
        ),
    ])

