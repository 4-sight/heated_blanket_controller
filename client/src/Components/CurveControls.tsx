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
      <SettingSlider
        label="upper"
        value={data.upper}
        min={0}
        max={150}
        step={1}
        onChange={(v: number) => {
          onChange({ upper: v });
        }}
      />
      <SettingSlider
        label="lower"
        value={data.lower}
        min={-20}
        max={40}
        step={1}
        onChange={(v: number) => {
          onChange({ lower: v });
        }}
      />
      <div className="zones">
        <div className="zone-settings">
          <SettingSlider
            label="feet_max"
            value={data.feet_max}
            min={0}
            max={200}
            step={1}
            onChange={(v: number) => {
              onChange({ feet_max: v });
            }}
          />
          <SettingSlider
            label="feet A"
            value={data.feet_curve.A}
            min={0}
            max={1}
            step={0.01}
            onChange={(v: number) => {
              onChange({
                feet_curve: {
                  ...data.feet_curve,
                  A: v,
                },
              });
            }}
          />
          <SettingSlider
            label="feet B"
            value={data.feet_curve.B}
            min={0}
            max={0.2}
            step={0.001}
            onChange={(v: number) => {
              onChange({
                feet_curve: {
                  ...data.feet_curve,
                  B: v,
                },
              });
            }}
          />
          <SettingSlider
            label="feet C"
            value={data.feet_curve.C}
            min={0}
            max={300}
            step={1}
            onChange={(v: number) => {
              onChange({
                feet_curve: {
                  ...data.feet_curve,
                  C: v,
                },
              });
            }}
          />
        </div>
        <div className="zone-settings">
          <SettingSlider
            label="body_max"
            value={data.body_max}
            min={0}
            max={200}
            step={1}
            onChange={(v: number) => {
              onChange({ body_max: v });
            }}
          />
          <SettingSlider
            label="body A"
            value={data.body_curve.A}
            min={0}
            max={1}
            step={0.01}
            onChange={(v: number) => {
              onChange({
                body_curve: {
                  ...data.body_curve,
                  A: v,
                },
              });
            }}
          />
          <SettingSlider
            label="body B"
            value={data.body_curve.B}
            min={0}
            max={0.2}
            step={0.001}
            onChange={(v: number) => {
              onChange({
                body_curve: {
                  ...data.body_curve,
                  B: v,
                },
              });
            }}
          />
          <SettingSlider
            label="body C"
            value={data.body_curve.C}
            min={0}
            max={300}
            step={1}
            onChange={(v: number) => {
              onChange({
                body_curve: {
                  ...data.body_curve,
                  C: v,
                },
              });
            }}
          />
        </div>
      </div>
    </div>
  );
};

const SettingSlider = ({
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
  onChange: (val: number) => void;
}) => {
  return (
    <div className="setting-control">
      <label htmlFor={label}>{label}</label>
      <div className="slider-container">
        <input
          className="settings-slider"
          name={label}
          type="range"
          value={value}
          min={min}
          max={max}
          step={step}
          onChange={(e) => {
            onChange(parseInt(e.currentTarget.value));
          }}
        ></input>
        {value}
      </div>
    </div>
  );
};

export default CurveControls;
