import time
from collections import defaultdict, deque
from threading import Lock


class ZScoreService:
    _instance = None

    def __init__(
        self,
        default_baseline_stats=None,
        default_threshold=3,
        aggregation_window=60,
        min_anomalies=3,
        use_ema=False,  # Exponential Moving Average
        ema_alpha=0.3,
        enable_logging=False,
    ):
        """
        Robust ZScoreService singleton.
        use_ema: se True aggiorna media/std con Exponential Moving Average
        ema_alpha: coefficiente alpha per EMA
        enable_logging: stampa messaggi di debug
        """
        if default_baseline_stats is None:
            default_baseline_stats = {
                "function_code": {"mean": 3, "std": 1},
                "data_length": {"mean": 20, "std": 5},
            }

        self.default_baseline_stats = default_baseline_stats
        self.default_threshold = default_threshold
        self.aggregation_window = aggregation_window
        self.min_anomalies = min_anomalies
        self.use_ema = use_ema
        self.ema_alpha = ema_alpha
        self.enable_logging = enable_logging

        self.device_protocol_anomalies = defaultdict(lambda: deque())
        self.device_protocol_baselines = defaultdict(
            lambda: {k: v.copy() for k, v in self.default_baseline_stats.items()}
        )
        self.device_protocol_thresholds = defaultdict(lambda: self.default_threshold)

        self.lock = Lock()

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = ZScoreService()
        return cls._instance

    def log(self, msg):
        if self.enable_logging:
            print(f"[ZScoreService] {msg}")

    def set_baseline(self, device_id, protocol, baseline_stats):
        key = f"{device_id}-{protocol}"
        self.device_protocol_baselines[key] = {
            k: v.copy() for k, v in baseline_stats.items()
        }

    def set_threshold(self, device_id, protocol, threshold):
        key = f"{device_id}-{protocol}"
        self.device_protocol_thresholds[key] = threshold

    def check(self, device_id, protocol, features, update_dynamic=False):
        now = time.time()
        key = f"{device_id}-{protocol}"

        with self.lock:  # thread-safe
            baseline_stats = self.device_protocol_baselines.get(
                key, self.default_baseline_stats
            )
            threshold = self.device_protocol_thresholds.get(key, self.default_threshold)

            triggered_metrics = []

            for metric, value in features.items():
                try:
                    value = float(value)
                except (ValueError, TypeError):
                    self.log(f"Feature '{metric}' non numerica: {value}, ignorata")
                    continue

                stats = baseline_stats.get(metric)
                if stats and stats["std"] > 0:
                    z = (value - stats["mean"]) / stats["std"]
                    if abs(z) > threshold:
                        triggered_metrics.append(f"{metric} Z={z:.2f}")

                    if update_dynamic:
                        if self.use_ema:
                            stats["mean"] = (
                                self.ema_alpha * value
                                + (1 - self.ema_alpha) * stats["mean"]
                            )
                            stats["std"] = max(
                                0.5,
                                self.ema_alpha * abs(value - stats["mean"])
                                + (1 - self.ema_alpha) * stats["std"],
                            )
                        else:
                            new_mean = (stats["mean"] + value) / 2
                            new_std = max(
                                0.5, (stats["std"] + abs(value - new_mean)) / 2
                            )
                            stats["mean"] = new_mean
                            stats["std"] = new_std
                        baseline_stats[metric] = stats

            if update_dynamic:
                self.device_protocol_baselines[key] = baseline_stats

            if not triggered_metrics:
                return False, None

            anomalies = self.device_protocol_anomalies[key]
            anomalies.append(now)
            while anomalies and anomalies[0] < now - self.aggregation_window:
                anomalies.popleft()

            if len(anomalies) >= self.min_anomalies:
                msg = f"Aggregated Z-score anomalies: {triggered_metrics}, count={len(anomalies)}"
                self.log(msg)
                anomalies.clear()
                return True, msg

            return False, None

    # --- Metodi utili extra ---
    def reset_anomalies(self, device_id=None, protocol=None):
        """Reset delle anomalie registrate"""
        with self.lock:
            if device_id and protocol:
                key = f"{device_id}-{protocol}"
                self.device_protocol_anomalies[key].clear()
            else:
                for dq in self.device_protocol_anomalies.values():
                    dq.clear()

    def get_baselines(self, device_id=None, protocol=None):
        """Restituisce le baseline correnti"""
        if device_id and protocol:
            key = f"{device_id}-{protocol}"
            return self.device_protocol_baselines.get(key)
        return dict(self.device_protocol_baselines)
