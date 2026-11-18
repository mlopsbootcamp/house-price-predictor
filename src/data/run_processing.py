# src/data/run_processing.py
import argparse
from processor import process_data

def main():
    parser = argparse.ArgumentParser(description='Process housing data.')
    parser.add_argument('--input', required=True, help='Path to input CSV file')
    parser.add_argument('--output', required=True, help='Path for output CSV file')
    
    args = parser.parse_args()
    
    process_data(args.input, args.output)
    print("Data processing completed successfully!")

if __name__ == "__main__":
    main()
