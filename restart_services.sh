#!/bin/bash
# Quick restart script for when site goes down
# Usage: bash restart_services.sh

echo "Restarting Daphne..."
sudo systemctl restart daphne
sleep 2

echo "Restarting Gunicorn..."
sudo systemctl restart gunicorn
sleep 2

echo "Restarting Nginx..."
sudo systemctl restart nginx

echo "Done! Services restarted."
echo "Check status:"
sudo systemctl status daphne --no-pager -l | head -5
sudo systemctl status gunicorn --no-pager -l | head -5
