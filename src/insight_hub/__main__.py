import argparse
import json

ap = argparse.ArgumentParser(prog="insight_hub", description="BDO Insight Hub")
sub = ap.add_subparsers(dest="cmd")
srv = sub.add_parser("serve", help="start the local web app (dev environment only)")
srv.add_argument("--port", type=int, default=None, help="default: port from config/env/dev.json")
run = sub.add_parser("run", help="generate all output files (default); CI uses it for dev, staging and production")
run.add_argument("--env", choices=["dev", "staging", "production"], default=None, help="default: $INSIGHT_HUB_ENV or dev")
ap.add_argument("--env", choices=["dev", "staging", "production"], default=None)
a = ap.parse_args()
if a.cmd == "serve":
    from .server import serve
    serve(a.port)
else:
    from .pipeline import run as run_pipeline
    print(json.dumps(run_pipeline(getattr(a, "env", None)), indent=1))
