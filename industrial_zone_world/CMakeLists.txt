cmake_minimum_required(VERSION 3.8)
project(industrial_zone_world)

find_package(ament_cmake REQUIRED)

ament_environment_hooks("${CMAKE_CURRENT_SOURCE_DIR}/hooks/${PROJECT_NAME}.dsv.in")

install(
  DIRECTORY launch worlds models
  DESTINATION share/${PROJECT_NAME}/
)

ament_package()
