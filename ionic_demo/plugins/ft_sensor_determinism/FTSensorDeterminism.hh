/*
 * Copyright (C) 2024 Open Source Robotics Foundation
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 *
 */

#ifndef EXAMPLE_PLUGIN_FTSENSORDETERMINISM_HH_
#define EXAMPLE_PLUGIN_FTSENSORDETERMINISM_HH_

#include <memory>
#include <mutex>
#include <optional>
#include <string>
#include <gz/transport/Node.hh>
#include <gz/sim/System.hh>

namespace ft_sensor_determinism
{
  // This plugin prints the number of elapsed simulation iterations,
  // this system's priority value from the XML configuration,
  // and a custom label from the XML configuration during the Update callback.
  class FTSensorDeterminism:
    public gz::sim::System,
    public gz::sim::ISystemConfigure,
    public gz::sim::ISystemUpdate
  {
    public: void Configure(const gz::sim::Entity &_entity,
                 const std::shared_ptr<const sdf::Element> &_sdf,
                 gz::sim::EntityComponentManager &_ecm,
                 gz::sim::EventManager &_eventMgr) override;

    public: void Update(const gz::sim::UpdateInfo &_info,
                        gz::sim::EntityComponentManager &_ecm) override;

    private: void OnWrench(const gz::msgs::Wrench &_msg);

    private: gz::sim::Sensor sensor{gz::sim::kNullEntity};
    private: bool subscribed{false};
    private: std::optional<gz::msgs::Wrench> wrenchFromECM;
    private: std::optional<gz::msgs::Wrench> wrenchFromTopic;
    private: std::mutex mutex;
    private: gz::transport::Node node;
  };
}
#endif
