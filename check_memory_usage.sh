#!/bin/bash
# Memory Usage Diagnostic Script
# Shows exactly where memory is being used on your server

echo "=========================================="
echo "MEMORY USAGE DIAGNOSTIC"
echo "=========================================="
echo ""

# 1. Overall Memory Summary
echo "1. OVERALL MEMORY SUMMARY"
echo "-------------------------"
free -h
echo ""
echo "Explanation:"
echo "  - Total: Total RAM available (961MB on your server)"
echo "  - Used: Memory currently in use"
echo "  - Free: Memory available for new processes"
echo "  - Shared: Memory used by tmpfs (temporary file system)"
echo "  - Buff/cache: Memory used for disk caching (can be freed if needed)"
echo "  - Available: Memory that can be used without swapping"
echo ""

# 2. Top 15 Processes by Memory Usage
echo "2. TOP 15 PROCESSES USING MEMORY"
echo "--------------------------------"
echo "PID       %MEM  RSS(MB)  COMMAND"
ps aux --sort=-%mem | awk 'NR==1 || NR<=16 {printf "%-9s %-5s %-8s %s\n", $2, $4, int($6/1024), $11}' | tail -n 15
echo ""
echo "Explanation:"
echo "  - %MEM: Percentage of total RAM used by this process"
echo "  - RSS(MB): Actual memory used in megabytes"
echo "  - COMMAND: Process name"
echo ""

# 3. Memory by Service
echo "3. MEMORY USAGE BY SERVICE"
echo "--------------------------"

# Gunicorn workers
GUNICORN_MEM=$(ps aux | grep gunicorn | grep -v grep | awk '{sum+=$6} END {print int(sum/1024)}')
GUNICORN_COUNT=$(ps aux | grep gunicorn | grep -v grep | wc -l)
echo "Gunicorn: ${GUNICORN_MEM}MB (${GUNICORN_COUNT} processes)"

# Daphne
DAPHNE_MEM=$(ps aux | grep daphne | grep -v grep | awk '{sum+=$6} END {print int(sum/1024)}')
DAPHNE_COUNT=$(ps aux | grep daphne | grep -v grep | wc -l)
echo "Daphne:   ${DAPHNE_MEM}MB (${DAPHNE_COUNT} processes)"

# Nginx
NGINX_MEM=$(ps aux | grep nginx | grep -v grep | awk '{sum+=$6} END {print int(sum/1024)}')
NGINX_COUNT=$(ps aux | grep nginx | grep -v grep | wc -l)
echo "Nginx:    ${NGINX_MEM}MB (${NGINX_COUNT} processes)"

# Redis
REDIS_MEM=$(ps aux | grep redis | grep -v grep | awk '{sum+=$6} END {print int(sum/1024)}')
REDIS_COUNT=$(ps aux | grep redis | grep -v grep | wc -l)
echo "Redis:    ${REDIS_MEM}MB (${REDIS_COUNT} processes)"

# MySQL/PostgreSQL
MYSQL_MEM=$(ps aux | grep -E 'mysql|postgres' | grep -v grep | awk '{sum+=$6} END {print int(sum/1024)}')
MYSQL_COUNT=$(ps aux | grep -E 'mysql|postgres' | grep -v grep | wc -l)
if [ "$MYSQL_COUNT" -gt 0 ]; then
    echo "Database: ${MYSQL_MEM}MB (${MYSQL_COUNT} processes)"
fi

# System processes
SYSTEM_MEM=$(ps aux | grep -E 'systemd|sshd|cron|rsyslog' | grep -v grep | awk '{sum+=$6} END {print int(sum/1024)}')
echo "System:   ${SYSTEM_MEM}MB (core system processes)"

echo ""
TOTAL_SERVICES=$((GUNICORN_MEM + DAPHNE_MEM + NGINX_MEM + REDIS_MEM + MYSQL_MEM + SYSTEM_MEM))
echo "Total Services: ${TOTAL_SERVICES}MB"
echo ""

# 4. Gunicorn Workers Detail
echo "4. GUNICORN WORKERS DETAIL"
echo "--------------------------"
ps aux | grep gunicorn | grep -v grep | awk '{printf "PID: %-6s  MEM: %-5s  RSS: %-7s  CMD: %s\n", $2, $4"%", int($6/1024)"MB", $11" "$12" "$13}'
echo ""
WORKER_COUNT=$(ps aux | grep 'gunicorn: worker' | grep -v grep | wc -l)
echo "Number of Gunicorn workers: ${WORKER_COUNT}"
echo ""

# 5. Memory Pressure Indicators
echo "5. MEMORY PRESSURE INDICATORS"
echo "------------------------------"

# Check if system is swapping
SWAP_USED=$(free -m | grep Swap | awk '{print $3}')
if [ "$SWAP_USED" -gt 0 ]; then
    echo "⚠️  WARNING: System is using ${SWAP_USED}MB of swap (disk memory)"
    echo "   This makes everything VERY SLOW!"
else
    echo "✓ No swap usage (good)"
fi

# Check available memory
AVAILABLE=$(free -m | grep Mem | awk '{print $7}')
if [ "$AVAILABLE" -lt 100 ]; then
    echo "⚠️  WARNING: Only ${AVAILABLE}MB available memory"
    echo "   System is under memory pressure!"
elif [ "$AVAILABLE" -lt 200 ]; then
    echo "⚠️  CAUTION: Only ${AVAILABLE}MB available memory"
    echo "   Consider reducing workers or upgrading RAM"
else
    echo "✓ ${AVAILABLE}MB available (healthy)"
fi

# Check for OOM killer activity
OOM_COUNT=$(dmesg | grep -i "out of memory" | wc -l)
if [ "$OOM_COUNT" -gt 0 ]; then
    echo "⚠️  WARNING: Out of Memory killer has been triggered ${OOM_COUNT} times"
    echo "   Check: dmesg | grep -i 'out of memory'"
else
    echo "✓ No OOM killer activity"
fi

echo ""

# 6. Recommendations
echo "6. RECOMMENDATIONS"
echo "------------------"

if [ "$WORKER_COUNT" -gt 2 ] && [ "$AVAILABLE" -lt 200 ]; then
    echo "⚠️  You have ${WORKER_COUNT} Gunicorn workers but low memory"
    echo "   RECOMMENDATION: Reduce to 2 workers"
    echo "   Command: sudo nano /etc/systemd/system/gunicorn.service"
    echo "   Change: --workers ${WORKER_COUNT} to --workers 2"
fi

TOTAL_RAM=$(free -m | grep Mem | awk '{print $2}')
if [ "$TOTAL_RAM" -lt 1500 ]; then
    echo ""
    echo "💡 Your server has only ${TOTAL_RAM}MB RAM"
    echo "   For better performance, consider upgrading to 2GB RAM"
fi

if [ "$DAPHNE_MEM" -gt 100 ] && [ "$AVAILABLE" -lt 150 ]; then
    echo ""
    echo "💡 Daphne (WebSocket) is using ${DAPHNE_MEM}MB"
    echo "   If you don't need real-time features, you can disable it:"
    echo "   sudo systemctl stop daphne"
fi

echo ""
echo "=========================================="
echo "DIAGNOSTIC COMPLETE"
echo "=========================================="
