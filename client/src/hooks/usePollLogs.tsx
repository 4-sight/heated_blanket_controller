import { useEffect, useState } from "preact/hooks";

export interface Log {
  t: number;
  r: {
    start: number;
    stop: number;
  };
  sv: number;
  f: number;
  b: number;
}

export type Logs = {
  channel1: Log[];
  channel2: Log[];
};

const usePollLogs = () => {
  const [logs, setLogs] = useState<Logs>({
    channel1: [],
    channel2: [],
  });

  useEffect(() => {
    const fetchLogs = async () => {
      const res = await fetch("/drain_logs/");
      if (!res.ok) {
        return logs;
      }

      try {
        let data = await res.json();
        data = data as { channel_1: Log[]; channel_2: Log };

        setLogs((prevLogs) => ({
          channel1: [...prevLogs.channel1, ...data.channel_1],
          channel2: [...prevLogs.channel2, ...data.channel_2],
        }));
      } catch (err) {
        console.error(err);
      }
    };

    fetchLogs();
    const interval = setInterval(fetchLogs, 5000);

    return () => {
      clearInterval(interval);
    };
  }, []);

  return logs;
};

export default usePollLogs;
