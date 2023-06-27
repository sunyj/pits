.PHONY: dist clean

.DEFAULT_TARGET = dist

dist:
	python3 -m build --no-isolation --wheel && rm -rf pits.egg-info build

clean:
	rm -rf pits.egg-info dist build
