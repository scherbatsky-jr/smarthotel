import { useEffect, useState } from "react";
import { supabase } from "../services/supabaseService";
import { Card, CardHeader, CardTitle, CardBody, Row, Col, Container } from "react-bootstrap";
import { FaTemperatureHigh } from "react-icons/fa";
import { WiHumidity } from "react-icons/wi";
import { FaWind } from "react-icons/fa6";
import { FaUserGroup } from "react-icons/fa6";

type DeviceData = {
  device_id: number;
  datapoint: string;
  value: string | number;
};

export default function DashboardPanel() {
  const userInfo = JSON.parse(localStorage.getItem("user_info") || "{}");

  const hotel = userInfo.hotel || {};
  const floor = hotel.floor || {};
  const room = floor.room || {};
  const guest = userInfo.guest_info || {};

  const hotel_name = hotel.name;
  const room_name = room.name;
  const guest_name = `${guest.first_name ?? ""} ${guest.last_name ?? ""}`;

  const deviceIds: number[] = (room.devices || []).map((d: any) => d.id);

  const [iaqData, setIaqData] = useState<any>({});
  const [lifeBeingData, setLifeBeingData] = useState<any>({});

  useEffect(() => {
    if (deviceIds.length === 0) return;

    const fetchInitialData = async () => {
      const { data, error } = await supabase
        .from("realtime_data")
        .select("*")
        .in("device_id", deviceIds);

      if (data) {
        const iaq: any = {};
        const lb: any = {};

        data.forEach((row) => {
          const devId = row.device_id;
          const matchingDevice = room.devices.find((d: any) => d.id === devId);

          if (!matchingDevice) return;

          if (matchingDevice.device_type === "iaq_sensor") {
            iaq[row.datapoint] = row.value;
          } else if (matchingDevice.device_type === "presence_sensor") {
            lb[row.datapoint] = row.value;
          }
        });

        setIaqData(iaq);
        setLifeBeingData(lb);
      }

      if (error) console.error("Error fetching initial data:", error);
    };

    fetchInitialData();

    const channel = supabase
      .channel("room-data")
      .on(
        "postgres_changes",
        {
          event: "UPDATE",
          schema: "public",
          table: "realtime_data",
        },
        (payload) => {
          const { device_id, datapoint, value } = payload.new as DeviceData;

          if (!deviceIds.includes(device_id)) return;

          const matchingDevice = room.devices.find((d: any) => d.id === device_id);
          if (!matchingDevice) return;

          if (matchingDevice.device_type === "iaq_sensor") {
            setIaqData((prev: any) => ({ ...prev, [datapoint]: value }));
          } else if (matchingDevice.device_type === "presence_sensor") {
            setLifeBeingData((prev: any) => ({ ...prev, [datapoint]: value }));
          }
        }
      )
      .subscribe();

    return () => {
      supabase.removeChannel(channel);
    };
  }, [deviceIds.join(",")]); // rerun if devices change

  return (
    <Container>
      <Row>
        <h4> Welcome to { hotel_name }</h4>
        <div>Guest Name: {guest_name}</div>
        <div>Room: {room_name}</div>
      </Row>
      <Row className="mt-2">
          <Col xs={6}>
            <Card>
              <CardBody>
                <div className="d-flex align-items-center w-100 justify-content-between">
                  <CardTitle>Temperature</CardTitle>
                  <FaTemperatureHigh className="icon"/>
                </div>
                {iaqData?.temperature ? `${iaqData.temperature} C` : "N/A"}
              </CardBody>
            </Card>
          </Col>
          <Col xs={6}>
            <Card>
              <CardBody>
                <div className="d-flex align-items-center w-100 justify-content-between">
                  <CardTitle>Humidity</CardTitle>
                  <WiHumidity className="icon"/>
                </div>
                {iaqData?.humidity ? `${iaqData.humidity}%` : "N/A"}
              </CardBody>
            </Card>
          </Col>
        </Row>
        <Row className="mt-3">
          <Col xs={6}>
            <Card>
              <CardBody>
                <div className="d-flex align-items-center w-100 justify-content-between">
                  <CardTitle>CO₂</CardTitle>
                  <FaWind className="icon"/>
                </div>
                {iaqData?.co2 ? `${iaqData.co2}%` : "N/A"}
              </CardBody>
            </Card>
          </Col>
          <Col xs={6}>
            <Card>
              <CardBody>
                <div className="d-flex align-items-center w-100 justify-content-between">
                  <CardTitle>Occupied</CardTitle>
                  <FaUserGroup className="icon"/>
                </div>
                {lifeBeingData?.presence_state ? "Yes" : "No"}
              </CardBody>
            </Card>
          </Col>
        </Row>
    </Container>
  );
}
