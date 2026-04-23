from prometheus_client import Counter, Histogram, Gauge

NODES_TOTAL = Gauge(
    "controlplane_nodes_total",
    "Number of nodes by state and region",
    ["state", "region"],
)

STATE_TRANSITIONS = Counter(
    "controlplane_state_transitions_total",
    "Number of state transitions",
    ["from_state", "to_state"],
)

PROVISIONING_DURATION = Histogram(
    "controlplane_provisioning_duration_seconds",
    "Time to provision a node",
    ["region"],
    buckets=[1, 5, 15, 30, 60, 120, 300],
)

RECONCILER_RUNS = Counter(
    "controlplane_reconciler_runs_total",
    "Number of reconciler loop iterations",
)

RECONCILER_DRIFT = Counter(
    "controlplane_reconciler_drift_total",
    "Number of drift corrections performed",
    ["state"],
)
