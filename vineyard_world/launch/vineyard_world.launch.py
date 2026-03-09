import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, GroupAction, IncludeLaunchDescription
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution, PythonExpression
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():

    world_arg = DeclareLaunchArgument(
        'world',
        default_value='vineyard',
        description='world in gazebo classic'
    )

    world_path_arg = DeclareLaunchArgument(
        'world_path',
        default_value=PathJoinSubstitution([
            FindPackageShare('vineyard_world'), 'worlds', 
            PythonExpression(["'", LaunchConfiguration('world'), ".world'"])
        ]),
        description='world path in gazebo classic'
    )

    gui_arg = DeclareLaunchArgument(
        'gui',
        default_value='true',
        description='Set to true to enable gazebo gui'
    )

    world_path = LaunchConfiguration('world_path')
    gui = LaunchConfiguration('gui')

    gazebo_ignition_launch_group = GroupAction(
        actions=[
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    os.path.join(get_package_share_directory('ros_gz_sim'), 'launch', 'gz_sim.launch.py')
                ),
                launch_arguments={
                    'gz_args': [ '-r ', '-s ', world_path],
                    'on_exit_shutdown': 'true'
                }.items(),
            ),
            
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    os.path.join(get_package_share_directory('ros_gz_sim'), 'launch', 'gz_sim.launch.py')
                ),
                launch_arguments={
                    'gz_args': '-g ',
                    'on_exit_shutdown': 'true'
                }.items(),
                condition=IfCondition(PythonExpression(["'", gui, "'.lower() in ('true', '1', 'yes', 'on')"])),
            ),

            Node(
                package="ros_gz_bridge",
                executable="parameter_bridge",
                name="gz_clock_bridge",
                output="screen",
                arguments=["/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock"],
            )
        ]
    )

    ld = LaunchDescription()
    ld.add_action(world_arg)
    ld.add_action(world_path_arg)
    ld.add_action(gui_arg)
    ld.add_action(gazebo_ignition_launch_group)

    return ld