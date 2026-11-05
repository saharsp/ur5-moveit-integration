cmake_minimum_required(VERSION 3.8)
project(ur5_gazebo_sim)

find_package(ament_cmake REQUIRED)

install(
  DIRECTORY urdf config launch
  DESTINATION share/${PROJECT_NAME}
)

ament_package()
