export PYTHONPATH := src
data:    ; python scripts/make_sample_data.py
test:    ; python -m unittest discover -s tests -v
lint:    ; ruff check .
run-dev: ; python -m insight_hub run --env dev
serve:   ; python -m insight_hub serve
# staging and production are not run locally: they are deployed by .github/workflows/deploy.yml (dev -> staging -> main)
