import { Router } from "preact-router";

import Home from "./pages/Home";
import NotFound from "./pages/NotFound";
import Controls from "./pages/Controls";

import "./app.css";

export function App() {
  return (
    <Router>
      <Home path="/app/" />
      <Controls path="/app/controls" />
      <NotFound default />
    </Router>
  );
}
