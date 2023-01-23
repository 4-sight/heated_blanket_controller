import { ChannelData, Log, Logs } from "../hooks/usePollLogs";
import "./DisplayLogs.css";

interface Props {
  logs: Logs | null;
}

const DisplayLogs = ({ logs }: Props) => {
  return (
    logs && (
      <div className="log-table">
        <DisplayChannel index={1} channelLogs={logs.channel_1} />
        <DisplayChannel index={2} channelLogs={logs.channel_2} />
      </div>
    )
  );
};

interface ChannelProps {
  index: number;
  channelLogs: ChannelData;
}

const DisplayChannel = ({ index, channelLogs }: ChannelProps) => {
  return (
    <div className="channel-table">
      <h3 className="channel-heading">Channel {index}</h3>
      <div className="channel-rows">
        <div>Min Threshold: {channelLogs.min_t}</div>
        <div>Max Threshold: {channelLogs.max_t}</div>
        <div>Mean Threshold: {channelLogs.mean_t}</div>
        <div>Out of range count: {channelLogs.exception_count}</div>
        {channelLogs.exceptions.map((log: Log) => (
          <div className="channel-row">
            <div className="timestamp">T: {log.t}</div>
            <div className="feet">
              Feet: <ZoneOutput zoneOutput={log.f} />
            </div>
            <div className="body">
              Body: <ZoneOutput zoneOutput={log.b} />
            </div>
            <div className="range">
              Expected Range: {log.r.start} - {log.r.stop}
            </div>
            <div className="safety-val">{log.sv}mV</div>
          </div>
        ))}
      </div>
    </div>
  );
};

const ZoneOutput = ({ zoneOutput }: { zoneOutput: number }) => {
  if (zoneOutput == 1) {
    return <span className="zone-output-off">OFF</span>;
  }
  return <span className="zone-output-on">ON</span>;
};

export default DisplayLogs;
