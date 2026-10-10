import os
import sys
from src.pipeline import run_phase0_pipeline

def main():
    fixture_path = "fixtures/seed_data.json"
    config_path = "fixtures/scoring_v1.json"
    db_path = "data/dry_run_test.db"
    report_output_dir = "fixtures"
    
    print("Starting LIDO AI Meditation Music Factory Phase 0 Dry-Run...")
    run_id, csv_p, brief_p, report_p = run_phase0_pipeline(fixture_path, config_path, db_path, report_output_dir)
    print(f"Dry-Run completed successfully!")
    print(f"Run ID: {run_id}")
    print(f"Database: {db_path}")
    print(f"CSV Output: {csv_p}")
    print(f"Brief Output: {brief_p}")
    print(f"Report Output: {report_p}")

if __name__ == "__main__":
    main()
