"use client";

import { useEffect, useRef, useState } from "react";

export default function Home() {
  const [messages, setMessages] = useState<string[]>([]);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    if (wsRef.current) {
      // If WebSocket is already created, do not create it again
      return;
    }

    console.log("Setting up WebSocket connection");
    wsRef.current = new WebSocket("ws://localhost:8008/ws");

    wsRef.current.onopen = () => {
      console.log("WebSocket connection opened");
    };

    wsRef.current.onmessage = (event) => {
      console.log("Received message:", event.data);
      setMessages((prev) => [...prev, event.data]);
    };

    wsRef.current.onclose = (event) => {
      console.log("WebSocket connection closed:", event);
      wsRef.current = null; // Reset the ref
    };

    wsRef.current.onerror = (error) => {
      console.error("WebSocket error:", error);
    };

    return () => {
      // if (wsRef.current) {
      //   console.log("Closing WebSocket connection");
      //   wsRef.current.close();
      // }
    };
  }, []);

  return (
    <main>
      <h1>WebSocket Messages</h1>
      <ul>
        {messages.map((msg, idx) => (
          <li key={idx}>{msg}</li>
        ))}
      </ul>
    </main>
  );
}
