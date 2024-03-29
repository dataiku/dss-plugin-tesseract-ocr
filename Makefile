# Makefile variables set automatically
plugin_id=`cat plugin.json | python -c "import sys, json; print(str(json.load(sys.stdin)['id']).replace('/',''))"`
plugin_version=`cat plugin.json | python -c "import sys, json; print(str(json.load(sys.stdin)['version']).replace('/',''))"`
archive_file_name="dss-plugin-${plugin_id}-${plugin_version}.zip"
remote_url=`git config --get remote.origin.url`
last_commit_id=`git rev-parse HEAD`


plugin:
	@echo "[START] Archiving plugin to dist/ folder..."
	@cat plugin.json | json_pp > /dev/null
	@rm -rf dist
	@mkdir dist
	@echo "{\"remote_url\":\"${remote_url}\",\"last_commit_id\":\"${last_commit_id}\"}" > release_info.json
	@git archive -v -9 --format zip -o dist/${archive_file_name} HEAD
	@zip -u dist/${archive_file_name} release_info.json
	@rm release_info.json
	@echo "[SUCCESS] Archiving plugin to dist/ folder: Done!"

unit-tests:
	@echo "No unit tests"

integration-tests:
	@echo "Running integration tests..."
	@( \
		rm -rf ./env/; \
		python3 -m venv env/; \
		source env/bin/activate; \
		pip3 install --upgrade pip;\
		pip install --no-cache-dir -r tests/python/integration/requirements.txt; \
		pytest tests/python/integration --alluredir=tests/allure_report || ret=$$?; exit $$ret \
	)

tests: unit-tests integration-tests

dist-clean:
	rm -rf dist