import pandas as pd
import jsonlines
import os

# Paths
csv_path = os.path.join(os.path.dirname(__file__), '../data/GPT-4.1_Concordance_Eval_Saloni.csv')
jsonl_path = os.path.join(os.path.dirname(__file__), '../test_results_gpt4.1/final_output.jsonl')
jsonl_out_path = jsonl_path  # Overwrite in place; change if you want to keep original

# Read CSV and build a mapping from dav_id to Concordance
csv_df = pd.read_csv(csv_path, encoding='utf-8')
# Some CSVs may have whitespace or int dav_id, so normalize to str
csv_df['dav_id'] = csv_df['dav_id'].astype(str).str.strip()
concordance_map = dict(zip(csv_df['dav_id'], csv_df['Concordance']))

# Read JSONL
entries = []
with jsonlines.open(jsonl_path, 'r') as reader:
    for obj in reader:
        dav_id = str(obj.get('dav_id')).strip()
        # Add Concordance if available
        if dav_id in concordance_map:
            obj['Concordance'] = concordance_map[dav_id]
        else:
            obj['Concordance'] = None  # Or leave out, or log missing
        entries.append(obj)

# Write back to JSONL (overwrite)
with jsonlines.open(jsonl_out_path, 'w') as writer:
    writer.write_all(entries)

print(f"Updated {len(entries)} entries in {jsonl_out_path} with Concordance values from {csv_path}.") 