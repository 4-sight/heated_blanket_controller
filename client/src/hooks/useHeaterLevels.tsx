import { useState, useEffect, useCallback } from "preact/hooks";

export type HeaterLevels = {
  c1: ZoneLevels;
  c2: ZoneLevels;
};

export type ZoneLevels = {
  f: number;
  b: number;
};

export type UpdateHeaterLevels = {
  c1?: Partial<ZoneLevels>;
  c2?: Partial<ZoneLevels>;
};

const dummyData: HeaterLevels = {
  c1: {
    f: 0,
    b: 3,
  },
  c2: {
    f: 6,
    b: 9,
  },
};

const useHeaterLevels = (): [
  HeaterLevels | null,
  (val: UpdateHeaterLevels) => void
] => {
  const [levels, setLevels] = useState<HeaterLevels | null>(dummyData);

  useEffect(() => {
    const fetchLevels = async () => {
      const res = await fetch(`/heater_levels`);
      if (!res.ok) {
        return;
      }

      try {
        let _levels = await res.json();
        _levels = _levels as HeaterLevels;
        setLevels(_levels);
      } catch (err) {
        console.error(err);
      }
    };

    fetchLevels();
  }, []);

  const onChange = useCallback(
    (val: UpdateHeaterLevels) => {
      setLevels((prevLevels) => {
        if (prevLevels == null) return prevLevels;

        let _levels = {
          ...prevLevels,
        };

        if (val.c1?.f != undefined) {
          _levels.c1.f = val.c1.f;
        }
        if (val.c1?.b != undefined) {
          _levels.c1.b = val.c1.b;
        }
        if (val.c2?.f != undefined) {
          _levels.c2.f = val.c2.f;
        }
        if (val.c2?.b != undefined) {
          _levels.c2.b = val.c2.b;
        }

        fetch("/api/set_heater_levels/", {
          method: "POST",
          body: JSON.stringify({ heater_levels: val }),
        });

        return _levels;
      });
    },
    [levels, setLevels]
  );

  return [levels, onChange];
};

export default useHeaterLevels;
