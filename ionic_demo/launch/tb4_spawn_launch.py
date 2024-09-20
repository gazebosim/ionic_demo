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

import xacro
from ament_index_python.packages import get_package_share_directory
from launch_ros.actions import Node
from ros_gz_bridge.actions import RosGzBridge

from launch import LaunchDescription
from launch.actions import (
    AppendEnvironmentVariable,
    IncludeLaunchDescription,
)
from launch.launch_description_sources import PythonLaunchDescriptionSource


def generate_launch_description():
    # Get the launch directory
    ionic_demo_dir = Path(get_package_share_directory('ionic_demo'))
    bringup_dir = Path(get_package_share_directory('nav2_bringup'))
    launch_dir = bringup_dir / 'launch'
    map_yaml_file = str(ionic_demo_dir / 'maps' / 'ionic_demo.yaml')

    bringup_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(str(launch_dir / 'bringup_launch.py')),
        launch_arguments={
            'map': map_yaml_file,
            'use_sim_time': 'True',
            'use_composition': 'True',
        }.items(),
    )
    # This checks that tb4 exists needed for the URDF / simulation files.
    # If not using TB4, its safe to remove.
    sim_dir = Path(get_package_share_directory('nav2_minimal_tb4_sim'))
    desc_dir = Path(get_package_share_directory('nav2_minimal_tb4_description'))

    # Launch configuration variables specific to simulation
    robot_name = 'ionic_tb4'
    robot_sdf = xacro.process(desc_dir / 'urdf' / 'standard' / 'turtlebot4.urdf.xacro')

    remappings = [('/tf', 'tf'), ('/tf_static', 'tf_static')]

    start_robot_state_publisher_cmd = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[
            {
                'use_sim_time': True,
                'robot_description': robot_sdf
            }
        ],
        remappings=remappings,
    )

    bridge = RosGzBridge(
        bridge_name='tb4_bridge',
        config_file=str(sim_dir / 'configs' / 'tb4_bridge.yaml'),
        use_composition='True',
    )
    camera_bridge = RosGzBridge(
        bridge_name='tb4_camera_bridge',
        config_file=str(ionic_demo_dir / 'configs' / 'tb4_camera_bridge.yaml'),
        use_composition='True',
    )

    spawn_model = Node(
        package='ros_gz_sim',
        executable='create',
        output='screen',
        parameters=[
            {
                'entity': robot_name,
                'string': robot_sdf,
            }
        ],
    )

    set_env_vars_resources = AppendEnvironmentVariable(
        'GZ_SIM_RESOURCE_PATH', str(desc_dir.parent.resolve())
    )

    # Create the launch description and populate
    ld = LaunchDescription()

    ld.add_action(bridge)
    ld.add_action(camera_bridge)

    # The meshes used for the turtlebot4 visuals seem to be complex and cause
    # a drop in RTF on non-GPU machines.
    # Comment this to let gazebo to fail to find the mesh files
    ld.add_action(set_env_vars_resources)

    ld.add_action(spawn_model)

    # Add the actions to launch all of the navigation nodes
    ld.add_action(start_robot_state_publisher_cmd)
    ld.add_action(bringup_cmd)

    return ld
