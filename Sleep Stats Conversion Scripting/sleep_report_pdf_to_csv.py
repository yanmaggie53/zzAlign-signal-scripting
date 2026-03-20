import pdfplumber
import re
import csv
import sys

def extract_sleep_data(pdf_path):
    data = {}
    
    with pdfplumber.open(pdf_path) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    
    # Define patterns for each field
    patterns = {
        'AHI/hr': r'AHI[^0-9]*(\d+\.?\d*)',
        'ODI/hr': r'ODI[^0-9]*(\d+\.?\d*)',
        'Sleep time (h)': r'Sleep\s*time[^0-9]*(\d+\.?\d*)',
        'Supine (%)': r'Supine[^0-9]*(\d+\.?\d*)',
        'number of awakenings': r'awakenings[^0-9]*(\d+)',
        'mean SPO2': r'mean\s*SPO2[^0-9]*(\d+\.?\d*)',
        'NADIR SPO2': r'NADIR\s*SPO2[^0-9]*(\d+\.?\d*)',
        'number of apneas per hour': r'apneas\s*per\s*hour[^0-9]*(\d+\.?\d*)'
    }
    
    for key, pattern in patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            data[key] = match.group(1)
        else:
            data[key] = 'N/A'
    
    return data

def main():
    if len(sys.argv) != 3:
        print("Usage: python sleep_report_pdf_to_csv.py <input_pdf> <output_csv>")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    csv_path = sys.argv[2]
    
    data = extract_sleep_data(pdf_path)
    
    with open(csv_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(data.keys())
        writer.writerow(data.values())
    
    print(f"Data extracted and saved to {csv_path}")

if __name__ == "__main__":
    main()