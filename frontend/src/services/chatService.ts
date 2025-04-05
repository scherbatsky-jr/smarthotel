import axios from 'axios';
import { getUserInfo } from './authService';

const BASE_URL = import.meta.env.VITE_BACKEND_URL;

export async function sendChatMessage(message: string) {
  const userInfo = getUserInfo();

  const res = await axios.post(`${BASE_URL}/chat/`, {
    message,
    user_info: {
      hotel_id: userInfo?.hotel_id,
      floor_id: userInfo?.floor_id,
      room_id: userInfo?.room_id,
    }
  });

  return res.data.reply;
}
