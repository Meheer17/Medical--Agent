-- Create database
CREATE DATABASE IF NOT EXISTS nithin_db;

-- Create user 'mahi' with all privileges
CREATE USER IF NOT EXISTS 'mahi'@'localhost' IDENTIFIED BY 'mahi@123';

-- Grant all privileges on nithin_db
GRANT ALL PRIVILEGES ON nithin_db.* TO 'mahi'@'localhost';

-- Grant global privileges
GRANT ALL PRIVILEGES ON *.* TO 'mahi'@'localhost' WITH GRANT OPTION;

-- Flush privileges to apply changes
FLUSH PRIVILEGES;

-- Show created user
SELECT User, Host FROM mysql.user WHERE User='mahi';

-- Show databases
SHOW DATABASES;
