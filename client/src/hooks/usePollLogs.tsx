import { useCallback, useEffect, useState } from "preact/hooks";

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
  channel_1: ChannelData;
  channel_2: ChannelData;
};

const usePollLogs = () => {
  const [logs, setLogs] = useState<Logs | null>(null);

  const fetchLogs = useCallback(async() => {
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

          let newLogs: Logs = {
            channel_1: {
              exceptions: [
                ...prevLogs.channel_1.exceptions,
                ...data.channel_1.exceptions,
              ],
              ...data.channel_1,
            },
            channel_2: {
              exceptions: [
                ...prevLogs.channel_2.exceptions,
                ...data.channel_2.exceptions,
              ],
              ...data.channel_2,
            },
          };

          return newLogs
        });
      } catch (err) {
        console.error(err);
      }
  }, [setLogs])

  useEffect(() => {
    fetchLogs();
    const interval = setInterval(fetchLogs, 500);

    return () => {
      clearInterval(interval);
    };
  }, [fetchLogs]);

  return logs;
};

export default usePollLogs;
