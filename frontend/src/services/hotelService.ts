import axios from 'axios';

const BASE_URL = import.meta.env.VITE_BACKEND_URL;

export async function getRooms() {
  const res = await axios.get(`${BASE_URL}/hotels/1/floors/`); // Assuming hotel ID 1
  const allRooms: { id: string; name: string }[] = [];

  for (const floor of res.data) {
    const floorRooms = await axios.get(`${BASE_URL}/floors/${floor.id}/rooms/`);
    allRooms.push(...floorRooms.data);
  }

  return allRooms;
}
  
export async function getRoomData(roomId: string) {
  const res = await axios.get(`${BASE_URL}/rooms/${roomId}/data/`);
  return res.data;
}

export async function getHotels() {
  const res = await axios.get(`${BASE_URL}/hotels/`);
  return res.data;
}

export async function getFloorsWithRooms(hotelId: string) {
  const floorsRes = await axios.get(`${BASE_URL}/hotels/${hotelId}/floors/`);
  const floors = floorsRes.data;

  const result = await Promise.all(
    floors.map(async (floor: any) => {
      const roomsRes = await axios.get(`${BASE_URL}/floors/${floor.id}/rooms/`);
      return {
        floor: floor,
        rooms: roomsRes.data,
      };
    })
  );

  return result;
}