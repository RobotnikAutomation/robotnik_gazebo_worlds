import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import GroupAction, IncludeLaunchDescription, SetEnvironmentVariable
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PythonExpression
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from robotnik_common.launch import AddArgumentParser, ExtendedArgument


def generate_launch_description():
    ld = LaunchDescription()
    add_to_launcher = AddArgumentParser(ld)
    world = LaunchConfiguration("world")
    package_share = get_package_share_directory("agentic_ai_demo")
    package_models = os.path.join(package_share, "models")

    add_to_launcher.add_arg(
        ExtendedArgument(
            name="world",
            description="World name in Gazebo Harmonic",
            default_value="agentic_ai_demo",
        )
    )

    add_to_launcher.add_arg(
        ExtendedArgument(
            name="world_path",
            description="World path in Gazebo Harmonic",
            default_value=[FindPackageShare("agentic_ai_demo"), "/worlds/", world, ".world"],  # type: ignore
        )
    )

    add_to_launcher.add_arg(
        ExtendedArgument(
            name="gui",
            description="Set to true to enable Gazebo GUI",
            default_value="true",
        )
    )

    params = add_to_launcher.process_arg()
    ros_gz_sim_launch = os.path.join(
        get_package_share_directory("ros_gz_sim"),
        "launch",
        "gz_sim.launch.py",
    )
    resource_paths = [package_models, package_share]
    gz_sim_resource_path = os.pathsep.join(
        resource_paths + [os.environ["GZ_SIM_RESOURCE_PATH"]]
    ) if os.environ.get("GZ_SIM_RESOURCE_PATH") else os.pathsep.join(resource_paths)
    ign_gazebo_resource_path = os.pathsep.join(
        resource_paths + [os.environ["IGN_GAZEBO_RESOURCE_PATH"]]
    ) if os.environ.get("IGN_GAZEBO_RESOURCE_PATH") else os.pathsep.join(resource_paths)
    gazebo_resource_path = os.pathsep.join(
        resource_paths + [os.environ["GAZEBO_RESOURCE_PATH"]]
    ) if os.environ.get("GAZEBO_RESOURCE_PATH") else os.pathsep.join(resource_paths)

    gazebo_launch_group = GroupAction(
        actions=[
            SetEnvironmentVariable(
                name="GZ_SIM_RESOURCE_PATH",
                value=gz_sim_resource_path,
            ),
            SetEnvironmentVariable(
                name="IGN_GAZEBO_RESOURCE_PATH",
                value=ign_gazebo_resource_path,
            ),
            SetEnvironmentVariable(
                name="GAZEBO_RESOURCE_PATH",
                value=gazebo_resource_path,
            ),
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(ros_gz_sim_launch),
                launch_arguments={
                    "gz_args": ["-r ", "-s ", params["world_path"]],
                    "on_exit_shutdown": "true",
                }.items(),
            ),
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(ros_gz_sim_launch),
                launch_arguments={
                    "gz_args": ["-g "],
                    "on_exit_shutdown": "true",
                }.items(),
                condition=IfCondition(
                    PythonExpression(
                        ["'", params["gui"], "'.strip().lower() in ('true','1','yes','on')"]
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

    ld.add_action(gazebo_launch_group)
    return ld
