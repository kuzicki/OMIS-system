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
    profile_picture VARCHAR(255),
	is_blocked BOOLEAN DEFAULT FALSE,
	blocked_until TIMESTAMP NULL,
    role user_role DEFAULT 'user',
	currency INT DEFAULT 1000,
	description TEXT
);


CREATE TYPE complaint_status AS ENUM (
    'confirmed',
	'pending',
    'rejected'
);

CREATE TABLE complaints (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id) ON DELETE CASCADE,
    complaint_text TEXT NOT NULL,
    status complaint_status DEFAULT 'pending',
    resolved_at TIMESTAMP NULL,
    admin_notes TEXT
);

CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    parent_id INT REFERENCES categories(id)
);

CREATE TYPE transaction_type AS ENUM ('trade', 'buy', 'both');

CREATE TABLE items (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    file_size FLOAT NOT NULL,
    file_format VARCHAR(50) NOT NULL,
    file_link TEXT NOT NULL,
    price INT NOT NULL,
    transaction_type transaction_type NOT NULL,
    owner_id INT REFERENCES users(id) ON DELETE CASCADE,
    category_id INT REFERENCES categories(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


INSERT INTO categories (title) VALUES
('Графические ресурсы'),
('Музыкальный контент'),
('Программное обеспечение'),
('Образовательные материалы'),
('Игровые ресурсы'),
('Книги'),
('Видеоматериалы'),
('Код, библиотеки для языков программирования');

-- Subcategories for "Графические ресурсы"
INSERT INTO categories (title, parent_id) VALUES
('Фотографии', 1),
('Иллюстрации', 1),
('Иконки', 1),
('Шаблоны (баннеры, презентации, визитки)', 1),
('3D-модели', 1),
('Шрифты', 1);

-- Subcategories for "Музыкальный контент"
INSERT INTO categories (title, parent_id) VALUES
('Музыкальные треки', 2),
('Звуковые эффекты', 2),
('Биты (ритмические шаблоны для треков)', 2);

-- Subcategories for "Программное обеспечение"
INSERT INTO categories (title, parent_id) VALUES
('Программы и утилиты', 3),
('Плагины', 3),
('Мобильные приложения', 3);

-- Subcategories for "Образовательные материалы"
INSERT INTO categories (title, parent_id) VALUES
('Видеоуроки и курсы', 4),
('Презентации', 4);

-- Subcategories for "Книги"
INSERT INTO categories (title, parent_id) VALUES
('Художественная литература', 6),
('Нон-фикшн', 6),
('Аудиокниги', 6),
('Комиксы и графические романы', 6);

-- Subcategories for "Видеоматериалы"
INSERT INTO categories (title, parent_id) VALUES
('Полнометражные фильмы', 7),
('Сериалы', 7),
('Видеоролики', 7);

CREATE TABLE favorites (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    product_id INT NOT NULL REFERENCES items(id) ON DELETE CASCADE,
    UNIQUE(user_id, product_id)
);

CREATE TABLE transactions (
    id SERIAL PRIMARY KEY,
    buyer_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    seller_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    item_id INT NOT NULL REFERENCES items(id) ON DELETE CASCADE,
    price INT NOT NULL,
	product_id INT NOT NULL REFERENCES items(id) ON DELETE CASCADE,
    exchange_id INT REFERENCES items(id) ON DELETE CASCADE,
    transaction_type VARCHAR(50) NOT NULL CHECK (transaction_type IN ('purchase', 'trade')),
    status VARCHAR(50) NOT NULL CHECK (status IN ('completed', 'pending', 'rejected')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);