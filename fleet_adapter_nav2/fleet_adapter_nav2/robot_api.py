# Copyright 2024 Open Source Robotics Foundation, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import enum
import time
import threading

import rclpy
from tf2_ros import TransformException
from tf2_ros.buffer import Buffer as TransformBuffer
from tf2_ros.transform_listener import TransformListener
import tf_transformations
from geometry_msgs.msg import PoseStamped
from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult


class RobotAPIResult(enum.IntEnum):
    SUCCESS = 0
    """The request was successful"""

    RETRY = 1
    """The client failed to connect but might succeed if you try again"""

    IMPOSSIBLE = 2
    """The client connected but something about the request is impossible"""


class RobotUpdateData:
    def __init__(self, data):
        self.robot_name = data['robot_name']
        position = data['position']
        x = position['x']
        y = position['y']
        yaw = position['yaw']
        self.position = [x, y, yaw]
        self.map = data['map_name']
        self.battery_soc = data['battery'] / 100.0
        self.requires_replan = data.get('replan', False)
        self.last_request_completed = data['last_request_completed']

    def is_command_completed(self, cmd_id):
        return self.last_request_completed == cmd_id


class RobotAPI:
    def __init__(self, robots, map_conversion, node):
        self.node = node
        self.robots = robots
        self.maps = map_conversion

        # Initialize nav2 navigator node
        #TODO(@xiyuoh) Enable handling multiple robots and nav2 nodes
        self.navigator = BasicNavigator('nav2_simple_commander_node', namespace='/tb4')
        self.robot_name = 'tb4'

        self.prefix = robots[self.robot_name]["prefix"]
        self.timeout = 5.0
        self.debug = False

        # TODO(AC): Populate these fields properly via ROS 2 subscriptions and
        # nav2 simple commander API feedback
        self.battery_soc = 100 - 1e-9
        self.ongoing_request_cmd_id = None
        self.last_request_completed = None

        # We need the fleet adapter node to create the transform listener
        # instead of using the navigator node as the navigator node only
        # activates after we set the initial pose of the robot, which we'd
        # need the TF info to do.
        self.tf_buffer = TransformBuffer()
        tf_listener = TransformListener(self.tf_buffer, node)
        tf_listener # Avoid unused variable warning

        self.position = None
        def _tf_listener():
            transform_stamped = None
            try:
                transform_stamped = self.tf_buffer.lookup_transform(
                    self.robots[self.robot_name]["target_frame"],
                    self.robots[self.robot_name]["from_frame"],
                    rclpy.time.Time())
            except TransformException as ex:
                self.node.get_logger().info(
                    f'Could not transform base_footprint to map: {ex}')
                return None

            theta = tf_transformations.euler_from_quaternion([
                transform_stamped.transform.rotation.x,
                transform_stamped.transform.rotation.y,
                transform_stamped.transform.rotation.z,
                transform_stamped.transform.rotation.w
            ])[2]
            self.position = {
                "x": transform_stamped.transform.translation.x,
                "y": transform_stamped.transform.translation.y,
                "yaw": theta,
            }

        timer = node.create_timer(1.0, _tf_listener)
        timer # Avoid unused variable warning

        tf_thread = threading.Thread(target=self.activate_navigator, args=())
        tf_thread.start()

    def activate_navigator(self):
        while self.get_data(self.robot_name) is None:
            self.node.get_logger().info(
                f'Unable to retrieve robot data!'
            )
            time.sleep(1)

        self.node.get_logger().info(
            f'Successfully retrieved robot data!'
        )

        # Set initial pose of robot
        robot_data = self.get_data(self.robot_name)
        initial_pose = PoseStamped()
        initial_pose.header.frame_id = 'map'
        initial_pose.header.stamp = self.navigator.get_clock().now().to_msg()
        initial_pose.pose.position.x = robot_data.position[0]
        initial_pose.pose.position.y = robot_data.position[1]
        initial_pose.pose.orientation.w = robot_data.position[2]
        initial_pose.pose.orientation.z = 0.0
        self.navigator.setInitialPose(initial_pose)

        self.navigator.waitUntilNav2Active()

    def navigate(
        self,
        robot_name: str,
        cmd_id: int,
        pose,
        map_name: str,
        speed_limit=0.0,
    ):
        if robot_name not in self.robots:
            self.navigator.get_logger().info(
                f'Robot [{robot_name}] not registered in fleet, ignoring...'
            )
            return
        assert len(pose) > 2

        goal_pose = PoseStamped()
        goal_pose.header.frame_id = self.maps[map_name]
        goal_pose.header.stamp = self.navigator.get_clock().now().to_msg()
        goal_pose.pose.position.x = pose[0]
        goal_pose.pose.position.y = pose[1]
        goal_pose.pose.orientation.w = pose[2]
        goal_pose.pose.orientation.z = 0.0

        self.navigator.goToPose(goal_pose)
        self.ongoing_request_cmd_id = cmd_id

        return True

    def start_activity(
        self, robot_name: str, cmd_id: int, activity: str, label: str
    ):
        #TODO(@xiyuoh) implement custom actions if any
        return RobotAPIResult.RETRY

    def stop(self, robot_name: str, cmd_id: int):
        if robot_name not in self.robots:
            self.navigator.get_logger().info(
                f'Robot [{robot_name}] not registered in fleet, ignoring...'
            )
            return
        if self.ongoing_request_cmd_id is None:
            return True
        if self.ongoing_request_cmd_id == cmd_id:
            self.navigator.cancelTask()
            return True
        return False

    def get_data(self, robot_name: str | None = None):
        if robot_name not in self.robots:
            self.node.get_logger().info(
                f'Robot [{robot_name}] not registered in fleet, ignoring...'
            )
            return None

        if self.position is None:
            self.node.get_logger().info(
                f'No position found!'
            )
            return

        if self.ongoing_request_cmd_id is not None and \
                self.navigator.isTaskComplete():
            self.node.get_logger().info(
                f'Robot [{robot_name}] completed task with cmd id '
                f'[{self.ongoing_request_cmd_id}]'
            )
            self.last_request_completed = self.ongoing_request_cmd_id
            self.ongoing_request_cmd_id = None

        data = {
            "robot_name": robot_name,
            "position": self.position,
            "map_name": self.robots[robot_name]['map'],
            "battery": self.battery_soc,
            "last_request_completed": self.last_request_completed
        }
        return RobotUpdateData(data)
