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
from ros_gz_sim.actions import GzServer

from launch import LaunchDescription


def generate_launch_description():
    ionic_demo_dir = Path(get_package_share_directory("ionic_demo"))
    world = str(ionic_demo_dir / "worlds" / "ionic.sdf")
    return LaunchDescription([GzServer(world_sdf_file=world, use_composition='True')])
