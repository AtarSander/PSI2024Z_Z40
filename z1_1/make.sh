#!/bin/bash

# Functions for building and running Python containers
build_py() {
    docker build -t z40_server_py -f server_py/dockerfile .
    docker build -t z40_client_py -f client_py/dockerfile .
}

run_py() {
    docker run -dit --network z40_network --network-alias z40_server_py_container --name z40_server_py_container z40_server_py:latest
    docker run -dit --network z40_network --network-alias z40_client_py_container --name z40_client_py_container z40_client_py:latest
}

# Functions for building and running C containers
build_c() {
    docker build -t z40_server_c -f server_c/dockerfile .
    docker build -t z40_client_c -f client_c/dockerfile .
}

run_c() {
    docker run -dit --network z40_network --network-alias z40_server_c_container --name z40_server_c_container z40_server_c:latest
    docker run -dit --network z40_network --network-alias z40_client_c_container --name z40_client_c_container z40_client_c:latest
}

# Function to clean up containers
clean() {
    docker kill z40_server_py_container z40_client_py_container z40_server_c_container z40_client_c_container || true
    docker rm -f z40_server_py_container z40_client_py_container z40_server_c_container z40_client_c_container
    docker rmi z40_server_py z40_client_py z40_server_c z40_client_c || true
}

# Main script logic to execute based on input arguments
case "$1" in
    py)
        clean
        build_py
        run_py
        ;;
    c)
        clean
        build_c
        run_c
        ;;
    build-py)
        build_py
        ;;
    run-py)
        run_py
        ;;
    build-c)
        build_c
        ;;
    run-c)
        run_c
        ;;
    clean)
        clean
        ;;
    *)
        echo "Usage: $0 {py|c|build-py|run-py|build-c|run-c|clean}"
        exit 1
        ;;
esac
