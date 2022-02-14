all: update run

run:
	python3 web-interface.py

watch:
	python3 web-interface.py & sass --watch static/custom/sass/:static/custom/css

update:
	# git pull
	supervisorctl restart wiki2print
