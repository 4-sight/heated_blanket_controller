import { useState, useEffect, useCallback } from "preact/hooks";

export type ZoneCurveSettings = {
  A: number;
  B: number;
  C: number;
};

export type CurveData = {
  upper: number;
  lower: number;
  feet_max: number;
  body_max: number;
  feet_curve: ZoneCurveSettings;
  body_curve: ZoneCurveSettings;
};

// const dummyData: CurveData = {
//   upper: 80,
//   lower: -10,
//   feet_max: 140,
//   body_max: 130,
//   feet_curve: {
//     A: 0.38,
//     B: 0.02,
//     C: 250,
//   },
//   body_curve: {
//     A: 0.38,
//     B: 0.02,
//     C: 250,
//   },
// };

const useCurveData = (
  channelIndex: number
): [CurveData | null, (val: Partial<CurveData>) => void] => {
  const [data, setData] = useState<CurveData | null>(null);

  useEffect(() => {
    const fetchLogs = async () => {
      const res = await fetch(`/curve_data/${channelIndex}/`);
      if (!res.ok) {
        return;
      }

      try {
        let _data = await res.json();
        _data = _data as CurveData;
        setData(_data);
      } catch (err) {
        console.error(err);
      }
    };

    fetchLogs();
  }, []);

  const onChange = useCallback(
    (val: Partial<CurveData>) => {
      setData((prevData) => {
        if (prevData == null) return prevData;

        let _data = {
          ...prevData,
          ...val,
        };

        fetch("/api/adjust_safety_range/", {
          method: "POST",
          body: JSON.stringify({ safety_range_settings: _data }),
        });

        return _data;
      });
    },
    [data, setData]
  );

  return [data, onChange];
};

export default useCurveData;
