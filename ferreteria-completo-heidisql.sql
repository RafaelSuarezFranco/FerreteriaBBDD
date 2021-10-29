-- --------------------------------------------------------
-- Host:                         127.0.0.1
-- Versión del servidor:         5.7.23 - MySQL Community Server (GPL)
-- SO del servidor:              macos10.13
-- HeidiSQL Versión:             11.3.0.6295
-- --------------------------------------------------------

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET NAMES utf8 */;
/*!50503 SET NAMES utf8mb4 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;


-- Volcando estructura de base de datos para ferreteria
DROP DATABASE IF EXISTS `ferreteria`;
CREATE DATABASE IF NOT EXISTS `ferreteria` /*!40100 DEFAULT CHARACTER SET latin1 */;
USE `ferreteria`;

-- Volcando estructura para tabla ferreteria.articulo
DROP TABLE IF EXISTS `articulo`;
CREATE TABLE IF NOT EXISTS `articulo` (
  `idarticulo` int(11) NOT NULL AUTO_INCREMENT,
  `codigoarticulo` int(11) NOT NULL DEFAULT '0',
  `idfamilia` int(11) NOT NULL,
  `nombrearticulo` varchar(100) NOT NULL,
  `preciounidad` float NOT NULL DEFAULT '0',
  PRIMARY KEY (`idarticulo`),
  KEY `idfamilia` (`idfamilia`),
  CONSTRAINT `articulo_ibfk_1` FOREIGN KEY (`idfamilia`) REFERENCES `familia` (`idfamilia`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=latin1;

-- Volcando datos para la tabla ferreteria.articulo: ~3 rows (aproximadamente)
DELETE FROM `articulo`;
/*!40000 ALTER TABLE `articulo` DISABLE KEYS */;
INSERT INTO `articulo` (`idarticulo`, `codigoarticulo`, `idfamilia`, `nombrearticulo`, `preciounidad`) VALUES
	(1, 10, 1, 'destornillador estrella', 2.35),
	(2, 15, 1, 'destornillador precision', 3.75),
	(3, 60, 2, 'pintura plastica blanca 25 litros', 12.55);
/*!40000 ALTER TABLE `articulo` ENABLE KEYS */;

-- Volcando estructura para tabla ferreteria.cabecerafactura
DROP TABLE IF EXISTS `cabecerafactura`;
CREATE TABLE IF NOT EXISTS `cabecerafactura` (
  `idfactura` int(11) NOT NULL AUTO_INCREMENT,
  `idcliente` int(11) NOT NULL,
  `numerofactura` int(11) NOT NULL,
  `fechafactura` date NOT NULL,
  `estadofactura` varchar(45) DEFAULT NULL,
  `totalneto` float NOT NULL DEFAULT '0',
  `iva` float NOT NULL DEFAULT '0',
  `totalmasiva` float NOT NULL DEFAULT '0',
  `descuento` float NOT NULL DEFAULT '0',
  `importedescuento` float NOT NULL DEFAULT '0',
  `totalbruto` int(11) NOT NULL DEFAULT '0',
  PRIMARY KEY (`idfactura`),
  KEY `idcliente` (`idcliente`),
  CONSTRAINT `cabecerafactura_ibfk_1` FOREIGN KEY (`idcliente`) REFERENCES `cliente` (`idcliente`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=latin1;

-- Volcando datos para la tabla ferreteria.cabecerafactura: ~1 rows (aproximadamente)
DELETE FROM `cabecerafactura`;
/*!40000 ALTER TABLE `cabecerafactura` DISABLE KEYS */;
INSERT INTO `cabecerafactura` (`idfactura`, `idcliente`, `numerofactura`, `fechafactura`, `estadofactura`, `totalneto`, `iva`, `totalmasiva`, `descuento`, `importedescuento`, `totalbruto`) VALUES
	(1, 1, 1, '2021-10-10', 'pendiente pago', 8.45, 1.77, 10.22, 10, 1.02, 9);
/*!40000 ALTER TABLE `cabecerafactura` ENABLE KEYS */;

-- Volcando estructura para tabla ferreteria.cliente
DROP TABLE IF EXISTS `cliente`;
CREATE TABLE IF NOT EXISTS `cliente` (
  `idcliente` int(11) NOT NULL AUTO_INCREMENT,
  `nombrecliente` varchar(100) NOT NULL,
  `direccioncliente` varchar(100) NOT NULL,
  `identificadorcliente` varchar(9) NOT NULL,
  `tipocliente` varchar(10) NOT NULL,
  `correoelectronicocliente` varchar(50) DEFAULT NULL,
  `telefonocliente` char(9) DEFAULT NULL,
  PRIMARY KEY (`idcliente`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=latin1;

-- Volcando datos para la tabla ferreteria.cliente: ~2 rows (aproximadamente)
DELETE FROM `cliente`;
/*!40000 ALTER TABLE `cliente` DISABLE KEYS */;
INSERT INTO `cliente` (`idcliente`, `nombrecliente`, `direccioncliente`, `identificadorcliente`, `tipocliente`, `correoelectronicocliente`, `telefonocliente`) VALUES
	(1, 'juan perez', 'calle alamo 21,21740 sevilla', 'b77777777', 'vip', 'x@x.com', '888888888'),
	(2, 'ana garcia', 'calle de aqui 51,21740 sevilla', 'b66666666', 'vip', 'xxxx@x.com', '111111111');
/*!40000 ALTER TABLE `cliente` ENABLE KEYS */;

-- Volcando estructura para tabla ferreteria.detallefactura
DROP TABLE IF EXISTS `detallefactura`;
CREATE TABLE IF NOT EXISTS `detallefactura` (
  `iddetallefactura` int(11) NOT NULL AUTO_INCREMENT,
  `idfactura` int(11) NOT NULL,
  `idarticulo` int(11) NOT NULL,
  `idfamilia` int(11) NOT NULL,
  `codigoarticulodetallefactura` int(11) NOT NULL DEFAULT '0',
  `unidades` int(11) NOT NULL DEFAULT '0',
  `preciounidaddetallefactura` float NOT NULL DEFAULT '0',
  `subtotal` float NOT NULL DEFAULT '0',
  PRIMARY KEY (`iddetallefactura`),
  KEY `idarticulo` (`idarticulo`),
  KEY `idfactura` (`idfactura`),
  CONSTRAINT `detallefactura_ibfk_1` FOREIGN KEY (`idarticulo`) REFERENCES `articulo` (`idarticulo`),
  CONSTRAINT `detallefactura_ibfk_2` FOREIGN KEY (`idfactura`) REFERENCES `cabecerafactura` (`idfactura`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=latin1;

-- Volcando datos para la tabla ferreteria.detallefactura: ~2 rows (aproximadamente)
DELETE FROM `detallefactura`;
/*!40000 ALTER TABLE `detallefactura` DISABLE KEYS */;
INSERT INTO `detallefactura` (`iddetallefactura`, `idfactura`, `idarticulo`, `idfamilia`, `codigoarticulodetallefactura`, `unidades`, `preciounidaddetallefactura`, `subtotal`) VALUES
	(1, 1, 1, 1, 10, 2, 2.35, 4.7),
	(2, 1, 2, 1, 15, 1, 3.75, 3.75);
/*!40000 ALTER TABLE `detallefactura` ENABLE KEYS */;

-- Volcando estructura para tabla ferreteria.empresa
DROP TABLE IF EXISTS `empresa`;
CREATE TABLE IF NOT EXISTS `empresa` (
  `idempresa` int(11) NOT NULL AUTO_INCREMENT,
  `nombreempresa` varchar(30) NOT NULL,
  `cif` varchar(9) NOT NULL,
  `correoelectronicoempresa` varchar(50) DEFAULT NULL,
  `telefonoempresa` char(9) DEFAULT NULL,
  PRIMARY KEY (`idempresa`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=latin1;

-- Volcando datos para la tabla ferreteria.empresa: ~1 rows (aproximadamente)
DELETE FROM `empresa`;
/*!40000 ALTER TABLE `empresa` DISABLE KEYS */;
INSERT INTO `empresa` (`idempresa`, `nombreempresa`, `cif`, `correoelectronicoempresa`, `telefonoempresa`) VALUES
	(1, 'ferreteria el clavo oxidado', 'b99999999', 'info@empresa.com', '999999999');
/*!40000 ALTER TABLE `empresa` ENABLE KEYS */;

-- Volcando estructura para tabla ferreteria.familia
DROP TABLE IF EXISTS `familia`;
CREATE TABLE IF NOT EXISTS `familia` (
  `idfamilia` int(11) NOT NULL AUTO_INCREMENT,
  `nombrefamilia` varchar(100) NOT NULL,
  `descuentofamilia` float DEFAULT '0',
  PRIMARY KEY (`idfamilia`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=latin1;

-- Volcando datos para la tabla ferreteria.familia: ~2 rows (aproximadamente)
DELETE FROM `familia`;
/*!40000 ALTER TABLE `familia` DISABLE KEYS */;
INSERT INTO `familia` (`idfamilia`, `nombrefamilia`, `descuentofamilia`) VALUES
	(1, 'herramientas', 0),
	(2, 'pinturas', 0);
/*!40000 ALTER TABLE `familia` ENABLE KEYS */;

-- Volcando estructura para tabla ferreteria.historicostock
DROP TABLE IF EXISTS `historicostock`;
CREATE TABLE IF NOT EXISTS `historicostock` (
  `idhistoricostock` int(11) NOT NULL AUTO_INCREMENT,
  `idarticulo` int(11) NOT NULL,
  `cantidadhistoricostock` int(11) NOT NULL DEFAULT '0',
  `fechastock` date NOT NULL,
  PRIMARY KEY (`idhistoricostock`),
  KEY `idarticulo` (`idarticulo`),
  CONSTRAINT `historicostock_ibfk_1` FOREIGN KEY (`idarticulo`) REFERENCES `articulo` (`idarticulo`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=latin1;

-- Volcando datos para la tabla ferreteria.historicostock: ~5 rows (aproximadamente)
DELETE FROM `historicostock`;
/*!40000 ALTER TABLE `historicostock` DISABLE KEYS */;
INSERT INTO `historicostock` (`idhistoricostock`, `idarticulo`, `cantidadhistoricostock`, `fechastock`) VALUES
	(1, 1, 10, '2020-12-30'),
	(2, 1, 15, '2021-01-01'),
	(3, 2, 3, '2021-04-01'),
	(4, 2, 2, '2021-05-15'),
	(5, 3, 7, '2021-01-01');
/*!40000 ALTER TABLE `historicostock` ENABLE KEYS */;

-- Volcando estructura para tabla ferreteria.stock
DROP TABLE IF EXISTS `stock`;
CREATE TABLE IF NOT EXISTS `stock` (
  `idstock` int(11) NOT NULL AUTO_INCREMENT,
  `idarticulo` int(11) NOT NULL,
  `cantidadstock` int(11) NOT NULL DEFAULT '0',
  PRIMARY KEY (`idstock`),
  KEY `idarticulo` (`idarticulo`),
  CONSTRAINT `stock_ibfk_1` FOREIGN KEY (`idarticulo`) REFERENCES `articulo` (`idarticulo`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=latin1;

-- Volcando datos para la tabla ferreteria.stock: ~3 rows (aproximadamente)
DELETE FROM `stock`;
/*!40000 ALTER TABLE `stock` DISABLE KEYS */;
INSERT INTO `stock` (`idstock`, `idarticulo`, `cantidadstock`) VALUES
	(1, 1, 25),
	(2, 2, 5),
	(3, 3, 7);
/*!40000 ALTER TABLE `stock` ENABLE KEYS */;

/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IFNULL(@OLD_FOREIGN_KEY_CHECKS, 1) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40111 SET SQL_NOTES=IFNULL(@OLD_SQL_NOTES, 1) */;
