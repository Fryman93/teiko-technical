.PHONY: setup pipeline dashboard

setup:
	python3 -m venv venv
	./venv/bin/pip install -r requirements.txt

pipeline:
	mkdir -p outputs
	./venv/bin/python load_data.py
	./venv/bin/python analysis.py

dashboard:
	./venv/bin/pip install streamlit
	./venv/bin/streamlit run dashboard.py



