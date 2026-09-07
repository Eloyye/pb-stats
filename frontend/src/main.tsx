import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { App } from "./App";
import { takeSessionToken } from "./session";
import "./style.css";

const sessionToken = takeSessionToken();
const root = document.getElementById("root");
if (!root) throw new Error("Application root is missing");
createRoot(root).render(
  <StrictMode>
    <App sessionToken={sessionToken} />
  </StrictMode>,
);
