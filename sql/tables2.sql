DROP TABLE IF EXISTS transactions CASCADE;
DROP TABLE IF EXISTS favorites CASCADE;
DROP TABLE IF EXISTS items CASCADE;
DROP TABLE IF EXISTS complaints CASCADE;
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS categories CASCADE;

DROP TYPE IF EXISTS item_type CASCADE;
DROP TYPE IF EXISTS complaint_status CASCADE;
DROP TYPE IF EXISTS user_role CASCADE;

CREATE TYPE user_role AS ENUM (
    'user',
    'admin'
);

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    nickname VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
	is_blocked BOOLEAN DEFAULT FALSE,
	blocked_until TIMESTAMP NULL,
    role user_role DEFAULT 'user',
	currency INT DEFAULT 1000000000,
	description TEXT
);

CREATE TYPE complaint_status AS ENUM (
    'confirmed',
	'pending',
    'rejected'
);



CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    parent_id INT REFERENCES categories(id)
);

CREATE TYPE item_type AS ENUM ('trade', 'buy', 'both');

CREATE TABLE items (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    file_size FLOAT,
    file_format VARCHAR(50),
    file_link TEXT,
	image_link TEXT,
    price INT NOT NULL,
    item_type item_type NOT NULL,
    owner_id INT REFERENCES users(id) ON DELETE CASCADE,
    category_id INT REFERENCES categories(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


INSERT INTO categories (title) VALUES
('Graphic Resources'),
('Music Content'),
('Software'),
('Educational Materials'),
('Gaming Resources'),
('Books'),
('Video Materials'),
('Programming');

-- Subcategories for "Graphic Resources"
INSERT INTO categories (title, parent_id) VALUES
('Photos', 1),
('Illustrations', 1),
('Icons', 1),
('Templates (banners, presentations, business cards)', 1),
('3D Models', 1),
('Fonts', 1);

-- Subcategories for "Music Content"
INSERT INTO categories (title, parent_id) VALUES
('Music Tracks', 2),
('Sound Effects', 2),
('Beats (rhythmic patterns for tracks)', 2);

-- Subcategories for "Software"
INSERT INTO categories (title, parent_id) VALUES
('Programs and Utilities', 3),
('Plugins', 3),
('Mobile Applications', 3);

-- Subcategories for "Educational Materials"
INSERT INTO categories (title, parent_id) VALUES
('Video Lessons and Courses', 4),
('Presentations', 4);

-- Subcategories for "Gaming Resources"
INSERT INTO categories (title, parent_id) VALUES
('Characters', 5),
('Textures', 5);

-- Subcategories for "Books"
INSERT INTO categories (title, parent_id) VALUES
('Fiction', 6),
('Non-fiction', 6),
('Audiobooks', 6),
('Comics and Graphic Novels', 6);

-- Subcategories for "Video Materials"
INSERT INTO categories (title, parent_id) VALUES
('Feature Films', 7),
('Series', 7),
('Video Clips', 7);

-- Subcategories for "Programming"
INSERT INTO categories (title, parent_id) VALUES
('Code', 8),
('Libraries', 8);


CREATE TABLE favorites (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    product_id INT NOT NULL REFERENCES items(id) ON DELETE CASCADE,
    UNIQUE(user_id, product_id)
);

CREATE TABLE complaints (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id) ON DELETE CASCADE,
	item_id INT REFEREnCES items(id) ON DELETE CASCADE,
    complaint_text TEXT NOT NULL,
    status complaint_status DEFAULT 'pending',
    resolved_at TIMESTAMP NULL,
    admin_notes TEXT
);

CREATE TABLE transactions (
    id SERIAL PRIMARY KEY,
    buyer_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    seller_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    item_id INT NOT NULL REFERENCES items(id) ON DELETE CASCADE,
    price INT NOT NULL,
    exchange_id INT REFERENCES items(id) ON DELETE CASCADE,
    transaction_type VARCHAR(50) NOT NULL CHECK (transaction_type IN ('buy', 'trade')),
    status VARCHAR(50) NOT NULL CHECK (status IN ('completed', 'pending', 'rejected')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Update main categories
UPDATE categories SET title = 'Graphic Resources' WHERE title = 'Графические ресурсы';
UPDATE categories SET title = 'Music Content' WHERE title = 'Музыкальный контент';
UPDATE categories SET title = 'Software' WHERE title = 'Программное обеспечение';
UPDATE categories SET title = 'Educational Materials' WHERE title = 'Образовательные материалы';
UPDATE categories SET title = 'Gaming Resources' WHERE title = 'Игровые ресурсы';
UPDATE categories SET title = 'Books' WHERE title = 'Книги';
UPDATE categories SET title = 'Video Materials' WHERE title = 'Видеоматериалы';
UPDATE categories SET title = 'Programming' WHERE title = 'Программирование';

-- Update subcategories for "Graphic Resources"
UPDATE categories SET title = 'Photos' WHERE title = 'Фотографии';
UPDATE categories SET title = 'Illustrations' WHERE title = 'Иллюстрации';
UPDATE categories SET title = 'Icons' WHERE title = 'Иконки';
UPDATE categories SET title = 'Templates (banners, presentations, business cards)' WHERE title = 'Шаблоны (баннеры, презентации, визитки)';
UPDATE categories SET title = '3D Models' WHERE title = '3D-модели';
UPDATE categories SET title = 'Fonts' WHERE title = 'Шрифты';

-- Update subcategories for "Music Content"
UPDATE categories SET title = 'Music Tracks' WHERE title = 'Музыкальные треки';
UPDATE categories SET title = 'Sound Effects' WHERE title = 'Звуковые эффекты';
UPDATE categories SET title = 'Beats (rhythmic patterns for tracks)' WHERE title = 'Биты (ритмические шаблоны для треков)';

-- Update subcategories for "Software"
UPDATE categories SET title = 'Programs and Utilities' WHERE title = 'Программы и утилиты';
UPDATE categories SET title = 'Plugins' WHERE title = 'Плагины';
UPDATE categories SET title = 'Mobile Applications' WHERE title = 'Мобильные приложения';

-- Update subcategories for "Educational Materials"
UPDATE categories SET title = 'Video Lessons and Courses' WHERE title = 'Видеоуроки и курсы';
UPDATE categories SET title = 'Presentations' WHERE title = 'Презентации';

-- Update subcategories for "Gaming Resources"
UPDATE categories SET title = 'Characters' WHERE title = 'Персонажи';
UPDATE categories SET title = 'Textures' WHERE title = 'Текстуры';

-- Update subcategories for "Books"
UPDATE categories SET title = 'Fiction' WHERE title = 'Художественная литература';
UPDATE categories SET title = 'Non-fiction' WHERE title = 'Нон-фикшн';
UPDATE categories SET title = 'Audiobooks' WHERE title = 'Аудиокниги';
UPDATE categories SET title = 'Comics and Graphic Novels' WHERE title = 'Комиксы и графические романы';

-- Update subcategories for "Video Materials"
UPDATE categories SET title = 'Feature Films' WHERE title = 'Полнометражные фильмы';
UPDATE categories SET title = 'Series' WHERE title = 'Сериалы';
UPDATE categories SET title = 'Video Clips' WHERE title = 'Видеоролики';

-- Update subcategories for "Programming"
UPDATE categories SET title = 'Code' WHERE title = 'Код';
UPDATE categories SET title = 'Libraries' WHERE title = 'Библиотеки';
