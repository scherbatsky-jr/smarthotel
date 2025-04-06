import { useEffect, useState } from "react";
import { supabase } from "../services/supabaseService";
import { Card, CardHeader, CardTitle, CardBody, Row, Col } from "react-bootstrap";

type DeviceData = {
  device_id: string;
  datapoint: string;
  value: string | number;
};

export default function DashboardPanel() {
  const userInfo = JSON.parse(localStorage.getItem("user_info") || "{}");
  const { hotel_id, floor_id, room_id, guest_name, room_name, hotel_name } = userInfo;

  const [iaqData, setIaqData] = useState<any>({});
  const [lifeBeingData, setLifeBeingData] = useState<any>({});

  useEffect(() => {
    const deviceIdPattern = `_R${room_id}`;

    const fetchInitialData = async () => {
      const { data, error } = await supabase
        .from("realtime_data")
        .select("*")
        .like("device_id", `%${deviceIdPattern}`);

      if (data) {
        const iaq: any = {};
        const lb: any = {};

        data.forEach((row) => {
          if (row.device_id.startsWith("iaq_sensor")) {
            iaq[row.datapoint] = row.value;
          } else if (row.device_id.startsWith("presence_sensor")) {
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
        table: "realtime_data"
      },
      (payload) => {
        const { device_id, datapoint, value } = payload.new as DeviceData;

        if (!device_id.includes(deviceIdPattern)) return;

        if (device_id.startsWith("iaq_sensor")) {
          setIaqData((prev: any) => ({ ...prev, [datapoint]: value }));
        } else if (device_id.startsWith("presence_sensor")) {
          setLifeBeingData((prev: any) => ({ ...prev, [datapoint]: value }));
        }
      }
    )
    .subscribe();

    return () => {
      supabase.removeChannel(channel);
    };
  }, [hotel_id, floor_id, room_id]);

  return (
    <Card>
      <CardHeader>
        <CardTitle>Dashboard</CardTitle>
      </CardHeader>
      <CardBody>
        <h5>Welcome to {hotel_name}!</h5>
        <p>Guest Name: {guest_name}</p>
        <p>Room: {room_name}</p>

        <Row>
          <Col xs={12} md={6}>
            <Card>
              <CardBody>
                <CardTitle>Temperature</CardTitle>
                {iaqData?.temperature ?? "N/A"}
              </CardBody>
            </Card>
          </Col>
          <Col xs={12} md={6}>
            <Card>
              <CardBody>
                <CardTitle>Humidity</CardTitle>
                {iaqData?.humidity ?? "N/A"}
              </CardBody>
            </Card>
          </Col>
        </Row>

        <Row className="mt-3">
          <Col xs={12} md={6}>
            <Card>
              <CardBody>
                <CardTitle>CO₂</CardTitle>
                {iaqData?.co2 ?? "N/A"}
              </CardBody>
            </Card>
          </Col>
          <Col xs={12} md={6}>
            <Card>
              <CardBody>
                <CardTitle>Occupied</CardTitle>
                {lifeBeingData?.presence_state ? "Yes" : "No"}
              </CardBody>
            </Card>
          </Col>
        </Row>
      </CardBody>
    </Card>
  );
}
