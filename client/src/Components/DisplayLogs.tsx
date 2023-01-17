import { Log, Logs } from "../hooks/usePollLogs";
import "./DisplayLogs.css";

interface Props {
  logs: Logs;
}

const DisplayLogs = ({ logs }: Props) => {
  return (
    <div className="log-table">
      <DisplayChannel index={1} channelLogs={logs.channel1} />
      <DisplayChannel index={2} channelLogs={logs.channel2} />
    </div>
  );
};

interface ChannelProps {
  index: number;
  channelLogs: Log[];
}

const DisplayChannel = ({ index, channelLogs }: ChannelProps) => {
  return (
    <div className="channel-table">
      <h3 className="channel-heading">Channel {index}</h3>
      <div className="channel-rows">
        {channelLogs.map((log) => (
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
