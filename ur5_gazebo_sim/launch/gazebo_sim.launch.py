from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    pkg_share = FindPackageShare('ur5_gazebo_sim')

    xacro_file = PathJoinSubstitution([pkg_share, 'urdf', 'ur5_gazebo.urdf.xacro'])
    initial_positions_file = PathJoinSubstitution([pkg_share, 'config', 'initial_positions.yaml'])

    robot_description = {
        'robot_description': ParameterValue(
            Command([
                'xacro ', xacro_file,
                ' initial_positions_file:=', initial_positions_file,
            ]),
            value_type=str,
        )
    }

    gz_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([
                FindPackageShare('ros_gz_sim'), 'launch', 'gz_sim.launch.py'
            ])
        ),
        launch_arguments={'gz_args': '-r empty.sdf'}.items(),
    )

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[robot_description],
    )

    spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=['-topic', 'robot_description', '-name', 'ur5', '-z', '0.0'],
        output='screen',
    )

    clock_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=['/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock'],
        output='screen',
    )

    joint_state_broadcaster_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['joint_state_broadcaster'],
        output='screen',
    )

    ur5_arm_controller_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['ur5_arm_controller'],
        output='screen',
    )

    delayed_joint_state_broadcaster = TimerAction(period=5.0, actions=[joint_state_broadcaster_spawner])
    delayed_arm_controller = TimerAction(period=7.0, actions=[ur5_arm_controller_spawner])

    return LaunchDescription([
        gz_sim,
        robot_state_publisher,
        spawn_entity,
        clock_bridge,
        delayed_joint_state_broadcaster,
        delayed_arm_controller,
    ])
