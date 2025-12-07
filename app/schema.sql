CREATE TABLE IF NOT EXISTS User {
    id INT PRIMARY KEY AUTO_INCREMENT,
    VARCHAR(50) name NOT NULL,
    VARCHAR(50) surname NOT NULL,
    email UNIQUE VARCHAR(100) NOT NULL
};

-- item listings basically
CREATE TABLE IF NOT EXISTS listing {
    id INT PRIMARY KEY AUTO_INCREMENT,
    listing_title VARCHAR(150) NOT NULL,
    price FLOAT NOT NULL
};

CREATE TABLE IF NOT EXISTS segmentation_group{
    id INT PRIMARY KEY AUTO INCREMENT,
    name UNIQUE VARCHAR(50) NOT NULL
};

CREATE TABLE IF NOT EXISTS listing_segmentation{
    listing_id INT,
    segmentation_id INT,
    PRIMARY KEY(listing_id, segmentation_id),
    FOREIGN KEY(listing_id) REFERENCES listing(id)
        ON DELETE CASCADE,
    FOREIGN KEY(segmentation_id) REFERENCES segmentation_group(id)
        ON DELETE CASCADE
};