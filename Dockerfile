# Based on https://github.com/j-rivero/ionic_testing/blob/main/Dockerfile
FROM ros:rolling
ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update \
    && apt-get install -y dirmngr curl git python3 python3-docopt python3-yaml python3-distro python3-pip sudo mesa-utils \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
RUN git clone https://github.com/gazebo-tooling/gzdev \
    && cd gzdev \
    && python3 gzdev.py repository enable osrf stable \
    && python3 gzdev.py repository enable osrf prerelease \
    && python3 gzdev.py repository enable osrf nightly
RUN apt-get install -y gz-ionic \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Also install libdart dependencies to avoid building dart vendor packages from source
RUN apt-get update \
    && apt-get install -y libdart6.13-collision-bullet-dev libdart6.13-collision-ode-dev libdart6.13-dev libdart6.13-external-ikfast-dev libdart6.13-external-odelcpsolver-dev libdart6.13-utils-urdf-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install nudged via pip (required by rmf_fleet_adapter_python)
RUN pip install nudged --break-system-packages

RUN mkdir -p /root/ws/src
WORKDIR /root/ws
COPY ionic_demo.repos .
RUN vcs import --input ionic_demo.repos src
RUN rosdep update
RUN apt-get update \
    && rosdep install --from-paths src --ignore-src -r --rosdistro rolling -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
RUN . /opt/ros/rolling/setup.sh \
      && MAKEFLAGS=-j6 GZ_RELAX_VERSION_MATCH=1 colcon build --symlink-install --packages-up-to ionic_demo --cmake-args -DNO_DOWNLOAD_MODELS=On
COPY entrypoint.sh /ionic_entrypoint.sh
ENTRYPOINT ["/ionic_entrypoint.sh"]
CMD ["bash"]
