import { Router } from "preact-router";

import Home from "./pages/Home";
import Controls from "./pages/Controls";
import Logs from "./pages/Logs";
import NotFound from "./pages/NotFound";

import "./app.css";

export function App() {
  return (
    <Router>
      <Home path="/app/" />
      <Controls path="/app/controls" />
      <Logs path="app/logs" />
      <NotFound default />
    </Router>
  );
}
