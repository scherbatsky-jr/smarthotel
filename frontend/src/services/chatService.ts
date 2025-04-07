import axios from 'axios';
import { getUserInfo } from './authService';

const BASE_URL = import.meta.env.VITE_BACKEND_URL;

export async function sendChatMessage(message: string) {
  const userInfo = getUserInfo();

  const reservation_id = userInfo?.id;
  const hotel_id = userInfo?.hotel?.id;
  const floor_id = userInfo?.hotel?.floor?.id;
  const room_id = userInfo?.hotel?.floor?.room?.id;
  const room_name = userInfo?.hotel?.floor?.room?.name;

  const res = await axios.post(`${BASE_URL}/chat/`, {
    message,
    user_info: {
      reservation_id,
      hotel_id,
      floor_id,
      room_id,
      room_name
    }
  });

  return res.data.reply;
}
