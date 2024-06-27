import Image from "next/image";
import {useEffect, useState} from 'react';

export default function Home() {
  const [messages, setMessages] = useState<string[]>([]);

  useEffect(() => {
    const ws = new WebSocket('wss://localhost:8008/ws/translate')

    ws.onmessage = (event) => {
      setMessages(prev => [...prev, event.data]);
    };


    return () => {
      ws.close();
    };
  }, []);

  return (
    <main>
      <h1>Placeholder Text</h1>
    </main>
  );
}
