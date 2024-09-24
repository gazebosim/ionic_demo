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

// We'll use a string and the gzmsg command below for a brief example.
// Remove these includes if your plugin doesn't need them.
#include <memory>
#include <string>
#include <gz/common/Console.hh>

#include <gz/msgs/convert/StdTypes.hh>

// This header is required to register plugins. It's good practice to place it
// in the cc file, like it's done here.
#include <gz/plugin/Register.hh>

#include <gz/sensors/ForceTorqueSensor.hh>
#include "gz/sim/components/WrenchMeasured.hh"
#include <gz/sim/Sensor.hh>

// Don't forget to include the plugin's header.
#include "FTSensorDeterminism.hh"

// This is required to register the plugin. Make sure the interfaces match
// what's in the header.
GZ_ADD_PLUGIN(
    ft_sensor_determinism::FTSensorDeterminism,
    gz::sim::System,
    ft_sensor_determinism::FTSensorDeterminism::ISystemConfigure,
    ft_sensor_determinism::FTSensorDeterminism::ISystemUpdate)

using namespace ft_sensor_determinism;

//////////////////////////////////////////////////
void FTSensorDeterminism::Configure(
        const gz::sim::Entity &_entity,
        const std::shared_ptr<const sdf::Element> &_sdf,
        gz::sim::EntityComponentManager &_ecm,
        gz::sim::EventManager &_eventMgr)
{
  this->sensor = gz::sim::Sensor(_entity);
  if (!this->sensor.Valid(_ecm))
  {
    gzerr << "This plugin should be attached to a sensor.\n";
    return;
  }

  // Create WrenchMeasured component for sensor Entity
  _ecm.CreateComponent(_entity, gz::sim::components::WrenchMeasured());

}

//////////////////////////////////////////////////
void FTSensorDeterminism::OnWrench(const gz::msgs::Wrench &_msg)
{
  std::lock_guard<std::mutex> lock(this->mutex);
  this->wrenchFromTopic = _msg;
}

//////////////////////////////////////////////////
double wrenchTimeStamp(const gz::msgs::Wrench &_msg)
{
  return std::chrono::duration<double>(
      gz::msgs::Convert(_msg.header().stamp())).count();
}

//////////////////////////////////////////////////
void FTSensorDeterminism::Update(const gz::sim::UpdateInfo &_info,
    gz::sim::EntityComponentManager &_ecm)
{
  double simTime = std::chrono::duration<double>(_info.simTime).count();

  auto wrenchComponent =
    _ecm.Component<gz::sim::components::WrenchMeasured>(this->sensor.Entity());
  if (!wrenchComponent)
  {
    return;
  }
  this->wrenchFromECM = wrenchComponent->Data();

  if (!subscribed)
  {
    auto topic = this->sensor.Topic(_ecm);
    if (topic)
    {
      this->node.Subscribe(*topic, &FTSensorDeterminism::OnWrench, this);
      this->subscribed = true;
    }
  }

  if (_info.paused)
  {
    return;
  }

  double wrenchTimeFromECM = wrenchTimeStamp(*this->wrenchFromECM);
  if (!gz::math::equal(simTime, wrenchTimeFromECM))
  {
    gzerr << "FT non-determinism in ECM data "
          << "THIS SHOULD NOT HAPPEN!!! "
          << "iteration " << _info.iterations
          << ", simTime " << simTime
          << ", wrenchFromECM time diff " << wrenchTimeFromECM - simTime
          << '\n';
  }

  std::lock_guard<std::mutex> lock(this->mutex);
  if (this->wrenchFromTopic)
  {
    double wrenchTimeFromTopic = wrenchTimeStamp(*this->wrenchFromTopic);
    if (!gz::math::equal(simTime, wrenchTimeFromTopic))
    {
      gzerr << "FT non-determinism in gz-transport data "
            << "iteration " << _info.iterations
            << ", simTime " << simTime
            << ", wrenchFromTopic time diff " << wrenchTimeFromTopic - simTime
            << '\n';
    }
  }
}
