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
    docker run -dit --network z40_network --network-alias z40_client_py_container --name z40_client_py_container z40_client_py:latest
}

run_py() {
    run_py_server
    run_py_client
}

# building and running C containers
build_c_server() {
    docker build -t z40_server_c -f server_c/dockerfile .
}

build_c_client() {
    docker build -t z40_client_c -f client_c/dockerfile .
}

build_c() {
    build_c_server
    build_c_client
}

run_c_server() {
    docker run -dit --network z40_network --network-alias z40_server_c_container --name z40_server_c_container z40_server_c:latest
}

run_c_client() {
    docker run -dit --network z40_network --network-alias z40_client_c_container --name z40_client_c_container z40_client_c:latest
}


run_c() {
    run_c_server
    run_c_client
}

# clean up containers and images
clean() {
    docker kill z40_server_py_container z40_client_py_container z40_server_c_container z40_client_c_container || true
    docker rm -f z40_server_py_container z40_client_py_container z40_server_c_container z40_client_c_container
    docker rmi z40_server_py z40_client_py z40_server_c z40_client_c || true
}

# script
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
    server-py-client-c)
        clean
        build_py_server
        build_c_client
        run_py_server
        run_c_client
        ;;
    server-c-client-py)
        clean
        build_c_server
        build_py_client
        run_c_server
        run_py_client
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
