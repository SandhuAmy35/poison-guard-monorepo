#include "zmq_client.hpp"
#include "tui_logger.hpp"

// Initialize the global logger instance
TUILogger tui_log("poisonguard_cpp.log");

ZMQClient::ZMQClient(const std::string &endpoint)
    : context(1), socket(context, zmq::socket_type::push) {
    try {
        socket.connect(endpoint);
        tui_log.log("INFO", "ZMQ_BRIDGE", "Successfully connected to " + endpoint);
    } catch (const zmq::error_t& e) {
        tui_log.log("FATAL", "ZMQ_BRIDGE", std::string("Connection Failed: ") + e.what());
    }
}

void ZMQClient::send_vector_telemetry(std::string batch_id, float feat1, float feat2, float label, std::string profile) {
    std::string json_msg = "{"
        "\"batch_id\":\"" + batch_id + "\","
        "\"demo_vector\": [" + std::to_string(feat1) + "," + std::to_string(feat2) + "," + std::to_string(label) + "],"
        "\"profile\": \"" + profile + "\","
        "\"ingestion_rate\": \"1.4 GB/s\""
    "}";
    socket.send(zmq::buffer(json_msg), zmq::send_flags::none);
}
