docker build --platform linux/amd64 . -t factoriotest  --build-arg VERSION=1.1.91 --build-arg SHA256=2288b21afb1d96aa06712a2ae2e31b9c45f0aa4a2e9dec041125d874f0781f6d -f docker/Dockerfile
