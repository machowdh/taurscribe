'use client';

import { useEffect, useRef, useState } from "react";

import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";

const Home = () => {
  const [isConnected, setIsConnected] = useState(false);
  const [messages, setMessages] = useState<string[]>([]);
  const [isTranslating, setIsTranslating] = useState(false);
  const socketRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    const connectWebSocket = () => {
      socketRef.current = new WebSocket("ws://localhost:8008/ws");

      socketRef.current.onopen = () => {
        console.log("WebSocket is open now.");
        setIsConnected(true);
      };

      socketRef.current.onmessage = (event) => {
        console.log("Received from server: " + event.data);
        setMessages((prev) => [...prev, event.data]);
      };

      socketRef.current.onerror = (event) => {
        console.error("WebSocket error observed:", event);
      };

      socketRef.current.onclose = () => {
        console.log("WebSocket is closed now.");
        setIsConnected(false);
      };
    };

    connectWebSocket();

    return () => {
      if (socketRef.current) {
        socketRef.current.close();
      }
    };
  }, []);

  const startRecording = () => {
    setIsTranslating(true);
    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      const message = JSON.stringify({ command: "start" });
      socketRef.current.send(message);
    }
  };

  const stopRecording = () => {
    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      const message = JSON.stringify({ command: "stop" });
      socketRef.current.send(message);
    }
    setIsTranslating(false);
  };

  return (
    <div className="container mx-auto p-4">
      <h1 className="mb-4 text-2xl font-bold">Live Transcription</h1>
      <div className="space-y-4">
        <Button
          onClick={startRecording}
          disabled={isTranslating || !isConnected}
        >
          Start Recording
        </Button>

        <Button
          onClick={stopRecording}
          disabled={!isTranslating || !isConnected}
        >
          Stop Recording
        </Button>

        <Textarea
          value={messages.join("\n")}
          readOnly
          className="h-64"
          placeholder="Transcription will appear here..."
        />
      </div>
    </div>
  );
};

export default Home;
