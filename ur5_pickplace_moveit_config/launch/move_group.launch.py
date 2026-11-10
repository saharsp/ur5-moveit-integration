from launch import LaunchDescription
from launch.actions import GroupAction
from launch_ros.actions import SetParameter
from moveit_configs_utils import MoveItConfigsBuilder
from moveit_configs_utils.launches import generate_move_group_launch


def generate_launch_description():
    moveit_config = MoveItConfigsBuilder(
        "ur5", package_name="ur5_pickplace_moveit_config"
    ).to_moveit_configs()

    # generate_move_group_launch() builds its own LaunchDescription containing
    # the move_group Node, with no way to inject extra parameters directly.
    # move_group was defaulting to wall-clock time while Gazebo's joint_states
    # are stamped with simulation time, so move_group's staleness check always
    # thought the robot state was ancient and failed execution with
    # CONTROL_FAILED. Wrapping its entities in a GroupAction with
    # SetParameter("use_sim_time", True) applies that parameter to every node
    # inside it without needing to modify moveit_configs_utils itself.
    move_group_launch = generate_move_group_launch(moveit_config)

    return LaunchDescription(
        [
            GroupAction(
                actions=[
                    SetParameter(name="use_sim_time", value=True),
                    *move_group_launch.entities,
                ]
            )
        ]
    )
