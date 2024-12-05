import React, { useEffect, useState } from "react";
import io from "socket.io-client";
import "./App.css";

const socket = io("http://127.0.0.1:5000"); // Connect to the backend

function App() {
  const [usbDevices, setUsbDevices] = useState([]);
  const [logs, setLogs] = useState([]);

  useEffect(() => {
    // Fetch initial list of devices
    fetch("http://127.0.0.1:5000/api/usb_devices")
      .then((res) => res.json())
      .then((data) => setUsbDevices(data));

    // Listen for USB events from the backend
    socket.on("usb_event", (data) => {
      const { event, device } = data;
      setLogs((prevLogs) => [
        ...prevLogs,
        `${new Date().toLocaleString()}: Device ${event} - ${device.product || "Unknown"}`,
      ]);

      // Update USB devices list
      if (event === "connected") {
        setUsbDevices((prevDevices) => [...prevDevices, device]);
      } else if (event === "removed") {
        setUsbDevices((prevDevices) =>
          prevDevices.filter(
            (d) =>
              d.idVendor !== device.idVendor || d.idProduct !== device.idProduct
          )
        );
      }
    });

    return () => {
      socket.off("usb_event");
    };
  }, []);

  return (
    <div className="App">
      <header>
        <h1>USB Detection App</h1>
      </header>
      <main>
        <section className="usb-status">
          <h2>Connected USB Devices</h2>
          <ul>
            {usbDevices.map((device, index) => (
              <li key={index}>
                {device.product || "Unknown Device"} - {device.manufacturer || "Unknown Manufacturer"}
              </li>
            ))}
          </ul>
        </section>
        <section className="logs">
          <h2>Logs</h2>
          <div className="log-area">
            {logs.map((log, index) => (
              <p key={index}>{log}</p>
            ))}
          </div>
        </section>
      </main>
    </div>
  );
}

export default App;
