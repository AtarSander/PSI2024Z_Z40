py: clean build-py run-py

c: clean build-c run-c

build-py:
	docker build -t server_py -f server_py/dockerfile .
	docker build -t client_py -f client_py/dockerfile .

run-py:
	docker run -dit --network cs_network --network-alias pserver1 --name pserver1 server_py:latest
	docker run -dit --network cs_network --network-alias pclient1 --name pclient1 client_py:latest

build-c:
	docker build -t server_c -f server_c/dockerfile .
	docker build -t client_c -f client_c/dockerfile .

run-c:
	docker run -dit --network cs_network --network-alias cserver1 --name cserver1 server_c:latest
	docker run -dit --network cs_network --network-alias cclient1 --name cclient1 client_c:latest

clean:
	docker rm -f pserver1 pclient1 cserver1 cclient1 || true