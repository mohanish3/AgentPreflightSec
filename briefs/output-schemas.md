# Output Schemas: JSON & SARIF v2.1.0 Specifications

This document defines the schema contracts for **AgentPreflight's** JSON and SARIF (Static Analysis Results Interchange Format) outputs.

---

## 1. JSON Schema Contract

For standard API queries and fast CLI processing, AgentPreflight exports a clean, simplified JSON object:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "AgentPreflightScanResult",
  "type": "object",
  "properties": {
    "scan_id": { "type": "string" },
    "timestamp": { "type": "string", "format": "date-time" },
    "summary": {
      "type": "object",
      "properties": {
        "trust_score": { "type": "integer", "minimum": 0, "maximum": 100 },
        "verdict": { "type": "string", "enum": ["pass", "fail"] },
        "findings_count": {
          "type": "object",
          "properties": {
            "critical": { "type": "integer" },
            "high": { "type": "integer" },
            "medium": { "type": "integer" },
            "low": { "type": "integer" }
          }
        }
      }
    },
    "findings": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "rule_id": { "type": "string" },
          "severity": { "type": "string", "enum": ["critical", "high", "medium", "low"] },
          "category": { "type": "string" },
          "file_path": { "type": "string" },
          "line_number": { "type": "integer" },
          "evidence": { "type": "string" },
          "fix_available": { "type": "boolean" }
        }
      }
    }
  }
}
```

---

## 2. SARIF v2.1.0 Schema Contract

To enable seamless integration with the GitHub Security tab and PR annotations, the scanner implements the official OASIS **SARIF v2.1.0** specification.

```json
{
  "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
  "version": "2.1.0",
  "runs": [
    {
      "tool": {
        "driver": {
          "name": "AgentPreflight",
          "semanticVersion": "1.0.0",
          "rules": [
            {
              "id": "AP-PI-001",
              "name": "ToolDescriptionPromptInjection",
              "shortDescription": { "text": "Adversarial prompt injection in tool description" },
              "defaultConfiguration": { "level": "error" }
            }
          ]
        }
      },
      "results": [
        {
          "ruleId": "AP-PI-001",
          "message": { "text": "The tool description contains system override phrases: 'Ignore previous instructions'." },
          "locations": [
            {
              "physicalLocation": {
                "artifactLocation": { "uri": "mcp.json" },
                "region": {
                  "startLine": 12,
                  "startColumn": 10
                }
              }
            }
          ]
        }
      ]
    }
  ]
}
```
