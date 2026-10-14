import json
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

with open("frontend/public/data/jobs.json", encoding="utf-8") as f:
    jobs = json.load(f)

TECH_PATTERNS = {
    "Cisco / Switch": r"\bcisco\b|\bswitch\b|\brouter\b",
    "Fortinet / Firewall": r"\bfortinet\b|\bfirewall\b|\btuong lua\b",
    "Windows Server": r"\bwindows server\b|\bactive directory\b",
    "Linux OS": r"\blinux\b|\bubuntu\b|\bcentos\b",
    "VMware / Ao hoa": r"\bvmware\b|\bao hoa\b",
    "Opera PMS": r"\bopera\b|\bpms\b",
    "Micros POS": r"\bmicros\b|\bpos\b",
    "RFID / Smart Ticketing": r"\brfid\b|\bthe tu\b|\bve dien tu\b|\bsoat ve\b",
    "SCADA / DCS": r"\bscada\b|\bdcs\b|\bdieu khien\b",
    "PLC Siemens / Cong nghiep": r"\bplc\b|\bsiemens\b|\bmitsubishi\b",
    "TOS Cang Bien": r"\btos\b|\bterminal operating system\b|\bcang bien\b",
    "EDI Hai Quan": r"\bedi\b|\bhai quan\b",
    "HIS / PACS Y Te": r"\bhis\b|\bpacs\b|\by te\b|\bbenh vien\b",
    "ERP SAP": r"\bsap\b|\berp\b",
    "MES San Xuat": r"\bmes\b|\bday chuyen\b|\bsan xuat\b",
    "Python": r"\bpython\b",
    "FastAPI": r"\bfastapi\b",
    "React.js / Next.js": r"\breact\b|\bnext\.?js\b",
    "TypeScript": r"\btypescript\b",
    "PostgreSQL": r"\bpostgresql\b",
    "SQL Server": r"\bsql server\b|\bsql\b|\bco so du lieu\b",
    "Docker / K8s": r"\bdocker\b|\bkubernetes\b|\bk8s\b",
    "Spring Boot": r"\bspring\b|\bjava\b",
    "DevOps / CI-CD": r"\bdevops\b|\bci\/cd\b",
    "AI / Machine Learning": r"\bai\b|\bmachine learning\b|\bdeep learning\b",
    "An Toan Thong Tin": r"\bsecurity\b|\ban toan thong tin\b|\bbao mat\b",
}

hits = 0
for j in jobs:
    haystack = f"{j['title']} {j.get('description', '')} {j.get('requirements', '')} {j.get('category', '')}".lower()
    matched = [tech for tech, pat in TECH_PATTERNS.items() if re.search(pat, haystack)]
    if matched:
        hits += 1
        print(f"{j['title'][:35]} -> {matched[:3]}")

print(f"\nJobs with matched tech: {hits}/{len(jobs)}")
