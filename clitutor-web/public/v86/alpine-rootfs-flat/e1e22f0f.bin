ls -la
cd projects/fleet-monitor
cat README.md
python3 monitor.py --check shore-hq
grep "Failed" /var/log/auth.log
tail -20 /var/log/syslog
ssh student@localhost
cd ~/data
wc -l access_log.csv
cut -d, -f2 access_log.csv | sort | uniq -c | sort -rn
cat fleet_inventory.csv
head -5 access_log.csv
awk -F, '{print $3}' access_log.csv | sort | uniq -c
find ~ -name "*.py"
grep -r "TODO" ~/projects/
vim monitor.py
git log --oneline
make test
cd ~/notes
cat cs3600_midterm_notes.md
curl -s http://localhost/api/status.json | jq .
nmap -sT localhost
ps aux | grep nginx
df -h
free -m
whoami
pwd
ls /var/log/
ip addr show
history
