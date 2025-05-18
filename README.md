# Assay Pricing Tool

This tool helps determine which assays are available in-house and which need to be sent to partner labs, along with pricing and turnaround time information.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure the assay library:
   - Edit `assay_library.json` to include your available assays
   - Each assay should include: name, price, and turnaround time

## Usage

1. Prepare a list of requested assays in either:
   - A text file (one assay per line)
   - A CSV file (assays in the first column, header row optional)
2. Run the script:
```bash
python assay_pricer.py input_file.txt
# or
python assay_pricer.py input_file.csv
```

## Output

The tool will provide:
- List of available assays with prices and turnaround times
- List of assays that need to be checked with partner labs
- Total cost for available assays
- Summary statistics 