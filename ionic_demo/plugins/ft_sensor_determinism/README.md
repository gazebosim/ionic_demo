# Force-torque sensor determinism

The Force-torque wrench data can now be read directly from the ECM in
addition to subscribing to a gz-transport topic.
This example plugin can be attached to a force-torque sensor to compare the
determinism of data access via these two methods by printing a console error
message whenever old data is accessed.

## Build

From this folder, do the following to build the plugin:

~~~
mkdir build
cd build
cmake ..
make
~~~

This will generate the `FTSensorDeterminism` library under `build`.

## Run

A demo world is adapted from the
[mimic\_fast\_slow\_pendulums\_world.sdf](https://github.com/gazebosim/gz-sim/blob/gz-sim9/examples/worlds/mimic_fast_slow_pendulums_world.sdf)
example world added to demonstrate mimic constraints in Gazebo Harmonic.
A force-torque sensor with an instance of the `FTSensorDeterminism` plugin is
added to each joint in the world.

Before starting Gazebo, we must make sure it can find the plugin by doing:

~~~
cd ionic_demo/plugins/ft_sensor_determinism
export GZ_SIM_SYSTEM_PLUGIN_PATH=`pwd`/build
~~~

Then run the demo world:

    gz sim -v 3 ft_sensor_determinism.sdf -r

The data accessed via the ECM should never be out of date, but data from the
gz-transport topic may be outdated depending on the computing load on your
system. To add stress to the system, the `real_time_factor` SDFormat parameter
is set to `0` to maximize the update rate and the example command above opens
the GUI. To add additional stress, use the `stress` command with a `--cpu`
parameter equal to the number of CPU cores on your system, which should
increase the number of error messages printed about "FT non-determinism in
gz-transport data."

Example error messages:

~~~
(2024-09-24 01:24:10.347) [error] FT non-determinism in gz-transport data iteration 57818, simTime 57.818, wrenchFromTopic time diff -0.001
(2024-09-24 01:24:10.347) [error] FT non-determinism in gz-transport data iteration 57818, simTime 57.818, wrenchFromTopic time diff -0.001
(2024-09-24 01:24:10.347) [error] FT non-determinism in gz-transport data iteration 57818, simTime 57.818, wrenchFromTopic time diff -0.001
(2024-09-24 01:24:10.347) [error] FT non-determinism in gz-transport data iteration 57818, simTime 57.818, wrenchFromTopic time diff -0.001
(2024-09-24 01:24:10.347) [error] FT non-determinism in gz-transport data iteration 57818, simTime 57.818, wrenchFromTopic time diff -0.001
(2024-09-24 01:24:10.347) [error] FT non-determinism in gz-transport data iteration 57818, simTime 57.818, wrenchFromTopic time diff -0.001
(2024-09-24 01:24:10.367) [error] FT non-determinism in gz-transport data iteration 57860, simTime 57.86, wrenchFromTopic time diff -0.001
(2024-09-24 01:24:10.367) [error] FT non-determinism in gz-transport data iteration 57860, simTime 57.86, wrenchFromTopic time diff -0.001
(2024-09-24 01:24:10.367) [error] FT non-determinism in gz-transport data iteration 57860, simTime 57.86, wrenchFromTopic time diff -0.001
(2024-09-24 01:24:10.367) [error] FT non-determinism in gz-transport data iteration 57860, simTime 57.86, wrenchFromTopic time diff -0.001
(2024-09-24 01:24:10.500) [error] FT non-determinism in gz-transport data iteration 58140, simTime 58.14, wrenchFromTopic time diff -0.001
(2024-09-24 01:24:10.540) [error] FT non-determinism in gz-transport data iteration 58226, simTime 58.226, wrenchFromTopic time diff -0.001
(2024-09-24 01:24:10.540) [error] FT non-determinism in gz-transport data iteration 58226, simTime 58.226, wrenchFromTopic time diff -0.001
(2024-09-24 01:24:10.540) [error] FT non-determinism in gz-transport data iteration 58226, simTime 58.226, wrenchFromTopic time diff -0.001
(2024-09-24 01:24:10.752) [error] FT non-determinism in gz-transport data iteration 58668, simTime 58.668, wrenchFromTopic time diff -0.001
(2024-09-24 01:24:10.752) [error] FT non-determinism in gz-transport data iteration 58668, simTime 58.668, wrenchFromTopic time diff -0.001
(2024-09-24 01:24:10.752) [error] FT non-determinism in gz-transport data iteration 58668, simTime 58.668, wrenchFromTopic time diff -0.001
(2024-09-24 01:24:11.063) [error] FT non-determinism in gz-transport data iteration 59334, simTime 59.334, wrenchFromTopic time diff -0.001
(2024-09-24 01:24:11.078) [error] FT non-determinism in gz-transport data iteration 59363, simTime 59.363, wrenchFromTopic time diff -0.001
(2024-09-24 01:24:11.111) [error] FT non-determinism in gz-transport data iteration 59427, simTime 59.427, wrenchFromTopic time diff -0.001
(2024-09-24 01:24:11.344) [error] FT non-determinism in gz-transport data iteration 59892, simTime 59.892, wrenchFromTopic time diff -0.001
(2024-09-24 01:24:11.533) [error] FT non-determinism in gz-transport data iteration 60283, simTime 60.283, wrenchFromTopic time diff -0.001
~~~
