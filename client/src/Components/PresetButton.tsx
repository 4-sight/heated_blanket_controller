import "./PresetButton.css";

type Props = {
  i: number;
};

const PresetButton = ({ i }: Props) => {
  const setPreset = () => {
    fetch("/api/apply_preset/", {
      method: "POST",
      body: JSON.stringify({
        preset: i,
      }),
    });
  };

  return (
    <>
      <button className="preset-button" onClick={setPreset}>
        {i}
      </button>
    </>
  );
};

export default PresetButton;
