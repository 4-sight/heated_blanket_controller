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

export type ChannelData = {
  exceptions: Log[];
  exception_count: number;
  min_t: number;
  max_t: number;
  mean_t: number;
};

export type Logs = {
  channel1: ChannelData;
  channel2: ChannelData;
};

const usePollLogs = () => {
  const [logs, setLogs] = useState<Logs | null>(null);

  useEffect(() => {
    const fetchLogs = async () => {
      const res = await fetch("/drain_logs/");
      if (!res.ok) {
        return logs;
      }

      try {
        let data = await res.json();
        data = data as Logs;

        setLogs((prevLogs) => {
          if (prevLogs == null) {
            return data;
          }

          return {
            channel1: {
              exceptions: [
                ...prevLogs.channel1.exceptions,
                ...data.channel_1.exceptions,
              ],
              ...data.channel_1,
            },
            channel2: {
              exceptions: [
                ...prevLogs.channel2.exceptions,
                ...data.channel_2.exceptions,
              ],
              ...data.channel_2,
            },
          };
        });
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
