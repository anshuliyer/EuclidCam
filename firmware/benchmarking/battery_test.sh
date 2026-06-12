#!/bin/bash
# EuclidCam Battery Benchmark Script
# Continuously logs the system uptime and voltage state to a CSV file.
# When the battery dies, the Pi will shut down. You can check the last entry 
# in the CSV file upon reboot to see exactly how long the battery lasted!

LOGFILE="battery_benchmark_$(date +%Y%m%d_%H%M%S).csv"

echo "=========================================="
echo "   EuclidCam Battery Benchmark Tool"
echo "=========================================="
echo "Logging system uptime and voltage state every 60 seconds."
echo "Results will be saved to: $LOGFILE"
echo ""
echo "INSTRUCTIONS: Leave the camera running until the battery completely dies."
echo "Once you recharge and reboot, read the last line of the CSV file to see your total battery life."
echo "Press [Ctrl+C] to stop if needed."
echo "=========================================="

# Write CSV header
echo "Timestamp,Uptime_Seconds,Throttled_State" > "$LOGFILE"

while true; do
    TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")
    # Get raw uptime in seconds from /proc/uptime
    UPTIME=$(awk '{print $1}' /proc/uptime)
    # Check for undervoltage states
    THROTTLED=$(vcgencmd get_throttled | cut -d '=' -f 2)
    
    # Append to logfile
    echo "$TIMESTAMP,$UPTIME,$THROTTLED" >> "$LOGFILE"
    
    # Print to console for active monitoring
    echo "[$TIMESTAMP] Logged -> Uptime: ${UPTIME}s | Throttle Hex: $THROTTLED"
    
    # Wait 60 seconds before next poll
    sleep 60
done
