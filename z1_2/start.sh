#!/bin/bash

# building and running Python containers
build_py_server() {
    docker build -t z40_server_py -f server_py/dockerfile .
}

build_py_client() {
    docker build -t z40_client_py -f client_py/dockerfile .
}

build_py() {
    build_py_server
    build_py_client
}

run_py_server() {
    docker run -dit --network z40_network --network-alias z40_server_py_container --name z40_server_py_container z40_server_py:latest
}

run_py_client() {
    # Use provided parameters if available, otherwise default
    server_name=${1:-z40_server_py_container}
    server_port=${2:-8000}
    client_param=${3:-1000}

    docker run -dit --network z40_network --network-alias z40_client_py_container --name z40_client_py_container z40_client_py:latest "$server_name" "$server_port" "$client_param"
}

run_py() {
    run_py_server
    run_py_client "$1" "$2" "$3"
}

# clean up containers and images
clean() {
    docker kill z40_server_py_container z40_client_py_container || true
    docker rm -f z40_server_py_container z40_client_py_container || true
    docker rmi z40_server_py z40_client_py || true
}

# script
case "$1" in
    py)
        clean
        build_py
        run_py "${@:2}"
        ;;
    build-py)
        build_py
        ;;
    run-py)
        run_py "${@:2}"
        ;;
    clean)
        clean
        ;;
    *)
        echo "Usage: $0 {py|build-py|run-py|clean} [server_name] [server_port] [client_param]"
        exit 1
        ;;
esac