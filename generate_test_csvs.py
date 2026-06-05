## CSV generator for me to test validation
import hashlib, csv, os

def h(v): return hashlib.sha256(v.strip().lower().encode()).hexdigest()

base_row = {
    "em": h("testuser@example.com"),
    "ph": h("27821234567"),
    "fn": h("john"),
    "ln": h("doe"),
    "external_id": "CRM-001",
    "event_name": "QualifiedLead",
    "event_time": "1746000000"
}

files = {
    "realbeds_QualifiedLead_meta_20260526_001.csv": base_row,
    "realbeds_QualifiedLead_googleads_20260526_001.csv": base_row,
}

for fname, row in files.items():
    with open(fname, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=row.keys())
        w.writeheader()
        w.writerow(row)
    print(f"Created: {fname}")

# Bad hash file (unhashed email)
bad_row = {**base_row, "em": "notahash@example.com"}
with open("realbeds_QualifiedLead_meta_20260526_002.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=bad_row.keys())
    w.writeheader()
    w.writerow(bad_row)
print("Created: bad hash test file (002)")
