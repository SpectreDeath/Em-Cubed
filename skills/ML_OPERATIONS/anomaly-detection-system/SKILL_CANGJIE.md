# Anomaly Detection System - Cangjie Edition
# Cangjie-coordinated multi-surface anomaly detection

# Cangjie surface block: orchestrator
func main() {
    // Input: data points, detection parameters
    let anomaly_data = context["anomaly_data"] as AnomalyInput;

    println("Cangjie Anomaly Detector Starting...");

    // 1. Python: Statistical detection (z-score, IQR) + Isolation Forest
    let py_detection = perform EmCubed.call_surface("python", "
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

def detect_anomalies(X, contamination=0.1):
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    iso = IsolationForest(contamination=contamination, random_state=42)
    predictions = iso.fit_predict(X_scaled)  # -1 = anomaly, 1 = normal
    scores = iso.decision_function(X_scaled)
    return {'predictions': predictions.tolist(), 'scores': scores.tolist()}

def statistical_zscore(X, threshold=3.0):
    mean = np.mean(X, axis=0)
    std = np.std(X, axis=0) + 1e-10
    z_scores = np.abs((X - mean) / std)
    return (z_scores > threshold).any(axis=1).tolist()

def statistical_iqr(X, k=1.5):
    q1 = np.percentile(X, 25, axis=0)
    q3 = np.percentile(X, 75, axis=0)
    iqr = q3 - q1
    lower = q1 - k * iqr
    upper = q3 + k * iqr
    return ((X < lower) | (X > upper)).any(axis=1).tolist()

X = ${anomaly_data.data}
contam = ${anomaly_data.contamination}
ml_result = detect_anomalies(X, contam)
zscore_anoms = statistical_zscore(X)
iqr_anoms = statistical_iqr(X)

{'ml_predictions': ml_result['predictions'],
 'ml_scores': ml_result['scores'],
 'zscore': zscore_anoms,
 'iqr': iqr_anoms,
 'n_samples': len(X)}
    ");

    // 2. Prolog: Logical anomaly rules (business constraints, context)
    let prolog_rules = build_anomaly_rules(anomaly_data);
    let prolog_anomalies = perform EmCubed.call_surface("prolog", prolog_rules + "
% Anomaly definition
anomaly(DataPoint, Type) :-
    outside_normal_range(DataPoint, Mean, Std, Threshold),
    classify_anomaly(Type).

% Statistical anomaly
outside_normal_range(Value, Mean, Std, Threshold) :-
    abs(Value - Mean) > (Threshold * Std).

% Pattern anomaly
pattern_anomaly(Sequence, Pattern) :-
    expected_pattern(Sequence, Expected),
    deviation(Sequence, Expected, Deviation),
    Deviation > threshold.

% Business rule anomaly
business_anomaly(Transaction, Violation) :-
    transaction(Transaction),
    violates_rule(Transaction, Violation).

% Context anomaly
contextual_anomaly(DataPoint, Context) :-
    normal_for_context(DataPoint, NormalContext),
    Context \\= NormalContext.

% Check anomalies in provided data
find_anomalies(Data) :-
    findall(DP, anomaly(DP, _), Anomalies),
    length(Anomalies, Count),
    format('Found ~w anomalies~n', [Count]).

% For demo, just assert some facts and query
assert_data :- 
    % (data from Python would be asserted here)
    true.

?- find_anomalies(${json.dumps(py_detection['ml_predictions'])}).
    ");

    // 3. Hy: Fuzzy anomaly scoring and temporal confidence
    let hy_scoring = perform EmCubed.call_surface("hy", "
(defn fuzzy-anomaly-score [ml-score zscore iqr]
  \"Combine anomaly signals using fuzzy logic\"
  (let [ml-signal (if (> ml-score 0) 1.0 0.0)
        z-signal (if zscore 1.0 0.0)
        i-signal (if iqr 1.0 0.0)
        combined (/ (+ ml-signal z-signal i-signal) 3)]
    combined))

(defn temporal-confidence [detections window]
  \"Confidence based on recent consistency\"
  (let [recent (take window detections)
        rate (/ (sum recent) (len recent))]
    rate))

(let [ml-scores ${py_detection['ml_scores']}
      zscore-flags ${py_detection['zscore']}
      iqr-flags ${py_detection['iqr']}
      n ${py_detection['n_samples']}]
  (def scores
    (list-comp (fuzzy-anomaly-score s z i)
               [s ml-scores z zscore-flags i iqr-flags]))
  {:mean_score (mean scores)
   :anomaly_rate (/ (sum (filter (fn [x] (> x 0.5)) scores)) n)
   :temporal_conf (temporal-confidence scores 10)})
    ");

    let hy = hy_scoring.get("value", {});
    return {
        "ml_detections": py_detection.get("ml_predictions", []),
        "statistical_zscore": py_detection.get("zscore", []),
        "statistical_iqr": py_detection.get("iqr", []),
        "combined_score": hy.get("mean_score", 0.0),
        "anomaly_rate": hy.get("anomaly_rate", 0.0),
        "temporal_confidence": hy.get("temporal_conf", 0.0),
        "prolog_anomalies": parse_prolog_anomalies(prolog_anomalies)
    };
}

func build_anomaly_rules(data: AnomalyInput): String {
    let rules = StringBuilder();
    rules.append("% Anomaly rules\n");
    rules.append("anomaly(DP, statistical) :- outlier(DP, _).\n");
    rules.append("anomaly(DP, business) :- violates_business_rule(DP).\n");
    rules.append("\n% Thresholds\n");
    rules.append("threshold(3.0).  % z-score\n");
    return rules.toString();
}

func parse_prolog_anomalies(result: Map): Int32 {
    let status = result.get("status", "error");
    if (status == "ok") {
        // Parse count from output
        return 0;
    }
    return 0;
}

struct AnomalyInput {
    data: List<List<Float64>>;  // 2D array: samples x features
    contamination: Float64;
}
