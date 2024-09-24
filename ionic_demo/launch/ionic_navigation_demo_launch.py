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

from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    ExecuteProcess,
    IncludeLaunchDescription,
)
from launch.conditions import UnlessCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    bringup_dir = Path(get_package_share_directory('nav2_bringup'))
    ionic_demo_dir = Path(get_package_share_directory('ionic_demo'))
    launch_dir = bringup_dir / 'launch'
    headless = LaunchConfiguration('headless')
    declare_headless_cmd = DeclareLaunchArgument(
        'headless', default_value='True', description='Whether to execute gzclient)'
    )

    return LaunchDescription(
        [
            declare_headless_cmd,
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    str(ionic_demo_dir / 'launch' / 'tb4_spawn_launch.py')
                ),
            ),
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    str(ionic_demo_dir / 'launch' / 'world_launch.py')
                ),
            ),
            ExecuteProcess(
                cmd=['gz', 'sim', '-g', '-v4'],
                output='screen',
                condition=UnlessCondition(headless),
            ),
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(str(launch_dir / 'rviz_launch.py')),
                launch_arguments={
                    'use_sim_time': 'True',
                    'rviz_config': str(ionic_demo_dir / 'configs' / 'nav2.rviz'),
                }.items(),
            ),
        ]
    )
