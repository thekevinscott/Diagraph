init:
	pip install -r requirements.txt

test:
	nosetests tests

copy_assets:
	cd ../.. && pnpm install --force && cd packages/javascript/visualizer && pnpm build:prod

build_package:
	python3 -m build


build_diagraph:
	make copy_assets
	make build_package
