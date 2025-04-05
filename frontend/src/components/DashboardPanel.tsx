import { useEffect, useState } from 'react';
import { getRoomData } from '../services/hotelService';
import { Container, Row, Col, Card, CardBody, CardTitle, CardHeader } from 'react-bootstrap';
import { getUserInfo } from '../services/authService';

export default function DashboardPanel() {
  const [data, setData] = useState<any>(null);
  const userInfo = getUserInfo();

  const roomId = userInfo?.room_id;
  const guestName = `${userInfo?.guest.first_name} ${userInfo?.guest.last_name}`;
  const hotelName = userInfo?.hotel_name;
  const roomName = userInfo?.room_name;

  useEffect(() => {
    if (roomId) {
      getRoomData(roomId).then(setData);
    }
  }, [roomId]);

  return (
    <Card>
      <CardHeader>
        <CardTitle>Welcome to {hotelName}!</CardTitle>
        <p className="mb-0">
          Guest: <strong>{guestName}</strong> <br />
          Room: <strong>{roomName}</strong>
        </p>
      </CardHeader>

      <CardBody>
        <Container>
          <Row>
            <Col xs={6}>
              <Card>
                <CardBody>
                  <CardTitle>Temperature</CardTitle>
                  {data?.iaq?.temperature ?? 'N/A'}
                </CardBody>
              </Card>
            </Col>
            <Col xs={6}>
              <Card>
                <CardBody>
                  <CardTitle>Humidity</CardTitle>
                  {data?.iaq?.humidity ?? 'N/A'}
                </CardBody>
              </Card>
            </Col>
          </Row>

          <Row className="mt-3">
            <Col xs={6}>
              <Card>
                <CardBody>
                  <CardTitle>CO₂</CardTitle>
                  {data?.iaq?.co2 ?? 'N/A'}
                </CardBody>
              </Card>
            </Col>
            <Col xs={6}>
              <Card>
                <CardBody>
                  <CardTitle>Occupied</CardTitle>
                  {data?.life_being?.presence_state ? 'Yes' : 'No'}
                </CardBody>
              </Card>
            </Col>
          </Row>
        </Container>
      </CardBody>
    </Card>
  );
}
