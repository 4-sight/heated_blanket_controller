import { useCallback, useEffect, useState } from "preact/hooks";

export interface Log {
  t: number;
  sv: number;
  r_start: number;
  r_stop: number;
  f: boolean;
  b: boolean;
  fq: number;
  bq: number
}

export type ChannelData = {
  logs: Log[];
  exception_count: number;
  min_t: number;
  max_t: number;
  mean_t: number;
  count: number;
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
        let _data = data as Logs;

        setLogs((prevLogs) => {
          if (prevLogs == null) {
            return _data;
          }

          let newLogs: Logs = {
            channel_1: {
              ..._data.channel_1,
              logs: [
                ...prevLogs.channel_1.logs,
                ..._data.channel_1.logs,
              ],
            },
            channel_2: {
              ..._data.channel_2,
              logs: [
                ...prevLogs.channel_2.logs,
                ..._data.channel_2.logs,
              ],
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
