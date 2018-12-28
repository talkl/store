CREATE TABLE products (
  product_id INT NOT NULL UNIQUE AUTO_INCREMENT,
  product_title VARCHAR(30) UNIQUE NOT NULL,
  product_description TEXT NOT NULL,
  product_price DECIMAL(10,2) NOT NULL,
  product_img_url VARCHAR(300) UNIQUE NOT NULL,
  product_category_id INT NOT NULL,
  product_is_favorite BOOLEAN NOT NULL,
  PRIMARY KEY (product_id),
  FOREIGN KEY (product_category_id)
		REFERENCES categories(category_id)
			ON UPDATE CASCADE
            ON DELETE RESTRICT
);