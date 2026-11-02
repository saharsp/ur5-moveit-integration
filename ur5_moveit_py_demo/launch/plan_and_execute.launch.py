from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    moveit_py_node = Node(
        package="ur5_moveit_py_demo",
        executable="plan_and_execute",
        output="screen",
    )
    return LaunchDescription([moveit_py_node])
