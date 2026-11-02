#!/usr/bin/env python3
"""Plan and execute a single pose-goal move for the UR5 using MoveIt's
Python API (moveit_py) -- no RViz interaction needed."""

import os
import time

import rclpy
from rclpy.logging import get_logger
from geometry_msgs.msg import PoseStamped

from moveit_configs_utils import MoveItConfigsBuilder
from moveit.planning import MoveItPy


def main():
    rclpy.init()
    logger = get_logger("ur5_moveit_py_demo")

    moveit_config = (
        MoveItConfigsBuilder("ur5", package_name="ur5_pickplace_moveit_config")
        .planning_pipelines(pipelines=["ompl"])
        .to_moveit_configs()
        .to_dict()
    )
    # MoveItCpp (which moveit_py wraps) reads the pipeline list from the
    # nested 'planning_pipelines.pipeline_names' parameter, which
    # MoveItConfigsBuilder's to_dict() doesn't produce on its own (it only
    # emits the flat 'planning_pipelines' key that move_group's own loader
    # expects).
    moveit_config["planning_pipelines"] = {"pipeline_names": ["ompl"]}
    moveit_config["plan_request_params"] = {
    "planning_pipeline": "ompl",
    "planner_id": "RRTConnectkConfigDefault",
    "planning_time": 5.0,
    "planning_attempts": 10,
    "max_velocity_scaling_factor": 0.1,
    "max_acceleration_scaling_factor": 0.1,
    }
    
    import yaml
    with open("/tmp/moveit_py_config_dump.yaml", "w") as f:
        yaml.safe_dump(moveit_config, f)
    logger.info(f"planning_pipelines value: {moveit_config.get('planning_pipelines')}")


    ur5 = MoveItPy(node_name="ur5_moveit_py_demo", config_dict=moveit_config)
    arm = ur5.get_planning_component("ur5_arm")

    logger.info("Setting start state to current state")
    
    def plan_and_execute_to(ur5, arm, logger, x, y, z):
        arm.set_start_state_to_current_state()
        goal_pose = PoseStamped()
        goal_pose.header.frame_id = "base_link"
        goal_pose.pose.orientation.w = 1.0
        goal_pose.pose.position.x = x
        goal_pose.pose.position.y = y
        goal_pose.pose.position.z = z
        arm.set_goal_state(pose_stamped_msg=goal_pose, pose_link="tool0")

        plan_result = arm.plan()
        if not plan_result:
            logger.error(f"Planning failed for ({x}, {y}, {z})")
            return None

        trajectory = plan_result.trajectory
        ur5.execute(trajectory, controllers=[])
        time.sleep(1.0)
        return trajectory.get_robot_trajectory_msg()
 

    traj_msg = plan_and_execute_to(ur5, arm, logger, 0.4, 0.1, 0.3)
    if traj_msg:
        for i, point in enumerate(traj_msg.joint_trajectory.points):
            logger.info(f"Waypoint {i}: {list(point.positions)}")
            
    logger.info("Done.")
    os._exit(0)

if __name__ == "__main__":
    main()
