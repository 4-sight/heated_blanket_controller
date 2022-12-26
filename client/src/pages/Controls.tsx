import warmzLogo from "../assets/warmz.svg";

import PresetButton from "../Components/PresetButton";

import "./Controls.css";

const Controls = ({ ...props }) => {
  return (
    <>
      <a href="/app">
        <img src={warmzLogo} class="logo" alt="Warmz logo" />
      </a>
      <h1>Controls</h1>
      <p className="presets-title">Presets</p>
      <div className="presets">
        {[1, 2, 3, 4, 5, 6].map((i) => (
          <PresetButton i={i} />
        ))}
      </div>
    </>
  );
};

export default Controls;