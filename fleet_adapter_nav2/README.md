# fleet_adapter_nav2

Set up workspace

```
git clone https://github.com/open-rmf/rmf

mkdir -p ws/src
vcs import ws/src < rmf/rmf.repos

cd ws/src
git clone https://github.com/gazebosim/ionic_demo

# rosdep
# build
```

Run basic tb4 bringup, and set initial posititon

```
ros2 launch ionic_demo ionic_navigation_demo_launch.py
```

Start `rmf_demos` common packages

```
cd ws
ros2 launch rmf_demos common.launch.xml headless:=1 use_sim_time:=true config_file:=src/ionic_demo/ionic_demo_building_maps/maps/ionic_demo/ionic_demo.building.yaml
```

Start `fleet_adapter_nav2`

```
ros2 run fleet_adapter_nav2 fleet_adapter -c src/ionic_demo/fleet_adapter_nav2/config/tb4_config.yaml -n install/ionic_demo_building_maps/share/ionic_demo_building_maps/maps/ionic_demo/nav_graphs/0.yaml -sim --ros-args -r /tf:=/tb4/tf
```

Send a task

```
ros2 run rmf_demos_tasks dispatch_patrol -p table_1 -n 1 -st 0 --use_sim_time
```

Send a delivery task

```
ros2 run rmf_demos_tasks dispatch_delivery -p bar -ph moveit_dispenser -d table_4 -dh coke_ingestor --use_sim_time
```
