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
  hotel: Hotel;
}

// Function to log in with passkey and store user info and access token
export async function loginWithPasskey(passkey: string): Promise<void> {
  const response = await axios.post<{ reservation: ReservationInfo; user_info: GuestInfo; access_token: string; refresh_token: string }>(`${BASE_URL}/login/guest/`, { passkey });

  localStorage.setItem('user_info', JSON.stringify(response.data.user_info));
  localStorage.setItem('reservation', JSON.stringify(response.data.reservation));
  localStorage.setItem('access_token', response.data.access_token);
  localStorage.setItem('refresh_token', response.data.refresh_token);
}

// Function to log in as admin and store access token
export async function loginAsAdmin(username: string, password: string): Promise<{ user_info: any }> {
  const response = await axios.post<{ access_token: string; refresh_token: string; user_info: any }>(`${BASE_URL}/login/admin/`, { username, password });
  localStorage.setItem('access_token', response.data.access_token);
  localStorage.setItem('refresh_token', response.data.refresh_token);
  localStorage.setItem('user_info', JSON.stringify(response.data.user_info));
  return { user_info: response.data.user_info };
}

// Access token getter
export function getAccessToken(): string | null {
  return localStorage.getItem('access_token');
}

// Fetch user info from localStorage
export function getUserInfo(): ReservationInfo | null {
  const info = localStorage.getItem('user_info');
  return info ? JSON.parse(info) : null;
}

// Logout helper
export function logout() {
  localStorage.removeItem('user_info');
  localStorage.removeItem('reservation');
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
}
