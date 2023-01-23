import useCurveData from "../hooks/useCurveData";
import "./CurveControls.css";

const CurveControls = () => {
  return (
    <div className="curve-controls">
      <ChannelCurveControls index={1} />
      <ChannelCurveControls index={2} />
    </div>
  );
};

const ChannelCurveControls = ({ index }: { index: number }) => {
  const [data, onChange] = useCurveData(index);

  if (data == null) {
    return null;
  }

  return (
    <div className="channel-curve-controls">
      <SettingInput
        label="upper"
        value={data.upper}
        min={0}
        max={150}
        step={1}
        onChange={(v) => {
          onChange({ upper: parseInt(v) });
        }}
      />
      <SettingInput
        label="lower"
        value={data.lower}
        min={-20}
        max={40}
        step={1}
        onChange={(v) => {
          onChange({ lower: parseInt(v) });
        }}
      />
      <div className="zones">
        <div className="zone-settings">
          <SettingInput
            label="feet_max"
            value={data.feet_max}
            min={0}
            max={200}
            step={1}
            onChange={(v) => {
              onChange({ feet_max: parseInt(v) });
            }}
          />
          <SettingInput
            label="feet A"
            value={data.feet_curve.A}
            min={0}
            max={1}
            step={0.01}
            onChange={(v) => {
              onChange({
                feet_curve: {
                  ...data.feet_curve,
                  A: parseFloat(v),
                },
              });
            }}
          />
          <SettingInput
            label="feet B"
            value={data.feet_curve.B}
            min={0}
            max={0.2}
            step={0.001}
            onChange={(v) => {
              onChange({
                feet_curve: {
                  ...data.feet_curve,
                  B: parseFloat(v),
                },
              });
            }}
          />
          <SettingInput
            label="feet C"
            value={data.feet_curve.C}
            min={0}
            max={300}
            step={1}
            onChange={(v) => {
              onChange({
                feet_curve: {
                  ...data.feet_curve,
                  C: parseInt(v),
                },
              });
            }}
          />
        </div>
        <div className="zone-settings">
          <SettingInput
            label="body_max"
            value={data.body_max}
            min={0}
            max={200}
            step={1}
            onChange={(v) => {
              onChange({ body_max: parseInt(v) });
            }}
          />
          <SettingInput
            label="body A"
            value={data.body_curve.A}
            min={0}
            max={1}
            step={0.01}
            onChange={(v) => {
              onChange({
                body_curve: {
                  ...data.body_curve,
                  A: parseFloat(v),
                },
              });
            }}
          />
          <SettingInput
            label="body B"
            value={data.body_curve.B}
            min={0}
            max={0.2}
            step={0.001}
            onChange={(v) => {
              onChange({
                body_curve: {
                  ...data.body_curve,
                  B: parseFloat(v),
                },
              });
            }}
          />
          <SettingInput
            label="body C"
            value={data.body_curve.C}
            min={0}
            max={300}
            step={1}
            onChange={(v) => {
              onChange({
                body_curve: {
                  ...data.body_curve,
                  C: parseInt(v),
                },
              });
            }}
          />
        </div>
      </div>
    </div>
  );
};

const SettingInput = ({
  label,
  value,
  min,
  max,
  step,
  onChange,
}: {
  label: string;
  value: number;
  min: number;
  max: number;
  step: number;
  onChange: (val: string) => void;
}) => {
  return (
    <div className="setting-control">
      <label htmlFor={label}>{label}</label>
      <div className="input-container">
        <input
          className="settings-sinput"
          name={label}
          type="number"
          value={value}
          min={min}
          max={max}
          step={step}
          onChange={(e) => {
            onChange(e.currentTarget.value);
          }}
        ></input>
        {value}
      </div>
    </div>
  );
};

export default CurveControls;
