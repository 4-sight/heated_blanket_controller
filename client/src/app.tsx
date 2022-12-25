import { Router } from "preact-router";

import Home from "./pages/Home";
import NotFound from "./pages/NotFound";

import "./app.css";

export function App() {
  return (
    <Router>
      <Home path="/app/" />
      <NotFound default />
    </Router>
  );
}
