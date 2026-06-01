import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, GroupAction, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PythonExpression
from launch_ros.actions import Node


def generate_launch_description():
    pkg_share = get_package_share_directory("industrial_zone_world")
    gz_sim_share = get_package_share_directory("ros_gz_sim")

    default_world = os.path.join(pkg_share, "worlds", "industrial_zone.world")

    gui_arg = DeclareLaunchArgument(
        "gui", default_value="true", description="Launch Gazebo GUI"
    )
    world_arg = DeclareLaunchArgument(
        "world_path",
        default_value=default_world,
        description="Path to the .world file",
    )

    world_path = LaunchConfiguration("world_path")
    gui = LaunchConfiguration("gui")

    gazebo_group = GroupAction(
        actions=[
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    os.path.join(gz_sim_share, "launch", "gz_sim.launch.py")
                ),
                launch_arguments={
                    "gz_args": ["-r ", "-s ", world_path],
                    "on_exit_shutdown": "true",
                }.items(),
            ),
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    os.path.join(gz_sim_share, "launch", "gz_sim.launch.py")
                ),
                launch_arguments={
                    "gz_args": ["-g "],
                    "on_exit_shutdown": "true",
                }.items(),
                condition=IfCondition(
                    PythonExpression(
                        ["'", gui, "'.strip().lower() in ('true','1','yes','on')"]
                    )
                ),
            ),
            Node(
                package="ros_gz_bridge",
                executable="parameter_bridge",
                name="gz_clock_bridge",
                output="screen",
                arguments=["/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock"],
            ),
        ]
    )

    return LaunchDescription([gui_arg, world_arg, gazebo_group])
