#include <ixwebsocket/IXWebSocketServer.h>
#include <iostream>

int main() {
    // Listen on port 4917 on all local network interfaces
    ix::WebSocketServer server(4917, "0.0.0.0");

    server.setOnClientMessageCallback([](std::shared_ptr<ix::ConnectionState> connectionState, 
                                         ix::WebSocket &webSocket, 
                                         const ix::WebSocketMessagePtr &msg) {
        if (msg->type == ix::WebSocketMessageType::Message) {
            std::cout << "Server received: " << msg->str << std::endl;
            
            // Echo the message back to the client
            webSocket.send("{\"type\": \"console\",\"value\": \"hello from B-V2\"}");
        }
    });

    auto res = server.listen();
    if (!res.first) {
        std::cerr << "Server failed to start: " << res.second << std::endl;
        return 1;
    }

    std::cout << "C++ WebSocket Server listening on ws://localhost:4917/" << std::endl;
    
    // Start server in the background and block the main thread
    server.start();
    server.wait(); 

    return 0;
}
