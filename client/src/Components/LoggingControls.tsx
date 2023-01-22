import useLoggingLevel from "../hooks/useLoggingLevel";

const LOGGING_LEVELS = ["DEBUG", "VERBOSE", "INFO"];

const LoggingControls = () => {
  const [level, onChange] = useLoggingLevel();

  if (level == null) return null;

  return (
    <div className="logging-level-controls">
      <p className="title">Logging</p>
      <p className="level">{LOGGING_LEVELS[level - 1]}</p>
      <input
        type="range"
        value={level}
        min={0}
        max={2}
        step={1}
        onChange={(e) => {
          onChange(parseInt(e.currentTarget.value));
        }}
      />
    </div>
  );
};

export default LoggingControls;
