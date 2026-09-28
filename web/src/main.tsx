import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "./ds/styles.css";
import { App } from "./App";
import { Motion } from "./motion";

createRoot(document.getElementById("root")!).render(<StrictMode><Motion><App /></Motion></StrictMode>);
