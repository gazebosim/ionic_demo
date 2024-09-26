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

from ament_index_python.packages import get_package_share_directory
from launch_ros.actions import Node

from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    ExecuteProcess,
    IncludeLaunchDescription,
)
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_xml.launch_description_sources import XMLLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    launch_dir = Path(get_package_share_directory('ionic_demo')) / 'launch'
    run_gazebo = LaunchConfiguration('run_gazebo')
    declare_headless_cmd = DeclareLaunchArgument(
        'run_gazebo', default_value='True', description='Whether to run gazebo'
    )

    return LaunchDescription(
        [
            declare_headless_cmd,
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    str(launch_dir / 'world_launch.py')
                ),
                condition=IfCondition(run_gazebo),
            ),
            ExecuteProcess(
                cmd=['gz', 'sim', '-g', '-v4'],
                output='screen',
                condition=IfCondition(run_gazebo),
            ),
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    str(launch_dir / 'tb4_spawn_launch.py')
                ),
            ),
        ]
    )
