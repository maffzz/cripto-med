#!/usr/bin/env python3
"""
Analizador y agregador de reportes de escaneo de seguridad (Fase 2 - Paso 2.1).
Procesa los JSON generados en reports/<before|after>/ y genera la tabla de hallazgos por herramienta y severidad.
"""

import sys
import os
import json
from pathlib import Path
from collections import defaultdict

def safe_load_json(path: Path):
    if not path.exists():
        return None
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read().strip()
            if not content:
                return None
            return json.loads(content)
    except Exception as e:
        return None

def analyze_reports(target_dir: Path):
    summary = {}

    # 1. Bandit
    bandit_data = safe_load_json(target_dir / "bandit.json")
    if bandit_data and "results" in bandit_data:
        counts = defaultdict(int)
        for issue in bandit_data.get("results", []):
            sev = issue.get("issue_severity", "LOW").upper()
            counts[sev] += 1
        summary["Bandit (SAST Python)"] = {
            "Alta": counts.get("HIGH", 0),
            "Media": counts.get("MEDIUM", 0),
            "Baja/Info": counts.get("LOW", 0),
            "Total": len(bandit_data.get("results", []))
        }
    else:
        summary["Bandit (SAST Python)"] = {"Alta": 0, "Media": 0, "Baja/Info": 0, "Total": 0}

    # 2. pip-audit
    pip_data = safe_load_json(target_dir / "pip-audit.json")
    if pip_data:
        counts = defaultdict(int)
        total_vulns = 0
        deps = pip_data.get("dependencies", []) if isinstance(pip_data, dict) else pip_data
        for dep in deps:
            for vuln in dep.get("vulns", []):
                total_vulns += 1
                counts["Media"] += 1  # Por defecto clasificado como medio si no trae CVSS
        summary["pip-audit (Dependencias Python)"] = {
            "Alta": counts.get("Alta", 0),
            "Media": total_vulns,
            "Baja/Info": 0,
            "Total": total_vulns
        }
    else:
        summary["pip-audit (Dependencias Python)"] = {"Alta": 0, "Media": 0, "Baja/Info": 0, "Total": 0}

    # 3. npm audit
    npm_data = safe_load_json(target_dir / "npm-audit.json")
    if npm_data and "metadata" in npm_data:
        vulns = npm_data.get("metadata", {}).get("vulnerabilities", {})
        alta = vulns.get("critical", 0) + vulns.get("high", 0)
        media = vulns.get("moderate", 0)
        baja = vulns.get("low", 0) + vulns.get("info", 0)
        total = vulns.get("total", alta + media + baja)
        summary["npm audit (Dependencias Frontend)"] = {
            "Alta": alta,
            "Media": media,
            "Baja/Info": baja,
            "Total": total
        }
    else:
        summary["npm audit (Dependencias Frontend)"] = {"Alta": 0, "Media": 0, "Baja/Info": 0, "Total": 0}

    # 4. Gitleaks
    gitleaks_data = safe_load_json(target_dir / "gitleaks.json")
    if isinstance(gitleaks_data, list):
        total_leaks = len(gitleaks_data)
        summary["Gitleaks (Secretos en Repo/Historial)"] = {
            "Alta": total_leaks,
            "Media": 0,
            "Baja/Info": 0,
            "Total": total_leaks
        }
    else:
        summary["Gitleaks (Secretos en Repo/Historial)"] = {"Alta": 0, "Media": 0, "Baja/Info": 0, "Total": 0}

    # 5. Hadolint
    hadolint_data = safe_load_json(target_dir / "hadolint.json")
    if isinstance(hadolint_data, list):
        counts = defaultdict(int)
        for h in hadolint_data:
            lvl = h.get("level", "info").lower()
            if lvl == "error":
                counts["Alta"] += 1
            elif lvl == "warning":
                counts["Media"] += 1
            else:
                counts["Baja/Info"] += 1
        summary["Hadolint (Dockerfiles)"] = {
            "Alta": counts.get("Alta", 0),
            "Media": counts.get("Media", 0),
            "Baja/Info": counts.get("Baja/Info", 0),
            "Total": len(hadolint_data)
        }
    else:
        summary["Hadolint (Dockerfiles)"] = {"Alta": 0, "Media": 0, "Baja/Info": 0, "Total": 0}

    # 6. Trivy (FS + Images)
    trivy_files = ["trivy-fs.json", "trivy-backend.json", "trivy-edge.json"]
    trivy_alta = 0
    trivy_media = 0
    trivy_baja = 0
    trivy_total = 0
    for tf in trivy_files:
        tdata = safe_load_json(target_dir / tf)
        if tdata and "Results" in tdata:
            for res in tdata.get("Results", []):
                for v in res.get("Vulnerabilities", []):
                    sev = v.get("Severity", "LOW").upper()
                    trivy_total += 1
                    if sev in ["CRITICAL", "HIGH"]:
                        trivy_alta += 1
                    elif sev == "MEDIUM":
                        trivy_media += 1
                    else:
                        trivy_baja += 1
    summary["Trivy (FS e Imágenes Docker)"] = {
        "Alta": trivy_alta,
        "Media": trivy_media,
        "Baja/Info": trivy_baja,
        "Total": trivy_total
    }

    # 7. testssl.sh
    testssl_data = safe_load_json(target_dir / "testssl.json")
    ssl_alta = 0
    ssl_media = 0
    ssl_baja = 0
    ssl_total = 0
    if isinstance(testssl_data, list):
        for item in testssl_data:
            sev = item.get("severity", "").upper()
            if "CRITICAL" in sev or "HIGH" in sev:
                ssl_alta += 1
                ssl_total += 1
            elif "MEDIUM" in sev or "WARN" in sev:
                ssl_media += 1
                ssl_total += 1
            elif "LOW" in sev or "INFO" in sev:
                ssl_baja += 1
                ssl_total += 1
    summary["testssl.sh (Configuración TLS 1.3)"] = {
        "Alta": ssl_alta,
        "Media": ssl_media,
        "Baja/Info": ssl_baja,
        "Total": ssl_total
    }

    # 8. OWASP ZAP (Baseline + API)
    zap_files = ["zap-baseline.json", "zap-api.json"]
    zap_alta = 0
    zap_media = 0
    zap_baja = 0
    zap_total = 0
    for zf in zap_files:
        zdata = safe_load_json(target_dir / zf)
        if zdata and "site" in zdata:
            for s in zdata.get("site", []):
                for a in s.get("alerts", []):
                    risk = str(a.get("riskcode", "0"))
                    zap_total += 1
                    if risk == "3":
                        zap_alta += 1
                    elif risk == "2":
                        zap_media += 1
                    else:
                        zap_baja += 1
    summary["OWASP ZAP (DAST Baseline y API)"] = {
        "Alta": zap_alta,
        "Media": zap_media,
        "Baja/Info": zap_baja,
        "Total": zap_total
    }

    # Imprimir Tabla Markdown
    print("\n" + "="*80)
    print(f" RESUMEN DE HALLAZGOS DE SEGURIDAD - FASE 2 ({target_dir.name.upper()})")
    print("="*80)
    print("| Herramienta | Alta / Crítica | Media | Baja / Info | Total Hallazgos |")
    print("|---|:---:|:---:|:---:|:---:|")
    
    tot_a, tot_m, tot_b, tot_t = 0, 0, 0, 0
    for tool, counts in summary.items():
        print(f"| {tool} | {counts['Alta']} | {counts['Media']} | {counts['Baja/Info']} | **{counts['Total']}** |")
        tot_a += counts["Alta"]
        tot_m += counts["Media"]
        tot_b += counts["Baja/Info"]
        tot_t += counts["Total"]
    
    print("|---|:---:|:---:|:---:|:---:|")
    print(f"| **TOTAL CONSOLIDADO** | **{tot_a}** | **{tot_m}** | **{tot_b}** | **{tot_t}** |")
    print("="*80 + "\n")

    return summary

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "before"
    target_path = Path("reports") / target
    if not target_path.exists():
        target_path.mkdir(parents=True, exist_ok=True)
    analyze_reports(target_path)
