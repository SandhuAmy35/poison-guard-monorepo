#ifndef TUI_LOGGER_HPP
#define TUI_LOGGER_HPP

#include <fstream>
#include <string>
#include <chrono>
#include <iostream>
#include <iomanip>

class TUILogger {
    std::ofstream log_file;
public:
    TUILogger(const std::string& filepath) {
        log_file.open(filepath, std::ios::out | std::ios::app);
    }
    ~TUILogger() { if(log_file.is_open()) log_file.close(); }

    void log(const std::string& level, const std::string& component, const std::string& message) {
        auto now = std::chrono::system_clock::now();
        auto time_t_now = std::chrono::system_clock::to_time_t(now);
        auto ms = std::chrono::duration_cast<std::chrono::milliseconds>(now.time_since_epoch()) % 1000;
        
        char time_str[20];
        strftime(time_str, sizeof(time_str), "%Y-%m-%d %H:%M:%S", localtime(&time_t_now));

        std::stringstream log_line;
        log_line << "[" << time_str << "." << std::setfill('0') << std::setw(3) << ms.count() << "] "
                 << "[" << level << "] "
                 << "[" << component << "] " 
                 << message;

        std::cout << log_line.str() << "\n";
        if(log_file.is_open()) {
            log_file << log_line.str() << "\n";
            log_file.flush();
        }
    }
};

extern TUILogger tui_log;

#endif
