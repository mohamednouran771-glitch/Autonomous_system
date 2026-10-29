from pathlib import Path
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.actions import SetEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command
from launch_ros.actions import Node


def generate_launch_description():
	description_share = Path(
			get_package_share_directory('autonomous_description')
	)
	bringup_share = Path(
			get_package_share_directory('autonomous_bringup')
	)
	gazebo_share = Path(get_package_share_directory('ros_gz_sim'))
	model_file = description_share / 'urdf' / 'shellcarlaunch.urdf.xacro'
	rviz_file = description_share / 'rviz' / 'urdf.rviz'
	world_file = description_share / 'worlds' / 'world.sdf'
	bridge_config = bringup_share / 'config' / 'gazebo.yaml'
	resource_path = os.pathsep.join([
		str(description_share.parent),
		os.environ.get('GZ_SIM_RESOURCE_PATH', ''),
	])

	robot_description = {
		'robot_description': Command(['xacro ', str(model_file)])
	}

	gazebo = IncludeLaunchDescription(
		PythonLaunchDescriptionSource(
			str(gazebo_share / 'launch' / 'gz_sim.launch.py')
			
		),
		launch_arguments={'gz_args': f'-r {world_file}'}.items(),
	)

	robot_state_publisher = Node(
		package='robot_state_publisher',
		executable='robot_state_publisher',
		parameters=[robot_description],
		output='screen',
	)

	spawn_robot = Node(
		package='ros_gz_sim',
		executable='create',
		arguments=[
			'-topic', 'robot_description',
			'-name', 'shell_car',
			'-z', '0.1',
		],
		output='screen',
	)

	ros_gz_bridge = Node(
		package='ros_gz_bridge',
		executable='parameter_bridge',
		parameters=[{'config_file': str(bridge_config)}],
		output='screen',
	)

	rviz = Node(
		package='rviz2',
		executable='rviz2',
		arguments=['-d', str(rviz_file)],
		output='screen',
	)

	return LaunchDescription([
		SetEnvironmentVariable('GZ_SIM_RESOURCE_PATH', resource_path),
		robot_state_publisher,
		ros_gz_bridge,
		spawn_robot,
		rviz,
		gazebo,
	])
