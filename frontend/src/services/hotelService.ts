import axios from 'axios';

const BASE_URL = import.meta.env.VITE_BACKEND_URL;

export async function getRoomData(roomId: string) {
  const token = localStorage.getItem("access_token");
  const res = await axios.get(`${BASE_URL}/rooms/${roomId}/data/`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
  return res.data;
}

export async function getHotels() {
  const token = localStorage.getItem("access_token");
  const res = await axios.get(`${BASE_URL}/hotels/`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
  return res.data;
}

export async function getGroupedRoomsByHotel(hotelId: string) {
  const token = localStorage.getItem("access_token");
  const res = await fetch(`${import.meta.env.VITE_BACKEND_URL}/hotels/${hotelId}/rooms`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
  return res.json();
}

export async function downloadEnergySummary(hotelId: string, roomId: string | null, resolution: string, startDate: string, endDate: string) {
  const token = localStorage.getItem("access_token");
  let url = "";

  if (roomId) {
    url = `${BASE_URL}/rooms/${roomId}/energy_summary/?resolution=${resolution}&start_date=${startDate}&end_date=${endDate}`;
  } else {
    url = `${BASE_URL}/hotels/${hotelId}/energy_summary/?resolution=${resolution}&start_date=${startDate}&end_date=${endDate}`;
  }

  const res = await axios.get(url, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
    responseType: "blob"
  });

  return res.data;
}
