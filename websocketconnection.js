import { WebSocket, WebSocketServer } from "ws";

const wss = new WebSocketServer({ port: 8080, host: "192.168.56.1" });

wss.on("listening", () => {
  console.log("WebSocket server running on ws://localhost:8080");
});

wss.on("connection", (ws) => {
  console.log("Client connected");

  ws.on("message", (message) => {
    console.log("message argument",message)
    const messageString = message.toString();
    console.log("message", messageString);
    if (
      messageString.startsWith("REGISTER") ||
      messageString.startsWith("INVITE")
    ) {
      broadcastMessageExcept(ws, message);
    } else if (messageString.startsWith("AUDIO_DATA:")) {
      broadcastMessageExceptfortos(ws, message, true);
    } else if (messageString.startsWith("SDP_ANSWER:")) {
      broadcastMessageExcept(ws, message);
    } else if (messageString == "call_acepted") {
      broadcastMessageExcept(ws, message);
    }  else if (messageString.startsWith("SIP/2.0 200 OK")) {
      // Handle the ACK message separately
      broadcastMessageExcept(ws, message);
    }
    else {
      console.warn("Received non-SIP message:", messageString);
    }
  });

  ws.on("close", () => {
    console.log("Client disconnected");
  });
});

function broadcastMessageExcept(excludedClient, message) {
  wss.clients.forEach((client) => {
    if (client !== excludedClient && client.readyState === WebSocket.OPEN) {
      client.send(message);
    }
  });
}

function broadcastMessageExceptfortos(
  excludedClient,
  message,
  isAudioData = false
) {
  wss.clients.forEach((client) => {
    if (client !== excludedClient && client.readyState === WebSocket.OPEN) {
      if (isAudioData) {
        client.send(message);
      } else {
        client.send(message);
      }
    }
  });
}
