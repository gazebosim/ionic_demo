cmake_minimum_required(VERSION 3.22.1 FATAL_ERROR)

find_package(gz-cmake4 REQUIRED)

project(ft_sensor_determinism)

gz_find_package(gz-plugin3 REQUIRED COMPONENTS register)
set(GZ_PLUGIN_VER ${gz-plugin3_VERSION_MAJOR})

gz_find_package(gz-sensors9 REQUIRED)
set(GZ_SENSORS_VER ${gz-sensors9_VERSION_MAJOR})

gz_find_package(gz-sim9 REQUIRED)
set(GZ_SIM_VER ${gz-sim9_VERSION_MAJOR})

add_library(FTSensorDeterminism SHARED FTSensorDeterminism.cc)
set_property(TARGET FTSensorDeterminism PROPERTY CXX_STANDARD 17)
target_link_libraries(FTSensorDeterminism
  PRIVATE gz-plugin${GZ_PLUGIN_VER}::gz-plugin${GZ_PLUGIN_VER}
  PRIVATE gz-sensors${GZ_SENSORS_VER}::gz-sensors${GZ_SENSORS_VER}
  PRIVATE gz-sim${GZ_SIM_VER}::gz-sim${GZ_SIM_VER})
