#!/bin/bash

WORK24_LOG_FILE="/home/ubuntu/work24/app.log"

# 랜덤 시간 설정
# sleep $((RANDOM % 120 * 60))
sleep $((RANDOM % 200))
# Python 스크립트 실행 시간 기록
echo "$(date '+%Y-%m-%d %H:%M:%S') - Executing Python script." >> $WORK24_LOG_FILE

# Python 스크립트 실행
echo "======▶️======" >> $WORK24_LOG_FILE
/home/ubuntu/job_crawling/bin/python3 /home/ubuntu/work24/crawling.py >> $WORK24_LOG_FILE 2>&1

# Python 스크립트 실행 완료 기록
echo "$(date '+%Y-%m-%d %H:%M:%S') - Python script execution finished." >> $WORK24_LOG_FILE