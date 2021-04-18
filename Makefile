.PHONY: all deps clean prune

venv = . venv/bin/activate

## public

all: deps

deps: venv/bin/activate

venv/bin/activate: Makefile
	@which python3 > /dev/null || { echo "Missing requirement: python3" >&2; exit 1; }
	virtualenv --version > /dev/null || { echo "Missing requirement: virtualenv -- aborting" >&2; exit 1; }
	[ -e venv/bin/python ] || virtualenv -p $$(which python3) venv > /dev/null
	${venv} && pip3 install -r requirements.txt
	touch venv/bin/activate

clean:
	rm -rf __pycache__

prune: clean
	rm -rf venv

test: deps
	${venv} && PYTHONPATH=zabbix-ldap-sync pytest

check: lint type-check
.PHONY: check

lint: deps
	${venv} && python3 -m flake8 zabbix-ldap-sync lib
.PHONY: lint

type-check: deps
	${venv} && python3 -m mypy zabbix-ldap-sync lib
.PHONY: lint

