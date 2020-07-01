PLUGIN_VERSION=1.0.0
PLUGIN_ID=tesseract-ocr

plugin:
	cat plugin.json|json_pp > /dev/null
	rm -rf dist
	mkdir dist
	zip --exclude "*.pyc" --exclude "resource/img-doc/*" -r dist/dss-plugin-${PLUGIN_ID}-${PLUGIN_VERSION}.zip code-env custom-recipes js notebook-templates python-lib resource plugin.json
