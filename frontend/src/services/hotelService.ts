import axios from 'axios';

const BASE_URL = import.meta.env.VITE_BACKEND_URL;

export async function getRoomData(roomId: string) {
  const res = await axios.get(`${BASE_URL}/rooms/${roomId}/data/`);
  return res.data;
}

export async function getHotels() {
  const res = await axios.get(`${BASE_URL}/hotels/`);
  return res.data;
}

export async function getGroupedRoomsByHotel(hotelId: string) {
  const res = await fetch(`${import.meta.env.VITE_BACKEND_URL}/hotels/${hotelId}/rooms`);
  return res.json();
}