import { useEffect, useState, useRef } from "react";
import { Card, CardHeader, CardTitle, CardBody, Row, Col, Form, Button } from "react-bootstrap";
import { getGroupedRoomsByHotel, getHotels } from "../services/hotelService";
import { supabase } from "../services/supabaseService";
import { downloadEnergySummary } from "../services/hotelService";

type DeviceData = {
  device_id: number;
  datapoint: string;
  value: string | number;
};

export default function AdminDashboard() {
  const [hotels, setHotels] = useState<any[]>([]);
  const [groupedRooms, setGroupedRooms] = useState<any>({});
  const [selectedHotelId, setSelectedHotelId] = useState<string | null>(null);
  const [selectedRoom, setSelectedRoom] = useState<any>(null);
  const [iaqData, setIaqData] = useState<any>({});
  const [lifeBeingData, setLifeBeingData] = useState<any>({});
  const [resolution, setResolution] = useState("1day");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const deviceIdsRef = useRef<number[]>([]);
  const currentChannelRef = useRef<any>(null);

  useEffect(() => {
    fetchHotels();
  }, []);

  const fetchHotels = async () => {
    const data = await getHotels();
    setHotels(data);
  };

  const fetchGroupedRooms = async (hotelId: string) => {
    const data = await getGroupedRoomsByHotel(hotelId);
    console.log(data)
    if (typeof data === "object" && data !== null) {
      console.log('here')
      setGroupedRooms(data);
    } else {
      setGroupedRooms({});
    }

    setSelectedRoom(null);
    setIaqData({});
    setLifeBeingData({});
  };

  const subscribeToRealtimeData = async (room: any) => {
    if (currentChannelRef.current) {
      supabase.removeChannel(currentChannelRef.current);
    }

    const ids = room.devices.map((d: any) => d.id);
    deviceIdsRef.current = ids;

    const { data } = await supabase
      .from("realtime_data")
      .select("*")
      .in("device_id", ids);

    const iaq: any = {};
    const lb: any = {};
    data?.forEach((row) => {
      if (row.device_id && row.datapoint) {
        if (["temperature", "humidity", "co2"].includes(row.datapoint)) {
          iaq[row.datapoint] = row.value;
        } else {
          lb[row.datapoint] = row.value;
        }
      }
    });

    setIaqData(iaq);
    setLifeBeingData(lb);

    const idFilter = `in.(${ids.join(",")})`;
    const channel = supabase
      .channel("admin-room-data")
      .on(
        "postgres_changes",
        {
          event: "UPDATE",
          schema: "public",
          table: "realtime_data",
          filter: `device_id=${idFilter}`,
        },
        (payload) => {
          const { device_id, datapoint, value } = payload.new as DeviceData;
          if (["temperature", "humidity", "co2"].includes(datapoint)) {
            setIaqData((prev: any) => ({ ...prev, [datapoint]: value }));
          } else {
            setLifeBeingData((prev: any) => ({ ...prev, [datapoint]: value }));
          }
        }
      )
      .subscribe();

    currentChannelRef.current = channel;
  };

  useEffect(() => {
    if (selectedRoom) {
      subscribeToRealtimeData(selectedRoom);
    }
  }, [selectedRoom]);

  const handleDownloadSummary = async () => {
    if (!selectedHotelId && !selectedRoom) {
      alert("Please select a hotel or room before downloading the summary.");
      return;
    }

    const blob = await downloadEnergySummary(
      selectedHotelId!,
      selectedRoom?.id || null,
      resolution,
      startDate,
      endDate
    );

    const urlBlob = window.URL.createObjectURL(blob);
    const a = document.createElement('a');

    a.href = urlBlob;
    a.download = getEnergySummaryFilename();
    document.body.appendChild(a);
    a.click();
    a.remove();
    window.URL.revokeObjectURL(urlBlob);
  };

  const getEnergySummaryFilename = () => {
    if (!selectedHotelId) return "energy_summary.csv";

    const selectedHotel = hotels.find((hotel) => hotel.id == selectedHotelId);
    if (!selectedHotel) return "energy_summary.csv";

    if (selectedRoom) {
      return `energy_summary_${selectedHotel.name}_room_${selectedRoom.number}.csv`;
    }

    return `energy_summary_${selectedHotel.name}.csv`;
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Admin Dashboard</CardTitle>
      </CardHeader>
      <CardBody>
        <Form.Group className="mb-3">
          <Form.Label>Select Hotel</Form.Label>
          <Form.Select
            value={selectedHotelId || ""}
            onChange={(e) => {
              const hotelId = e.target.value;
              if (hotelId) {
                setSelectedHotelId(hotelId);
                fetchGroupedRooms(hotelId);
              } else {
                setSelectedHotelId(null);
                setGroupedRooms([]);
                setSelectedRoom(null);
                setIaqData({});
                setLifeBeingData({});
              }
            }}
          >
            <option value="">-- Select Hotel --</option>
            {hotels.map((h) => (
              <option key={h.id} value={h.id}>{h.name}</option>
            ))}
          </Form.Select>
        </Form.Group>

        <Form.Group className="mb-3">
          <Form.Label>Select Room</Form.Label>
          <Form.Select
            value={selectedRoom?.id || ""}
            onChange={(e) => {
              const roomId = parseInt(e.target.value);
              const room = groupedRooms
                .flatMap((group: any) => group.rooms)
                .find((r: any) => r.id === roomId);
              setSelectedRoom(room || null);
            }}
          >
            <option value="">-- Select Room --</option>
            {Array.isArray(groupedRooms) &&
              groupedRooms.map((group: any) => (
                group.rooms.length > 0 && (
                  <optgroup key={group.floor.id} label={`Floor ${group.floor.number}`}>
                    {group.rooms.map((room: any) => (
                      <option key={room.id} value={room.id}>
                        Room {room.number}
                      </option>
                    ))}
                  </optgroup>
                )
              ))}
          </Form.Select>
        </Form.Group>

        <Row>
            <Col xs={6}>
            <Card><CardBody><CardTitle>Temperature</CardTitle>{iaqData?.temperature ?? "N/A"}</CardBody></Card>
            </Col>
            <Col xs={6}>
            <Card><CardBody><CardTitle>Humidity</CardTitle>{iaqData?.humidity ?? "N/A"}</CardBody></Card>
            </Col>
        </Row>
        <Row className="mt-3">
            <Col xs={6}>
            <Card><CardBody><CardTitle>CO₂</CardTitle>{iaqData?.co2 ?? "N/A"}</CardBody></Card>
            </Col>
            <Col xs={6}>
            <Card><CardBody><CardTitle>Occupied</CardTitle>{lifeBeingData?.presence_state ? "Yes" : "No"}</CardBody></Card>
            </Col>
        </Row>

        <Card className="mt-4">
          <CardBody>
            <CardTitle>Download Energy Summary</CardTitle>
            <Form>
              <Form.Group className="mb-3">
                <Form.Label>Resolution</Form.Label>
                <Form.Select value={resolution} onChange={(e) => setResolution(e.target.value)}>
                  <option value="1hour">1 Hour</option>
                  <option value="1day">1 Day</option>
                  <option value="1month">1 Month</option>
                </Form.Select>
              </Form.Group>
              <Form.Group className="mb-3">
                <Form.Label>Start Date</Form.Label>
                <Form.Control type="date" value={startDate} onChange={(e) => setStartDate(e.target.value)} />
              </Form.Group>
              <Form.Group className="mb-3">
                <Form.Label>End Date</Form.Label>
                <Form.Control type="date" value={endDate} onChange={(e) => setEndDate(e.target.value)} />
              </Form.Group>
              <Button onClick={handleDownloadSummary}>Download Summary</Button>
            </Form>
          </CardBody>
        </Card>
      </CardBody>
    </Card>
  );
}
