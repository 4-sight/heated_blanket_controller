import warmzLogo from "../assets/warmz.svg";

import "./Home.css";

const Home = ({ ...props }) => {
  return (
    <>
      <img src={warmzLogo} class="logo" alt="Warmz logo" />
      <h1>Warmz</h1>
      <div className="links">
        <a className="nav-link" href="/app/controls">
          controls
        </a>
        <a className="nav-link" href="/app/settings">
          settings
        </a>
      </div>
    </>
  );
};

export default Home;
