-- Crear la base de datos
CREATE DATABASE IF NOT EXISTS bookify CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE bookify;

-- Tabla de clientes
CREATE TABLE IF NOT EXISTS clientes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario VARCHAR(50) NOT NULL UNIQUE,
    correo VARCHAR(100) NOT NULL UNIQUE,
    clave VARCHAR(255) NOT NULL, -- Para almacenar hash de contraseñas
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de autores
CREATE TABLE IF NOT EXISTS autores (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    nacionalidad VARCHAR(50),
    fecha_nacimiento DATE
);

-- Tabla de géneros literarios
CREATE TABLE IF NOT EXISTS generos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL UNIQUE
);

-- Tabla de editoriales
CREATE TABLE IF NOT EXISTS editoriales (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    pais VARCHAR(50),
    direccion VARCHAR(200)
);

-- Tabla de libros
CREATE TABLE IF NOT EXISTS libros (
    id INT AUTO_INCREMENT PRIMARY KEY,
    titulo VARCHAR(100) NOT NULL,
    id_autor INT NOT NULL,
    id_genero INT NOT NULL,
    id_editorial INT NOT NULL,
    precio DECIMAL(10,2) NOT NULL,
    stock INT NOT NULL DEFAULT 0,
    fecha_publicacion DATE,
    FOREIGN KEY (id_autor) REFERENCES autores(id),
    FOREIGN KEY (id_genero) REFERENCES generos(id),
    FOREIGN KEY (id_editorial) REFERENCES editoriales(id)
);

-- Tabla de ventas
CREATE TABLE IF NOT EXISTS ventas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_libro INT NOT NULL,
    id_cliente INT NOT NULL,
    cantidad INT NOT NULL,
    total DECIMAL(10,2) NOT NULL,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_libro) REFERENCES libros(id),
    FOREIGN KEY (id_cliente) REFERENCES clientes(id)
);

-- Insertar datos de prueba en autores
INSERT INTO autores (nombre, nacionalidad, fecha_nacimiento) VALUES
('Gabriel García Márquez', 'Colombiano', '1927-03-06'),
('J.K. Rowling', 'Británica', '1965-07-31'),
('Isabel Allende', 'Chilena', '1942-08-02'),
('Stephen King', 'Estadounidense', '1947-09-21'),
('Julio Cortázar', 'Argentino', '1914-08-26');

-- Insertar datos de prueba en géneros
INSERT INTO generos (nombre) VALUES
('Novela'),
('Ciencia Ficción'),
('Fantasía'),
('Terror'),
('Aventura'),
('Romance'),
('Misterio');

-- Insertar datos de prueba en editoriales
INSERT INTO editoriales (nombre, pais, direccion) VALUES
('Penguin Random House', 'España', 'Calle Falsa 123'),
('Editorial Planeta', 'México', 'Av. Siempre Viva 456'),
('Anagrama', 'España', 'Gran Vía 789'),
('Alfaguara', 'Colombia', 'Calle Principal 101'),
('Salamandra', 'Argentina', 'Av. Libertador 202');

-- Insertar datos de prueba en libros
INSERT INTO libros (titulo, id_autor, id_genero, id_editorial, precio, stock, fecha_publicacion) VALUES
('Cien años de soledad', 1, 1, 1, 25.99, 15, '1967-06-05'),
('Harry Potter y la piedra filosofal', 2, 3, 5, 19.99, 30, '1997-06-26'),
('La casa de los espíritus', 3, 1, 2, 22.50, 8, '1982-01-01'),
('El resplandor', 4, 4, 1, 18.75, 12, '1977-01-28'),
('Rayuela', 5, 1, 3, 24.99, 5, '1963-06-01');

-- Crear usuario de la base de datos
CREATE USER IF NOT EXISTS 'bookify_user'@'localhost' IDENTIFIED BY 'bookify_password';
GRANT ALL PRIVILEGES ON bookify.* TO 'bookify_user'@'localhost';
FLUSH PRIVILEGES;