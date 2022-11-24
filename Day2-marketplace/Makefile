# Path to sandbox script
SANDBOX=~/git/algorand/sandbox/sandbox
DRYRUN=app_create.dr
TEAL=approval.teal

CLEAN_TESTS="rm -f tests/*.teal tests/index.js* tests/dryruns/*"

init:
	pip install -r requirements.txt
	cd tests && mkdir -p dryruns && npm i

clean:
	rm -f *.teal
	eval ${CLEAN_TESTS}

teal: 
	python3 contract.py

test:
	eval ${CLEAN_TESTS}
	cd tests && ../contract.py && npx tsc && npx jest

lint:
	black --diff --color contract.py
	cd tests && npx eslint index.ts

fix:
	black contract.py
	cd tests && npx eslint index.ts --fix

debug:
	${SANDBOX} copyTo ./tests/dryruns/${DRYRUN}
	${SANDBOX} copyTo ./tests/${TEAL}
	${SANDBOX} tealdbg debug ${TEAL} -d ${DRYRUN} --listen 0.0.0.0
