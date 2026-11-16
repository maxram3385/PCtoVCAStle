DELETE FROM users WHERE UserNo=2;

DELETE FROM products where ProductNo=1;

UPDATE users
SET LName = 'Busche'
WHERE UserNo=3;

UPDATE products
SET ProductDescription = 'Organic Produce'
WHERE ProductNo=2;

SELECT * FROM users;