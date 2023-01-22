import usePollLogs from "../hooks/usePollLogs";

import warmzLogo from "../assets/warmz.svg";
import DisplayLogs from "../Components/DisplayLogs";

import "./Logs.css";
import { useCallback } from "preact/hooks";
import CurveControls from "../Components/CurveControls";
import LoggingControls from "../Components/LoggingControls";
import ManualZoneControls from "../Components/ManualZoneControls";

const Controls = ({ ...props }) => {
  const logs = usePollLogs();

  const saveLogs = useCallback(() => {
    const blob = new Blob([JSON.stringify(logs)], {
      type: "application/json",
    });
    const a = document.createElement("a");
    a.download = "warmz-logs.txt";
    a.href = URL.createObjectURL(blob);
    a.addEventListener("click", (e) => {
      setTimeout(() => URL.revokeObjectURL(a.href), 30 * 1000);
    });
    a.click();
  }, [logs]);

  return (
    <>
      <a href="/app">
        <img src={warmzLogo} class="logo" alt="Warmz logo" />
      </a>
      <h1>Logs</h1>
      <LoggingControls />
      <ManualZoneControls />
      <CurveControls />
      {logs && (
        <>
          <SaveButton onClick={saveLogs} />
          <DisplayLogs logs={logs} />
          <SaveButton onClick={saveLogs} />
        </>
      )}
    </>
  );
};

const SaveButton = ({ onClick }: { onClick: () => void }) => {
  return (
    <button className="save-button" onClick={onClick}>
      Save Logs
    </button>
  );
};

export default Controls;
