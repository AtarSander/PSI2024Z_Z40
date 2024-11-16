py: clean build-py run-py

c: clean build-c run-c

build-py:
	docker build -t z40_server_py -f server_py/dockerfile .
	docker build -t z40_client_py -f client_py/dockerfile .

run-py:
	docker run -dit --network z40_network --network-alias z40_server_py_container --name z40_server_py_container z40_server_py:latest
	docker run -dit --network z40_network --network-alias z40_client_py_container --name z40_client_py_container z40_client_py:latest

build-c:
	docker build -t z40_server_c -f server_c/dockerfile .
	docker build -t z40_client_c -f client_c/dockerfile .

run-c:
	docker run -dit --network z40_network --network-alias z40_server_c_container --name z40_server_c_container z40_server_c:latest
	docker run -dit --network z40_network --network-alias z40_client_c_container --name z40_client_c_container z40_client_c:latest

clean:
	docker rm -f z40_server_py z40_client_py z40_server_c z40_client_c || true
