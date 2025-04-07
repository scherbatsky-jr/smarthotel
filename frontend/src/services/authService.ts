import axios from 'axios';

const BASE_URL = import.meta.env.VITE_BACKEND_URL;

// Interfaces matching the nested backend response
export interface Device {
  id: number;
  device_type: string;
}

export interface Room {
  id: number;
  name: string;
  devices: Device[];
}

export interface Floor {
  id: number;
  number: string;
  room: Room;
}

export interface Hotel {
  id: number;
  name: string;
  floor: Floor;
}

export interface GuestInfo {
  first_name: string;
  last_name: string;
  contact: string;
  address: string;
}

export interface ReservationInfo {
  id: number;
  start_date: string;
  end_date: string;
  guest_info: GuestInfo;
  hotel: Hotel;
}

// Function to log in with passkey and store user info
export async function loginWithPasskey(passkey: string): Promise<ReservationInfo> {
  const response = await axios.post<{ reservation: ReservationInfo }>(`${BASE_URL}/login/guest`, { passkey });
  const reservation = response.data.reservation;

  // Save to localStorage
  localStorage.setItem('user_info', JSON.stringify(reservation));

  return reservation;
}

// Fetch user info from localStorage
export function getUserInfo(): ReservationInfo | null {
  const info = localStorage.getItem('user_info');
  return info ? JSON.parse(info) : null;
}

// Logout helper
export function logout() {
  localStorage.removeItem('user_info');
}
