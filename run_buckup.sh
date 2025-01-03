#!/bin/zsh

PYTHON_SCRIPT="./backup_screentime.py"
LOG_FILE="./log/backup.log"

# 実行!
python3 "$PYTHON_SCRIPT" >> "$LOG_FILE" 2>&1

echo "$(date) - Backup script executed." >> "$LOG_FILE"
