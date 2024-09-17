USE `taipei_day_trip`;

CREATE TABLE `categorys`(
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL
);

CREATE TABLE `mrts`(
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255)
);

CREATE TABLE `attractions` (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    category_id BIGINT NOT NULL,
    description TEXT NOT NULL,
    address VARCHAR(255) NOT NULL,
    transport TEXT NOT NULL,
    mrt_id BIGINT,
    latitude DECIMAL(10, 8) NOT NULL,
    longitude DECIMAL(11, 8) NOT NULL,
    images TEXT NOT NULL,
    popular INT UNSIGNED NOT NULL DEFAULT 0,
    CONSTRAINT fk_category FOREIGN KEY (category_id) REFERENCES categorys(id) 
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_mrt FOREIGN KEY (mrt_id) REFERENCES mrts(id) 
        ON DELETE SET NULL ON UPDATE CASCADE
);

CREATE TABLE `users`(
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL
);

CREATE TABLE `booking`(
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    attraction_id BIGINT NOT NULL,
    date VARCHAR(255) NOT NULL,
    time VARCHAR(255) NOT NULL,
    price BIGINT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES `users`(id) 
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (attraction_id) REFERENCES `attractions`(id) 
        ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE `order`(
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    prime VARCHAR(255) UNIQUE NOT NULL,
    total_price INT NOT NULL,
    contact_name VARCHAR(255) NOT NULL,
    contact_email VARCHAR(255) NOT NULL,
    contact_phone VARCHAR(20) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    payment_status ENUM("UNPAID", "PAID") DEFAULT "UNPAID" NOT NULL,
    FOREIGN KEY (user_id) REFERENCES `users`(id) 
        ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE `orderItems`(
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    order_id BIGINT NOT NULL,
    attraction_id BIGINT NOT NULL,
    trip_date VARCHAR(10) NOT NULL,
    trip_time ENUM("morning", "afternoon") NOT NULL,
    price INT CHECK (price IN (2000, 2500)) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES `order`(id) 
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (attraction_id) REFERENCES `attractions`(id) 
        ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE `payment` (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    order_id BIGINT NOT NULL,
    payment_amount INT NOT NULL,
    payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    payment_status ENUM("SUCCESS", "FAILURE") NOT NULL,
    FOREIGN KEY (order_id) REFERENCES `order`(id) 
        ON DELETE CASCADE ON UPDATE CASCADE
);