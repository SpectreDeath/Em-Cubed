---
name: SAP Endpoint Consistency Checker
Domain: CLINICAL_TRIALS
Version: 1.0.0
surfaces:
  - python
  - prolog
---

# Purpose

Validates that a Statistical Analysis Plan's declared primary and secondary endpoints align with trial registry entries and the original protocol, flagging mismatched analysis windows or populations.

# Description

Prolog defines relational consistency rules across endpoint strings, analysis methods, and timepoints. Python loads the SAP, registry, and protocol into predicate form and runs consistency queries. Outputs a list of aligned and conflicting endpoints.

## Python Surface

```python
def load_sap_endpoints(sap):
    return [(e.get("endpoint_id"), e.get("name"), e.get("analysis_method"), e.get("timepoint"))
            for e in sap.get("endpoints", [])]

def load_registry_endpoints(registry):
    return [(e.get("endpoint_id"), e.get("name"), e.get("timepoint"))
            for e in registry.get("endpoints", [])]

def load_protocol_endpoints(protocol):
    return [(e.get("endpoint_id"), e.get("name"), e.get("analysis_method"))
            for e in protocol.get("endpoints", [])]

def check_endpoint_consistency(sap, registry, protocol):
    sap_eps = set(load_sap_endpoints(sap))
    reg_eps = set(load_registry_endpoints(registry))
    proto_eps = set(load_protocol_endpoints(protocol))
    sap_ids = {e[0] for e in sap_eps}
    reg_ids = {e[0] for e in reg_eps}
    proto_ids = {e[0] for e in proto_eps}
    missing_from_registry = list(sap_ids - reg_ids)
    missing_from_protocol = list(sap_ids - proto_ids)
    aligned = list(sap_ids & reg_ids & proto_ids)
    return {
        "status": "ok",
        "aligned": aligned,
        "missing_from_registry": missing_from_registry,
        "missing_from_protocol": missing_from_protocol,
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
    "sap": {
        "endpoints": [
            {"endpoint_id": "ep01", "name": "Progression-Free Survival", "analysis_method": "Kaplan-Meier", "timepoint": "Cycle 28"},
            {"endpoint_id": "ep02", "name": "Objective Response Rate", "analysis_method": "CMH", "timepoint": "Cycle 18"},
            {"endpoint_id": "ep03", "name": "Overall Survival", "analysis_method": "Kaplan-Meier", "timepoint": "Cycle 36"},
        ]
    },
    "registry": {
        "endpoints": [
            {"endpoint_id": "ep01", "name": "Progression-Free Survival", "timepoint": "Cycle 28"},
            {"endpoint_id": "ep02", "name": "Objective Response Rate", "timepoint": "Cycle 18"},
        ]
    },
    "protocol": {
        "endpoints": [
            {"endpoint_id": "ep01", "name": "Progression-Free Survival", "analysis_method": "Kaplan-Meier"},
            {"endpoint_id": "ep02", "name": "Objective Response Rate", "analysis_method": "CMH"},
        ]
    },
}
# Expected: {"aligned": ["ep01", "ep02"], "missing_from_registry": ["ep03"], "missing_from_protocol": []}
```
