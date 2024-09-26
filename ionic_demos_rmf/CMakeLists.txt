cmake_minimum_required(VERSION 3.8)
project(ionic_demos_rmf)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(moveit_ros_planning_interface REQUIRED)
find_package(rmf_dispenser_msgs REQUIRED)
find_package(gz_sim_vendor REQUIRED)
find_package(gz-sim REQUIRED)

ament_environment_hooks("${CMAKE_CURRENT_SOURCE_DIR}/hooks/${PROJECT_NAME}.dsv.in")

add_executable(moveit_dispenser src/moveit_dispenser.cpp)
# add_library(moveit_dispenser SHARED src/moveit_dispenser.cpp)
target_link_libraries(moveit_dispenser
  gz-sim::core
)

ament_target_dependencies(moveit_dispenser
    rclcpp
    geometry_msgs
    rmf_dispenser_msgs
    moveit_ros_planning_interface
)

install(TARGETS
    moveit_dispenser
    DESTINATION lib/${PROJECT_NAME}
)
# uncomment the following section in order to fill in
# further dependencies manually.
# find_package(<dependency> REQUIRED)

ament_package()
