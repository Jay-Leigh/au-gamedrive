import hashlib
import re
import csv

RAW_FILE    = "Realbedstest.csv"
HASHED_FILE = "audiences_realbeds_QualifiedLead_test_20260605_001.csv"

COLUMN_MAP = {
    "LeadCustomer_Name":    "hashed_name",
    "LeadCustomer_SurName": "hashed_surname",
    "Lead_Email":           "hashed_email",
    "Lead_CellNumber":      "hashed_cell_number",
}

def meta_hash_email(val):
    return hashlib.sha256(str(val).strip().lower().encode()).hexdigest()

def meta_hash_name(val):
    cleaned = re.sub(r'[^a-z]', '', str(val).strip().lower())
    return hashlib.sha256(cleaned.encode()).hexdigest()

def meta_hash_phone(val):
    digits = re.sub(r'[^0-9]', '', str(val).strip())
    return hashlib.sha256(digits.encode()).hexdigest()

HASH_FN = {
    "LeadCustomer_Name":    meta_hash_name,
    "LeadCustomer_SurName": meta_hash_name,
    "Lead_Email":           meta_hash_email,
    "Lead_CellNumber":      meta_hash_phone,
}

def read_csv(path):
    with open(path, newline='', encoding='utf-8-sig') as f:
        return list(csv.DictReader(f))

def run():
    raw_rows    = [r for r in read_csv(RAW_FILE) if r.get("PK_Lead_ID", "").strip()]
    hashed_rows = [r for r in read_csv(HASHED_FILE) if r.get("hashed_email", "").strip()]

    print(f"Raw rows: {len(raw_rows)} | Hashed rows: {len(hashed_rows)}\n")

    for i, (raw, hashed) in enumerate(zip(raw_rows, hashed_rows)):
        print(f"--- Row {i+1} | PK_Lead_ID: {raw.get('PK_Lead_ID', '?')} ---")
        all_pass = True

        for raw_col, hashed_col in COLUMN_MAP.items():
            raw_val      = raw.get(raw_col, "")
            computed     = HASH_FN[raw_col](raw_val)
            expected     = hashed.get(hashed_col, "")
            match        = computed == expected
            if not match:
                all_pass = False

            status = "✅" if match else "❌"
            print(f"  {status} {raw_col}")
            print(f"       raw      : '{raw_val}'")
            if not match:
                print(f"       computed : {computed}")
                print(f"       expected : {expected}")

        if all_pass:
            print("  All fields matched.")
        print()

if __name__ == "__main__":
    run()