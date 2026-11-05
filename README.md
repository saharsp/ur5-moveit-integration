# UR5 MoveIt + Gazebo Integration

Portfolio project extending a custom 6-DOF UR5-style manipulator (originally
developed with a DH-parameter-based inverse kinematics solver in
`robot_ik_pickplace`) with full MoveIt2 motion planning and Gazebo physics
simulation on ROS2 Jazzy.

This repository is intentionally kept separate from `robot_ik_pickplace` and
does not modify it — it is a self-contained MoveIt + Gazebo integration layer
built on top of the same robot description.

## Repository layout

This is a plain source folder (no top-level `package.xml`) containing three
independent ROS2 packages, each buildable with
`colcon build --packages-select <name>`:

- **ur5_pickplace_moveit_config/** — MoveIt2 configuration generated via
  MoveIt Setup Assistant: SRDF, kinematics, planning pipeline (OMPL),
  controller config, and a MoveIt-only duplicate of the robot URDF with
  slimmed collision geometry (see "Why two collision geometries?" below).
- **ur5_moveit_py_demo/** — A Python node (`plan_and_execute.py`) using
  MoveIt's Python API (`moveit_py`) to plan and execute a single Cartesian
  pose-goal move, with automatic retry on transient planning failures.
- **ur5_gazebo_sim/** — Gazebo Harmonic simulation package: a physics-ready
  duplicate of the robot URDF (inertials, a fixed world anchor, joint
  damping), `ros2_control` wiring to the `gz_ros2_control` hardware
  interface, controller configuration, and a launch file that brings up
  Gazebo with the robot spawned and controllers active.

## Prerequisites

- ROS2 Jazzy Jalisco (Ubuntu 24.04)
- MoveIt2
- Gazebo Harmonic (`gz-sim8`) with `ros_gz` and `gz_ros2_control` (bundled
  with a standard ROS2 Jazzy + Gazebo Harmonic desktop install)
- The sibling `robot_ik_pickplace` package (provides the base robot URDF
  these packages build on)

## Build

```bash
cd ~/ros2_ws
colcon build --packages-select ur5_pickplace_moveit_config ur5_moveit_py_demo ur5_gazebo_sim
source install/setup.bash
```

## Usage

### Option A — Simulate in Gazebo and plan/execute with MoveIt (recommended)

1. Launch Gazebo with the robot spawned and controllers active:

   ```bash
   ros2 launch ur5_gazebo_sim gazebo_sim.launch.py
   ```

   Wait for the log to show both `joint_state_broadcaster` and
   `ur5_arm_controller` as "Configured and activated".

2. In a second terminal, run the MoveIt planning/execution demo:

   ```bash
   source ~/ros2_ws/install/setup.bash
   ros2 run ur5_moveit_py_demo plan_and_execute --ros-args -p use_sim_time:=true
   ```

   This plans a collision-aware Cartesian move (default target hardcoded in
   `plan_and_execute.py`) and executes it against the live Gazebo
   simulation. The `use_sim_time:=true` flag is required so the planning
   node's own clock matches Gazebo's simulated clock.

### Option B — Mock hardware only (no physics simulation)

For quick planning tests without Gazebo, launch the MoveIt demo against
`mock_components/GenericSystem` instead — see `ur5_pickplace_moveit_config`'s
own demo launch file for the mock-hardware bring-up.

## Why two collision geometries?

`ur5_pickplace_moveit_config/urdf/ur5_moveit.urdf` is a MoveIt-only
duplicate of the robot with narrower `<collision>` cylinders than the
original/Gazebo URDFs. The original collision geometry was thick enough
relative to link lengths that MoveIt's self-collision checker flagged false
positives at many reachable, physically valid arm configurations. Slimming
the MoveIt-only collision geometry (while leaving the original and the
Gazebo physics URDF untouched) fixed this without affecting physical
simulation accuracy or the original IK package.

## Known configuration notes / gotchas

- **`position_proportional_gain`**: `gz_ros2_control`'s `GazeboSimSystem`
  converts `position` command interfaces into joint torque via an internal
  P-controller. This must be set explicitly per `<hardware>` block in
  `ur5_gazebo_sim/config/ur5_gazebo.ros2_control.xacro` (currently
  `1000.0`) — the plugin's own default (`0.1`) is far too weak to move the
  simulated arm, even though the controller will falsely report successful
  execution.
- **`use_sim_time`**: `MoveItPy` initializes its own internal rclcpp node
  separate from the one created by your script's `--ros-args`. Passing
  `use_sim_time:=true` on the command line is not sufficient on its own —
  it must also be set in the `moveit_config` dict passed into
  `MoveItPy(...)` (see `plan_and_execute.py`), otherwise trajectory
  execution will abort due to a wall-clock vs. sim-clock mismatch.
- **Planning retries**: OMPL's RRTConnect is randomized;
  `plan_and_execute_to` retries planning up to 5 times before giving up,
  since an occasional random seed can produce a path that clips a
  self-collision during post-processing simplification even with slimmed
  collision geometry.
- **Stale processes**: If Gazebo or `ros2 launch` was closed uncleanly
  (e.g. VM suspend/resume), leftover background processes can cause
  "Controller already loaded" errors on the next launch. Clean up with:
  ```bash
  pkill -9 -f "ros2 launch"; pkill -9 -f "gz sim"; pkill -9 -f controller_manager; pkill -9 -f robot_state_publisher; pkill -9 -f parameter_bridge; pkill -9 -f spawner
  ros2 daemon stop && ros2 daemon start
  ```

## Joint limits

All six joints are `revolute` with `±6.2831853 rad` (±360°) position
limits, `50 N·m` effort limit, and `3.1415927 rad/s` (180°/s) velocity
limit.

## Author

Sahar Samanipour — built as a portfolio project translating industrial
ABB/KUKA robotics experience into ROS2/MoveIt2.
