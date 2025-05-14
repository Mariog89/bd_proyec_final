-- Crear la base de datos
CREATE DATABASE IF NOT EXISTS bookify CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE bookify;

-- Tabla de clientes:
-- CONSTRAINTS: El usuario debe tener más de 3 caracteres
CREATE TABLE IF NOT EXISTS clientes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario VARCHAR(50) NOT NULL UNIQUE,
    correo VARCHAR(100) NOT NULL UNIQUE,
    clave VARCHAR(255) NOT NULL, -- Para almacenar hash de contraseñas
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CHECK (LENGTH(usuario) > 3)  -- CONSTRAINT
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
-- CONSTRAINS: se añaden restricciones CHECK en precio mayor a 0 y stock mayor o igual a 0
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
    FOREIGN KEY (id_editorial) REFERENCES editoriales(id),
    CONSTRAINT chk_precio_positive CHECK (precio > 0),
    CONSTRAINT chk_stock_nonnegative CHECK (stock >= 0)

);

-- Tabla de ventas
-- CONSTRAINTS: se añade restricción CHECK en cantidad
CREATE TABLE IF NOT EXISTS ventas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_libro INT NOT NULL,
    id_cliente INT NOT NULL,
    cantidad INT NOT NULL,
    total DECIMAL(10,2) NOT NULL,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_libro) REFERENCES libros(id),
    FOREIGN KEY (id_cliente) REFERENCES clientes(id),
    CONSTRAINT chk_cantidad_positive CHECK (cantidad > 0)

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

-- Creación de índices
CREATE INDEX idx_titulo_libros ON libros(titulo);
CREATE INDEX idx_fecha_registro_clientes ON clientes(fecha_registro);

-- Procedimientos almacenados:

-- Procedimiento para registrar una venta.
DELIMITER $$
CREATE PROCEDURE sp_registrar_venta(
    IN p_id_libro INT,
    IN p_id_cliente INT,
    IN p_cantidad INT
)
BEGIN
    DECLARE v_stock INT;
    DECLARE v_precio DECIMAL(10,2);
    DECLARE v_total DECIMAL(10,2);

    -- Obtener el stock y precio actual del libro
    SELECT stock, precio INTO v_stock, v_precio FROM libros WHERE id = p_id_libro;

    -- Verificar que el stock sea suficiente
    IF v_stock < p_cantidad THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Stock insuficiente para realizar la venta';
    ELSE
        SET v_total = v_precio * p_cantidad;
        INSERT INTO ventas (id_libro, id_cliente, cantidad, total) VALUES (p_id_libro, p_id_cliente, p_cantidad, v_total);
        -- No se actualiza el stock aquí: se realiza en el trigger AFTER INSERT
    END IF;
END $$


-- Procedimiento para obtener los libros de un autor determinado
CREATE PROCEDURE sp_get_libros_por_autor(
    IN p_id_autor INT
)
BEGIN
    SELECT l.id, l.titulo, l.precio, l.stock, l.fecha_publicacion
    FROM libros l
    WHERE l.id_autor = p_id_autor;
END $$

DELIMITER ;


-- Disparadores (Triggers)
DELIMITER $$

-- Trigger antes de insertar en ventas: verifica que haya stock suficiente
CREATE TRIGGER trg_ventas_before_insert
BEFORE INSERT ON ventas
FOR EACH ROW
BEGIN
    DECLARE v_stock INT;
    SELECT stock INTO v_stock FROM libros WHERE id = NEW.id_libro;
    IF v_stock < NEW.cantidad THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Stock insuficiente para la venta (trigger check)';
    END IF;
END $$

-- Trigger después de insertar en ventas: actualiza el stock del libro restándole la cantidad vendida
CREATE TRIGGER trg_ventas_after_insert
AFTER INSERT ON ventas
FOR EACH ROW
BEGIN
    UPDATE libros SET stock = stock - NEW.cantidad WHERE id = NEW.id_libro;
END $$

DELIMITER ;