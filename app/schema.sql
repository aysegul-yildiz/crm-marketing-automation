CREATE TABLE IF NOT EXISTS StaffUser (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'MARKETER'
);

CREATE TABLE IF NOT EXISTS Customer (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) NOT NULL,
    surname VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL
);

-- item listings basically
CREATE TABLE IF NOT EXISTS listing (
    id INT PRIMARY KEY AUTO_INCREMENT,
    listing_title VARCHAR(150) NOT NULL,
    price FLOAT NOT NULL
);

CREATE TABLE IF NOT EXISTS segmentation_group (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS listing_segmentation (
    listing_id INT,
    segmentation_id INT,
    PRIMARY KEY(listing_id, segmentation_id),
    FOREIGN KEY(listing_id) REFERENCES listing(id)
        ON DELETE CASCADE,
    FOREIGN KEY(segmentation_id) REFERENCES segmentation_group(id)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS segmentation_discount (
    segmentation_id INT PRIMARY KEY,
    discount_percentage INT DEFAULT 0,
    FOREIGN KEY(segmentation_id) REFERENCES segmentation_group(id)
        ON DELETE CASCADE,
    CHECK(discount_percentage >= 0)
);

CREATE TABLE IF NOT EXISTS customer_segmentation (
    customer_id INT,
    segmentation_id INT,
    PRIMARY KEY(customer_id, segmentation_id),
    FOREIGN KEY(customer_id) REFERENCES Customer(id)
        ON DELETE CASCADE,
    FOREIGN KEY(segmentation_id) REFERENCES segmentation_group(id)
        ON DELETE CASCADE
);

CREATE TABLE segmentation_rule (
    id INT PRIMARY KEY AUTO_INCREMENT,
    segmentation_id INT,
    field VARCHAR(50) NOT NULL,
    operator VARCHAR(10) NOT NULL,
    target_value VARCHAR(100) NOT NULL,
    add_or_remove BOOLEAN NOT NULL, -- when true the user will be added to the segment, else it will be removed from the segment when the predicate is true
    FOREIGN KEY(segmentation_id) REFERENCES segmentation_group(id)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS campaign (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    status VARCHAR(20) NOT NULL,
    CHECK(status IN ('PLANNED', 'ACTIVE', 'CLOSED'))
);

CREATE TABLE IF NOT EXISTS campaign_has_segment(
    campaign_id INT,
    segmentation_id INT,
    PRIMARY KEY(campaign_id, segmentation_id),
    FOREIGN KEY(campaign_id) REFERENCES campaign(id)
        ON DELETE CASCADE,
    FOREIGN KEY(segmentation_id) REFERENCES segmentation_group(id)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS workflow (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) NOT NULL,
    campaign_id INT NOT NULL,
    creation_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    execution_start_time TIMESTAMP DEFAULT NULL,
    FOREIGN KEY(campaign_id) REFERENCES campaign(id)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS workflow_step (
    id INT PRIMARY KEY AUTO_INCREMENT,
    workflow_id INT,
    step_order INT NOT NULL,
    action_type VARCHAR(50),
    action_payload JSON,
    status VARCHAR(20),
    delay_minutes_after_prev INT DEFAULT 0,
    executed_at TIMESTAMP DEFAULT NULL, 
    FOREIGN KEY(workflow_id) REFERENCES workflow(id)
        ON DELETE CASCADE,
    CHECK(step_order > 0),
    CHECK(status IN ('PENDING', 'DONE', 'FAILED')),
    CHECK(action_type IN ('email', 'discord-post', 'discount')),
    UNIQUE(workflow_id, step_order)
);

CREATE TABLE IF NOT EXISTS customer_event (
    id INT PRIMARY KEY AUTO_INCREMENT,
    customer_id INT,
    event_type VARCHAR(50),
    event_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSON,
    FOREIGN KEY(customer_id) REFERENCES Customer(id)
);


CREATE TABLE IF NOT EXISTS campaign_event (
    id INT PRIMARY KEY AUTO_INCREMENT,
    customer_id INT,
    step_id INT,
    event_type VARCHAR(50),
    event_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(customer_id) REFERENCES Customer(id),
    FOREIGN KEY(step_id) REFERENCES workflow_step(id)
);


CREATE TABLE IF NOT EXISTS conversion_event (
    id INT PRIMARY KEY AUTO_INCREMENT,
    customer_id INT,
    listing_id INT,
    campaign_id INT,
    revenue FLOAT NOT NULL,
    occurred_at DATETIME NOT NULL,
    FOREIGN KEY (listing_id) REFERENCES listing(id),
    FOREIGN KEY (campaign_id) REFERENCES campaign(id),
    FOREIGN KEY (customer_id) REFERENCES Customer(id)
);

