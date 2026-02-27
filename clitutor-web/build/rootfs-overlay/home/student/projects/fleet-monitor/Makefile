.PHONY: test check clean help

help:
	@echo "Usage:"
	@echo "  make check    - Run health check on all hosts"
	@echo "  make test     - Run unit tests"
	@echo "  make logs     - Parse auth logs for suspicious activity"
	@echo "  make clean    - Remove cached files"

check:
	python3 monitor.py --check-all

test:
	python3 -m pytest tests/ -v

logs:
	python3 parse_logs.py /var/log/auth.log

clean:
	find . -name '__pycache__' -type d -exec rm -rf {} + 2>/dev/null; true
	find . -name '*.pyc' -delete 2>/dev/null; true
