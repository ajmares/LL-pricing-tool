#!/usr/bin/env python3

import json
import sys
import csv
from typing import List, Dict, Tuple
from dataclasses import dataclass
from pathlib import Path
from collections import defaultdict
import re

@dataclass
class Assay:
    name: str
    price: float
    turnaround_time: str
    analytes: List[str] = None

class AssayPricer:
    def __init__(self, library_path: str = "assay_library.json"):
        self.library_path = library_path
        self.available_assays = self._load_library()
        self.analyte_to_assay_map = self._create_analyte_map()

    def _normalize(self, s: str) -> str:
        # Remove parentheses and their contents, then normalize
        s = re.sub(r'\([^)]*\)', '', s)
        # Remove trailing 's' from each word, keep spaces for mapping
        return ' '.join(word.rstrip('s') for word in s.lower().split())

    def _load_library(self) -> Dict[str, Assay]:
        with open(self.library_path, 'r') as f:
            data = json.load(f)
        return {
            self._normalize(assay['name']): Assay(
                name=assay['name'],
                price=assay['price'],
                turnaround_time=assay['turnaround_time'],
                analytes=assay.get('analytes', [])
            )
            for assay in data['assays']
        }

    def _create_analyte_map(self) -> Dict[str, str]:
        analyte_map = {}
        for assay_name, assay in self.available_assays.items():
            # Add the main assay name
            analyte_map[self._normalize(assay.name)] = assay.name
            
            # Extract alternative names from parentheses
            alt_names = re.findall(r'\((.*?)\)', assay.name)
            for alt_name in alt_names:
                analyte_map[self._normalize(alt_name)] = assay.name
            
            # Add any analytes
            if assay.analytes:
                for analyte in assay.analytes:
                    analyte_map[self._normalize(analyte)] = assay.name
        return analyte_map

    def process_request(self, requested_items: List[str]) -> Tuple[List[Dict], List[str], float]:
        available = []
        unavailable = []
        total_cost = 0.0
        processed_assays = set()

        for item in requested_items:
            norm_item = self._normalize(item)
            # Vitamin group matching
            if norm_item.startswith('vitamin') and len(norm_item) > 7:
                # e.g., 'vitaminb', 'vitaminc', 'vitamina', etc.
                vitamin_group = item.strip().lower()
                found = False
                for assay in self.available_assays.values():
                    if vitamin_group in assay.name.lower() and self._normalize(assay.name) not in processed_assays:
                        available.append({
                            'name': assay.name,
                            'price': assay.price,
                            'turnaround_time': assay.turnaround_time
                        })
                        total_cost += assay.price
                        processed_assays.add(self._normalize(assay.name))
                        found = True
                if found:
                    continue  # Skip to next item if vitamin group match found
            # Check if it's an assay name
            if norm_item in self.available_assays and norm_item not in processed_assays:
                assay_data = self.available_assays[norm_item]
                available.append({
                    'name': assay_data.name,
                    'price': assay_data.price,
                    'turnaround_time': assay_data.turnaround_time
                })
                total_cost += assay_data.price
                processed_assays.add(norm_item)
            # Check if it's an analyte
            elif norm_item in self.analyte_to_assay_map:
                assay_name = self.analyte_to_assay_map[norm_item]
                norm_assay_name = self._normalize(assay_name)
                if norm_assay_name not in processed_assays:
                    assay_data = self.available_assays[norm_assay_name]
                    available.append({
                        'name': f"{assay_data.name} ({item})",
                        'price': assay_data.price,
                        'turnaround_time': assay_data.turnaround_time
                    })
                    total_cost += assay_data.price
                    processed_assays.add(norm_assay_name)
            else:
                unavailable.append(item)

        return available, unavailable, total_cost

    def format_output(self, available: List[Dict], unavailable: List[str], total_cost: float) -> str:
        output = []
        output.append("TESTS WE CAN DO:")
        if available:
            for assay in available:
                output.append(f"\n{assay['name']}")
                output.append(f"Price: ${assay['price']:.2f}")
                output.append(f"TAT: {assay['turnaround_time']}")
        else:
            output.append("\nNo tests available from our lab for your request.")
        output.append("\nTESTS TO CHECK WITH PARTNER LABS:")
        if unavailable:
            for item in unavailable:
                output.append(f"- {item}")
        else:
            output.append("None - we can handle all requested tests")
        if available:
            output.append(f"\nTOTAL COST: ${total_cost:.2f}")
        return "\n".join(output)

def main():
    if len(sys.argv) < 2:
        print("Usage: python assay_pricer.py <test1> <test2> ...")
        sys.exit(1)
    
    requested_items = sys.argv[1:]
    pricer = AssayPricer()
    available, unavailable, total_cost = pricer.process_request(requested_items)
    print(pricer.format_output(available, unavailable, total_cost))

if __name__ == "__main__":
    main() 