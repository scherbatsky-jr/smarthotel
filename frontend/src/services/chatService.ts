import axios from 'axios';
import { getAccessToken, getReservationInfo } from './authService';

const BASE_URL = import.meta.env.VITE_BACKEND_URL;

export async function sendChatMessage(message: string) {
  const reservation = getReservationInfo();
  const token = getAccessToken();

  const reservation_id = reservation?.id;
  const hotel_id = reservation?.hotel?.id;
  const floor_id = reservation?.hotel?.floor?.id;
  const room_id = reservation?.hotel?.floor?.room?.id;
  const room_name = reservation?.hotel?.floor?.room?.name;

  const res = await axios.post(
    `${BASE_URL}/chat/`,
    {
      message,
      user_info: {
        reservation_id,
        hotel_id,
        floor_id,
        room_id,
        room_name
      }
    },
    {
      headers: {
        Authorization: `Bearer ${token}`
      }
    }
  );

  return res.data.reply;
}
