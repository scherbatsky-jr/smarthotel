import axios from 'axios';

const BASE_URL = import.meta.env.VITE_BACKEND_URL;

export interface GuestInfo {
  first_name: string;
  last_name: string;
  contact: string;
  address: string;
}

export interface ReservationInfo {
  guest: GuestInfo;
  room_id: number;
  room_name: string;
  floor_id: number;
  floor_name: string;
  hotel_id: number;
  hotel_name: string;
}

export async function loginWithPasskey(passkey: string): Promise<ReservationInfo> {
  const response = await axios.post<ReservationInfo>(`${BASE_URL}/login/guest`, { passkey });
  const data = response.data;

  // Save to localStorage
  localStorage.setItem('user_info', JSON.stringify(data));

  return data;
}

export function getUserInfo(): ReservationInfo | null {
  const info = localStorage.getItem('user_info');
  return info ? JSON.parse(info) : null;
}

export function logout() {
  localStorage.removeItem('user_info');
}
