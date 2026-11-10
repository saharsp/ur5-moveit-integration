from launch import LaunchDescription
from launch.actions import GroupAction
from launch_ros.actions import SetParameter
from moveit_configs_utils import MoveItConfigsBuilder
from moveit_configs_utils.launches import generate_moveit_rviz_launch


def generate_launch_description():
    moveit_config = MoveItConfigsBuilder(
        "ur5", package_name="ur5_pickplace_moveit_config"
    ).to_moveit_configs()

    # Same use_sim_time fix as move_group.launch.py, applied here too for
    # consistency so RViz's own clock/TF handling matches the simulation.
    rviz_launch = generate_moveit_rviz_launch(moveit_config)

    return LaunchDescription(
        [
            GroupAction(
                actions=[
                    SetParameter(name="use_sim_time", value=True),
                    *rviz_launch.entities,
                ]
            )
        ]
    )
