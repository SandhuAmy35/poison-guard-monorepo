#include <iostream>
#include <fcntl.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <unistd.h>
#include <openssl/sha.h>
#include <sstream>
#include <cmath>
#include <vector>
#include "zmq_client.hpp"
#include "tui_logger.hpp"

std::string get_sha256(void* addr, size_t size) {
    if (!addr || size == 0) return "NULL_ADDR";
    unsigned char hash[SHA256_DIGEST_LENGTH];
    SHA256((unsigned char*)addr, size, hash);
    std::stringstream ss;
    for(int i = 0; i < SHA256_DIGEST_LENGTH; i++)
        ss << std::hex << std::setw(2) << std::setfill('0') << (int)hash[i];
    return ss.str();
}

float calculate_haversine(float lat1, float lon1, float lat2, float lon2) {
    const float R = 6371.0; 
    float dlat = (lat2 - lat1) * M_PI / 180.0;
    float dlon = (lon2 - lon1) * M_PI / 180.0;
    lat1 = lat1 * M_PI / 180.0;
    lat2 = lat2 * M_PI / 180.0;
    float a = std::sin(dlat / 2) * std::sin(dlat / 2) +
              std::cos(lat1) * std::cos(lat2) * std::sin(dlon / 2) * std::sin(dlon / 2);
    return R * (2 * std::atan2(std::sqrt(a), std::sqrt(1 - a)));
}

int main(int argc, char* argv[]) {
    tui_log.log("INFO", "SYSTEM", "Booting PoisonGuard Ingestion Engine");
    if (argc < 3) return 1;

    const char* filepath = argv[1];
    std::string profile = argv[2];

    int fd = open(filepath, O_RDONLY);
    if (fd == -1) return 1;

    struct stat sb;
    fstat(fd, &sb);
    if (sb.st_size == 0) return 1;

    char* addr = (char*)mmap(NULL, sb.st_size, PROT_READ, MAP_PRIVATE, fd, 0);
    if (addr == MAP_FAILED) return 1;

    tui_log.log("INFO", "PROVENANCE", "SHA-256: " + get_sha256(addr, sb.st_size));

    ZMQClient client("tcp://127.0.0.1:5555");
    std::string content(addr, sb.st_size);
    std::stringstream ss(content);
    std::string line;
    std::getline(ss, line); // Skip Header

    int count = 0;
    while (std::getline(ss, line)) {
        try {
            std::stringstream line_ss(line);
            std::string val;
            std::vector<std::string> cols;
            while (std::getline(line_ss, val, ',')) { cols.push_back(val); }

            float f1 = 0.0, f2 = 0.0, label = 0.0;
            if (profile == "UPI" && cols.size() >= 22) {
                f1 = std::stof(cols[5]) / 1000.0; 
                f2 = calculate_haversine(std::stof(cols[13]), std::stof(cols[14]), std::stof(cols[20]), std::stof(cols[21])) / 100.0;
                label = std::stof(cols[22]);
            } else if (profile == "CREDIT") {
                f1 = std::stof(cols[1]) / 200000.0; 
                f2 = std::stof(cols[2]) / 20.0;     
                label = std::stof(cols[3]);
            }

            client.send_vector_telemetry(profile + "_TRX_" + std::to_string(count), f1, f2, label, profile);
            count++;
            
            // THE FIX: Lowered throttle from 150,000 to 1,000 microseconds.
            // This allows ~1000 rows per second to flood the ML pipeline.
            usleep(10000); 

        } catch (...) { continue; }
    }
    munmap(addr, sb.st_size);
    close(fd);
    return 0;
}
