import { JSXInternal } from "preact/src/jsx";
import useHeaterLevels, {
  UpdateHeaterLevels,
  ZoneLevels,
} from "../hooks/useHeaterLevels";
import "./ManualZoneControls.css";

const ManualZoneControls = () => {
  const [levels, onChange] = useHeaterLevels();

  if (levels == null) return null;

  return (
    <div className="zone-level-controls">
      <p className="zone-levels-title">Zone Levels</p>
      <div className="channels-container">
        <ChannelZoneControls
          channelIndex={1}
          levels={levels.c1}
          onChange={onChange}
        />
        <ChannelZoneControls
          channelIndex={2}
          levels={levels.c2}
          onChange={onChange}
        />
      </div>
    </div>
  );
};

const ChannelZoneControls = ({
  levels: { f, b },
  channelIndex,
  onChange,
}: {
  levels: ZoneLevels;
  channelIndex: 1 | 2;
  onChange: (val: UpdateHeaterLevels) => void;
}) => {
  return (
    <div className="channel-zone-controls">
      <p className="channel-heading">Channel {channelIndex}</p>
      <ZoneLevelInput
        name="feet"
        level={f}
        onChange={(e) => {
          if (channelIndex == 1) {
            onChange({ c1: { f: parseInt(e.currentTarget.value) } });
          } else {
            onChange({ c2: { f: parseInt(e.currentTarget.value) } });
          }
        }}
      />
      <ZoneLevelInput
        name="body"
        level={b}
        onChange={(e) => {
          if (channelIndex == 1) {
            onChange({ c1: { b: parseInt(e.currentTarget.value) } });
          } else {
            onChange({ c2: { b: parseInt(e.currentTarget.value) } });
          }
        }}
      />
    </div>
  );
};

const ZoneLevelInput = ({
  level,
  name,
  onChange,
}: {
  level: number;
  name: string;
  onChange: (e: JSXInternal.TargetedEvent<HTMLInputElement>) => void;
}) => {
  return (
    <div className="zone-level-slider-container">
      <label htmlFor={name}>{name}</label>
      <div className="slider-wrapper">
        <input
          type="range"
          name={name}
          value={level}
          className="zone-level-slider"
          min={0}
          max={9}
          step={1}
          onChange={onChange}
        />
        {level}
      </div>
    </div>
  );
};

export default ManualZoneControls;
