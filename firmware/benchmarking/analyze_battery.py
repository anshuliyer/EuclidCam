import os
import glob
import csv

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # The benchmark CSVs are generated in the firmware/python directory by main.py
    python_dir = os.path.abspath(os.path.join(script_dir, "..", "python"))
    
    csv_files = glob.glob(os.path.join(python_dir, "battery_benchmark_*.csv"))
    
    if not csv_files:
        print(f"No benchmark CSV files found in {python_dir}")
        return
        
    combined_data = []
    total_max_uptime = 0
    
    print("🔋 Battery Benchmark Analysis\n" + "="*40)
    
    for file in sorted(csv_files):
        max_uptime = 0
        run_name = os.path.basename(file).replace("battery_benchmark_", "").replace(".csv", "")
        
        with open(file, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            if rows:
                for row in rows:
                    try:
                        uptime_str = row.get('Uptime_Seconds')
                        if not uptime_str:
                            continue
                        uptime = int(uptime_str)
                        if uptime > max_uptime:
                            max_uptime = uptime
                        
                        # Add a column for the run name to distinguish in combined CSV
                        row['Run_ID'] = run_name
                        combined_data.append(row)
                    except (ValueError, TypeError):
                        pass
                        
        if max_uptime > total_max_uptime:
            total_max_uptime = max_uptime
            
        hours = max_uptime // 3600
        minutes = (max_uptime % 3600) // 60
        seconds = max_uptime % 60
        print(f"Run {run_name}: Battery ran for {hours}h {minutes}m {seconds}s ({max_uptime} sec)")
        
    # Write combined CSV
    if combined_data:
        combined_path = os.path.join(script_dir, "combined_benchmark.csv")
        fieldnames = ['Run_ID', 'Timestamp', 'Uptime_Seconds', 'Throttled_State']
        
        with open(combined_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for row in combined_data:
                # Only write fields we care about, ignoring any malformed extra fields
                writer.writerow({k: row.get(k, '') for k in fieldnames})
                
        print("\n" + "="*40)
        
        t_hours = total_max_uptime // 3600
        t_minutes = (total_max_uptime % 3600) // 60
        print(f"🏆 Longest Run: {t_hours}h {t_minutes}m")
        print(f"✅ Combined data saved to: {combined_path}")

if __name__ == "__main__":
    main()
