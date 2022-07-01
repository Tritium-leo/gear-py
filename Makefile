.PHONY:init
init:
	python -m pip install --upgrade pip
	pip install -r ./requirements.txt

.PHONY:dump
dump:
	pip freeze > ./requirements.txt


.PHONY:test
test:
	 export PYTHONPATH=$PYTHONPATH:`pwd` && python ./test_case/run_test.py

