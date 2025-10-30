# Websockets
## Principles of Two-Way Communication with Websockets
When developing our API, our goal is to process the incoming request and build a response for the client. Thus, in order to get data from the server, the client always has to initiate a request first.

When a user receives a new message, we would like them to be notified immediately by the server. In a chat application, working only with HTTP, we would have to make requests every second to check whether new messages had arrived, which would be a massive waste of resources. This is why a new protocol has emerged: **Websocket**. The goal of this protocol is to open a communication channel between a client and a server so that they can exchange data in real time, in both directions.

Websockets try to solve that by opening a full-duplex communication channel, meaning that messages can be sent in both directions and possibly at the same time. Once the channel is opened, the server can send messages to the client without having to wait for a request from the client.

Even if HTTP and Websocket are different protocols, Websockets have been designed to work with HTTP. Indeed, when opening a Websocket, the connection is first initiated using an HTTP request and then upgraded to a WebSocket tunnel. This makes it compatible out of the box with the traditional ports `80` and `443`, which is extremely convenient because we can easily add this feature over existing web servers without the need for an extra process.

WebSockets also share another similarity with HTTP: URIs. As with HTTP, Websockets are identified through classic URIs, with a host, a path, and query parameters. `ws` (Websocket) for insecure connections and `wss` (WebSocket Secure) for SSL/TLS-encrypted connections.


## Handling Multiple Websocket Connections and Broadcasting Messages
A typical use case for WebSockets is to implement real-time communication across multiple clients, such as a chat application. In this configuration, several clients have a open WebSocket tunnel with the server. Thus, the role of the server is to manage all the client connections and broadcast messages to all of them: when a user sends a message, the server has to send it to all other clients in their WebSockets.

For that, we rely on **message brokers**. Message brokers are pieces of software whose role is to receive messages published by a first program and broadvast them to programs that are subscribed to it. Usually, this **publish-subscribe (pub-sub)** pattern is organised into different channels so that messages are clearly organised following their topic or ussage. Some of the best-known message broker software includes Apache Kafka, RabbitMQ, Amazon MQ, Google Cloud Pub/Sub, and Azure Service Bus.

[INSERT IMAGE]

`pip install "broadcaster[redis]"`