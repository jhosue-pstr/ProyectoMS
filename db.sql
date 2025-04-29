-- Base de datos cliente
CREATE DATABASE cliente_db;
USE cliente_db;

CREATE TABLE cliente (
    id INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(50),
    apellido VARCHAR(50),
    dni VARCHAR(20),
    correo VARCHAR(50),
    telefono VARCHAR(20),
    direccion VARCHAR(100)
);
INSERT INTO cliente (nombre, apellido, dni, correo, telefono, direccion) VALUES
('Juan', 'Pérez', '12345678', 'juan.perez@email.com', '987654321', 'Av. Siempre Viva 123'),
('María', 'Gómez', '87654321', 'maria.gomez@email.com', '987654322', 'Calle Falsa 456'),
('Luis', 'Ramírez', '23456789', 'luis.ramirez@email.com', '987654323', 'Jirón Los Olivos 789'),
('Ana', 'Torres', '34567890', 'ana.torres@email.com', '987654324', 'Pasaje El Sol 101'),
('Carlos', 'Fernández', '45678901', 'carlos.fernandez@email.com', '987654325', 'Av. Libertad 202'),
('Lucía', 'Martínez', '56789012', 'lucia.martinez@email.com', '987654326', 'Calle Primavera 303'),
('Pedro', 'Díaz', '67890123', 'pedro.diaz@email.com', '987654327', 'Av. Las Flores 404'),
('Sofía', 'Castro', '78901234', 'sofia.castro@email.com', '987654328', 'Calle Los Rosales 505'),
('Jorge', 'Vega', '89012345', 'jorge.vega@email.com', '987654329', 'Jirón Amazonas 606'),
('Elena', 'Campos', '90123456', 'elena.campos@email.com', '987654330', 'Pasaje Los Pinos 707');

-- Base de datos producto
CREATE DATABASE producto_db;
USE producto_db;

CREATE TABLE producto (
    id INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(50),
    descripcion VARCHAR(100),
    precio DECIMAL(10,2),
    stock INT,
    categoria VARCHAR(50)
);
INSERT INTO producto (nombre, descripcion, precio, stock, categoria) VALUES
('Laptop', 'Laptop para oficina', 2500.00, 15, 'Tecnología'),
('Mouse', 'Mouse inalámbrico', 50.00, 100, 'Tecnología'),
('Teclado', 'Teclado mecánico', 150.00, 80, 'Tecnología'),
('Silla Gamer', 'Silla ergonómica', 900.00, 25, 'Muebles'),
('Monitor', 'Monitor 24 pulgadas', 700.00, 30, 'Tecnología'),
('Audífonos', 'Audífonos bluetooth', 120.00, 60, 'Tecnología'),
('Escritorio', 'Escritorio de madera', 850.00, 20, 'Muebles'),
('Webcam', 'Cámara Full HD', 300.00, 40, 'Tecnología'),
('Impresora', 'Impresora multifunción', 500.00, 15, 'Tecnología'),
('Router', 'Router wifi 5G', 200.00, 50, 'Tecnología');

-- Base de datos venta
CREATE DATABASE venta_db;
USE venta_db;
-- Tabla VENTA
CREATE TABLE venta (
    id INT PRIMARY KEY AUTO_INCREMENT, 
    id_cliente INT NULL,
    fecha DATE,
    total DECIMAL(10,2)
);

-- Tabla DETALLE_VENTA
CREATE TABLE detalle_venta (
    id INT PRIMARY KEY AUTO_INCREMENT,
    id_venta INT,
    id_producto INT,
    cantidad INT,
    precio_unitario DECIMAL(10,2),
    subtotal DECIMAL(10,2),
    FOREIGN KEY (id_venta) REFERENCES venta(id),
    FOREIGN KEY (id_producto) REFERENCES producto_db.producto(id)
);

-- Inserción de VENTAS con totales coherentes con los detalles
INSERT INTO venta (id_cliente, fecha, total) VALUES
(1, '2025-04-20', 2500.00),
(2, '2025-04-21', 100.00),
(3, '2025-04-22', 150.00),
(4, '2025-04-23', 900.00),
(5, '2025-04-24', 3500.00),
(6, '2025-04-25', 240.00),
(7, '2025-04-26', 850.00),
(8, '2025-04-27', 900.00),
(9, '2025-04-27', 1000.00),
(10, '2025-04-28', 200.00);

-- Inserción de DETALLES con subtotales correctos (cantidad * precio_unitario)
INSERT INTO detalle_venta (id_venta, id_producto, cantidad, precio_unitario, subtotal) VALUES
(1, 1, 1, 2500.00, 2500.00),
(2, 2, 2, 50.00, 100.00),
(3, 3, 1, 150.00, 150.00),
(4, 4, 1, 900.00, 900.00),
(5, 5, 5, 700.00, 3500.00),
(6, 6, 2, 120.00, 240.00),
(7, 7, 1, 850.00, 850.00),
(8, 8, 3, 300.00, 900.00),
(9, 9, 2, 500.00, 1000.00),
(10, 10, 1, 200.00, 200.00);

