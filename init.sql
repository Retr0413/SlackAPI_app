CREATE DATABASE IF NOT EXISTS slack_attendance;

USE slack_attendance;

CREATE TABLE IF NOT EXISTS attendance (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_name VARCHAR(255) NOT NULL,
    clocl_in_time DATETIME,
    clock_out_time DATETIME
);