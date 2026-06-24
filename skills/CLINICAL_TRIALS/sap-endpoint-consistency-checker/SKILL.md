---
name: sap-endpoint-consistency-checker
domain: CLINICAL_TRIALS
version: 1.0.0
surfaces:
- python
- prolog
description: Multi-surface SAP endpoint consistency checker with Python surface for endpoint alignment and Prolog surface
  for registry-protocol rule verification.
compatibility: PYTHON
allowed-tools: '- read

  - write

  - edit

  - bash

  - glob

  - grep

  - codebase_search

  - task

  - sequentialthinking_sequentialthinking

  - webfetch

  - websearch

  - question

  - suggest

  '
---

# Purpose

Validates that a Statistical Analysis Plan's declared primary and secondary endpoints align with trial registry entries and the original protocol, flagging mismatched analysis windows or populations.

# Description

Prolog defines relational consistency rules across endpoint strings, analysis methods, and timepoints. Python loads the SAP, registry, and protocol into predicate form and runs consistency queries. Outputs a list of aligned and conflicting endpoints.

## Python Surface

```python
def build_endpoint_maps(sap, registry, protocol):
    sap_map = {e.get("endpoint_id"): e for e in sap.get("endpoints", []) if e.get("endpoint_id")}
    reg_map = {e.get("endpoint_id"): e for e in registry.get("endpoints", []) if e.get("endpoint_id")}
    proto_map = {e.get("endpoint_id"): e for e in protocol.get("endpoints", []) if e.get("endpoint_id")}
    return sap_map, reg_map, proto_map

def check_endpoint_consistency(sap, registry, protocol):
    sap_map, reg_map, proto_map = build_endpoint_maps(sap, registry, protocol)
    aligned = []
    missing_from_registry = []
    missing_from_protocol = []
    mismatched_metadata = []
    for ep_id, sap_ep in sap_map.items():
        in_reg = ep_id in reg_map
        in_proto = ep_id in proto_map
        if not in_reg:
            missing_from_registry.append(ep_id)
        if not in_proto:
            missing_from_protocol.append(ep_id)
        if in_reg and in_proto:
            reg_ep = reg_map[ep_id]
            proto_ep = proto_map[ep_id]
            timepoint_match = sap_ep.get("timepoint") == reg_ep.get("timepoint")
            method_match = sap_ep.get("analysis_method") == proto_ep.get("analysis_method")
            if timepoint_match and method_match:
                aligned.append(ep_id)
            else:
                mismatched_metadata.append({
                    "endpoint_id": ep_id,
                    "issues": {
                        "timepoint_mismatch": not timepoint_match,
                        "method_mismatch": not method_match,
                    },
                })
    return {
        "status": "ok",
        "aligned": aligned,
        "missing_from_registry": missing_from_registry,
        "missing_from_protocol": missing_from_protocol,
        "mismatched_metadata": mismatched_metadata,
    }

def main(skill_input):
    sap = skill_input.get("sap", {})
    registry = skill_input.get("registry", {})
    protocol = skill_input.get("protocol", {})
    return check_endpoint_consistency(sap, registry, protocol)
```

## Prolog Surface

```prolog
endpoint(sap, EndpointID, Name, Method, Timepoint) :-
    sap_endpoint(EndpointID, Name, Method, Timepoint).

endpoint(registry, EndpointID, Name, Timepoint) :-
    registry_endpoint(EndpointID, Name, Timepoint).

endpoint(protocol, EndpointID, Name, Method) :-
    protocol_endpoint(EndpointID, Name, Method).

aligned_endpoint(EndpointID, Name) :-
    endpoint(sap, EndpointID, Name, _, _),
    endpoint(registry, EndpointID, Name, _),
    endpoint(protocol, EndpointID, Name, _).

missing_from_registry(EndpointID) :-
    endpoint(sap, EndpointID, _, _, _),
    \+ endpoint(registry, EndpointID, _, _).

missing_from_protocol(EndpointID) :-
    endpoint(sap, EndpointID, _, _, _),
    \+ endpoint(protocol, EndpointID, _, _).

sap_endpoint(ep01, "Progression-Free Survival", "Kaplan-Meier", "Cycle 28").
sap_endpoint(ep02, "Objective Response Rate", "Cochran-Mantel-Haenszel", "Cycle 18").

registry_endpoint(ep01, "Progression-Free Survival", "Cycle 28").
registry_endpoint(ep02, "Objective Response Rate", "Cycle 18").

protocol_endpoint(ep01, "Progression-Free Survival", "Kaplan-Meier").
protocol_endpoint(ep02, "Objective Response Rate", "Cochran-Mantel-Haenszel").
```

## Examples

 ```python
input_data = {
    "ae_record": {"lab_name": "Hemoglobin", "observed_value": 7.2},
    "ae_records": [
        {"lab_name": "Hemoglobin", "observed_value": 7.2},
        {"lab_name": "Hemoglobin", "observed_value": 5.0},
    ],
    "grade_rules": [
        {"lab_name": "Hemoglobin", "grade": 1, "grade_low": 10.0, "grade_high": 9.5},
        {"lab_name": "Hemoglobin", "grade": 2, "grade_low": 9.4, "grade_high": 8.0},
        {"lab_name": "Hemoglobin", "grade": 3, "grade_low": 7.9, "grade_high": 6.5},
        {"lab_name": "Hemoglobin", "grade": 4, "grade_low": 0.0, "grade_high": 6.4},
    ],
}
# Expected: {"grade": 4, "pathway": [...], "contradictions": []}
```
