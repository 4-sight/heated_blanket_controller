import { useState, useEffect, useCallback } from "preact/hooks";

const useLoggingLevel = (): [number | null, (val: number) => void] => {
  const [level, setLevel] = useState<number | null>(null);

  useEffect(() => {
    const fetchLevel = async () => {
      const res = await fetch(`/logging_level`);
      if (!res.ok) {
        return;
      }

      try {
        let { level: _level } = await res.json();
        setLevel(_level);
      } catch (err) {
        console.error(err);
      }
    };

    fetchLevel();
  }, []);

  const onChange = useCallback((val: number) => {
    setLevel(val);
    fetch("/api/set_logging_level/", {
      method: "POST",
      body: JSON.stringify({ log_level: val }),
    });
  }, []);

  return [level, onChange];
};

export default useLoggingLevel;
