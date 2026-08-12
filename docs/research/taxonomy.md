# Cyber-Security Taxonomy

The cyber-security-research corpus is organized along a **20-category × 8-aspect**
matrix (160 cells). Every paper carries exactly one category and one aspect;
every news item in `news.yaml` is tagged with a category for cross-referencing.

## Categories

| # | Category | Focus |
|---|----------|-------|
| 1 | `threat-intelligence` | Threat intelligence collection, sharing (ISACs), TTP modeling, attribution |
| 2 | `vulnerability-management` | Discovery, coordinated disclosure, CVE/CVSS, patch prioritization |
| 3 | `incident-response` | DFIR, playbooks, containment, digital evidence |
| 4 | `malware-analysis` | Static/dynamic analysis, ransomware, ML classification, sandboxing |
| 5 | `network-security` | IDS/IPS, anomaly detection, traffic analysis, DNS security |
| 6 | `application-security` | Secure SDLC, SAST/DAST, web app security, DevSecOps |
| 7 | `cloud-security` | Misconfiguration, containers/K8s, serverless, CSPM |
| 8 | `identity-access` | IAM, MFA/FIDO, SSO, privileged access, identity governance |
| 9 | `cryptography` | Post-quantum, homomorphic, ZK, key management, protocol analysis |
| 10 | `zero-trust` | ZTA/ZTNA, microsegmentation, continuous verification, least privilege |
| 11 | `supply-chain-security` | SBOM, dependency attacks, provenance, reproducible builds |
| 12 | `security-operations` | SOC, SIEM, detection engineering, threat hunting, SOAR |
| 13 | `ai-security` | Adversarial ML, prompt injection, jailbreaks, model poisoning, red-teaming |
| 14 | `security-education` | Cyber education, awareness programs, serious games, workforce skills |
| 15 | `security-compliance` | NIST CSF, ISO 27001, NIS2/CMMC, certification, audit |
| 16 | `risk-management` | Cyber risk quantification, FAIR, cyber insurance |
| 17 | `privacy` | GDPR, PETs, data breach economics, consent, anonymization |
| 18 | `iot-security` | IoT/OT/ICS/SCADA, firmware, embedded security |
| 19 | `human-factor` | Phishing susceptibility, social engineering, user behavior |
| 20 | `cyber-warfare` | Nation-state operations, deterrence, critical-infrastructure attacks |

## Aspects

| Aspect | Meaning |
|--------|---------|
| `theory` | Constructs, frameworks, taxonomies, conceptual models |
| `mechanism` | Causal mechanisms, attack/defense dynamics |
| `method` | Techniques, experiments, empirical studies |
| `application` | Applied settings, deployments, case studies |
| `development` | Tooling, standards, curricula, capability building |
| `systems` | Systems & platform architecture |
| `evaluation` | Measurement, benchmarks, effectiveness, ROI |
| `review` | Surveys, meta-analyses, position papers |

## White Space (post-seed)

| Cell | Papers | Note |
|------|-------:|------|
| `security-operations` / `evaluation` | ~0 | SOC effectiveness measurement is thin |
| `zero-trust` / `development` | ~0 | ZT migration playbooks barely published |
| `security-education` / `evaluation` | ~0 | Training-to-behavior transfer evidence gap (mirrors AI-literacy) |
| `cyber-warfare` / `mechanism` | ~0 | Attribution/deterrence causal evidence scarce |

White-space cells are prime targets for the deep-dives in
[`RESEARCH_PLAN.md`](RESEARCH_PLAN.md) and for the news↔paper bridge: operational
alerts (e.g., CISA advisories) often lead the literature in exactly these cells.
