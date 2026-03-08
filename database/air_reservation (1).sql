-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- 主机： 127.0.0.1
-- 生成日期： 2025-05-11 16:12:29
-- 服务器版本： 10.4.32-MariaDB
-- PHP 版本： 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- 数据库： `air_reservation`
--

-- --------------------------------------------------------

--
-- 表的结构 `airline`
--

CREATE TABLE `airline` (
  `airline_name` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

--
-- 转存表中的数据 `airline`
--

INSERT INTO `airline` (`airline_name`) VALUES
('Air France'),
('Alaska Airlines'),
('Allegiant Air'),
('American Airlines'),
('China Eastern'),
('Delta Airlines'),
('Emirates'),
('Frontier Airlines'),
('Hawaiian Airlines'),
('JetBlue Airways'),
('Lufthansa'),
('Southwest Airlines'),
('Spirit Airlines'),
('United Airlines');

-- --------------------------------------------------------

--
-- 表的结构 `airline_staff`
--

CREATE TABLE `airline_staff` (
  `username` varchar(50) NOT NULL,
  `password` varchar(50) NOT NULL,
  `first_name` varchar(50) NOT NULL,
  `last_name` varchar(50) NOT NULL,
  `date_of_birth` date NOT NULL,
  `airline_name` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

--
-- 转存表中的数据 `airline_staff`
--

INSERT INTO `airline_staff` (`username`, `password`, `first_name`, `last_name`, `date_of_birth`, `airline_name`) VALUES
('admin1', 'staffpass1', 'Michael', 'Scott', '1970-05-15', 'Delta Airlines'),
('admin2', 'staffpass2', 'Dwight', 'Schrute', '1975-08-20', 'United Airlines'),
('airfrance_admin', 'france123', 'Marie', 'Dupont', '1983-09-22', 'Air France'),
('american_admin', 'american123', 'Susan', 'Brown', '1982-07-25', 'American Airlines'),
('ce_admin', 'china123', 'Li', 'Wei', '1975-11-08', 'China Eastern'),
('delta_admin', 'delta123', 'John', 'Smith', '1980-05-15', 'Delta Airlines'),
('delta_oper', 'delta456', 'Jane', 'Doe', '1985-10-20', 'Delta Airlines'),
('emirates_admin', 'emir123', 'Ahmed', 'Hassan', '1981-01-30', 'Emirates'),
('lauren', '123456', 'lauren', 'yy', '2025-05-01', 'China Eastern'),
('lufthansa_admin', 'luft123', 'Hans', 'Schmidt', '1979-04-18', 'Lufthansa'),
('operator1', 'staffpass3', 'Jim', 'Halpert', '1980-03-10', 'American Airlines'),
('operator2', 'staffpass4', 'Pam', 'Beesly', '1982-11-25', 'Southwest Airlines'),
('staff1', 'staffpass5', 'Stanley', 'Hudson', '1978-07-05', 'JetBlue Airways'),
('staff2', 'staffpass6', 'Phyllis', 'Vance', '1985-01-30', 'Alaska Airlines'),
('staff3', 'staffpass7', 'Angela', 'Martin', '1983-09-12', 'Spirit Airlines'),
('staff4', 'staffpass8', 'Kevin', 'Malone', '1981-04-22', 'Frontier Airlines'),
('staff5', 'staffpass9', 'Oscar', 'Martinez', '1979-12-08', 'Hawaiian Airlines'),
('staff6', 'staffpass10', 'Kelly', 'Kapoor', '1987-02-14', 'Allegiant Air'),
('united_admin', 'united123', 'Michael', 'Johnson', '1978-03-12', 'United Airlines'),
('wyy', '123', 'w', 'yy', '2025-05-08', 'Southwest Airlines');

-- --------------------------------------------------------

--
-- 表的结构 `airplane`
--

CREATE TABLE `airplane` (
  `airline_name` varchar(50) NOT NULL,
  `airplane_id` int(11) NOT NULL,
  `seats` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

--
-- 转存表中的数据 `airplane`
--

INSERT INTO `airplane` (`airline_name`, `airplane_id`, `seats`) VALUES
('Air France', 701, 280),
('Air France', 702, 200),
('Alaska Airlines', 601, 210),
('American Airlines', 301, 280),
('China Eastern', 401, 320),
('Delta Airlines', 101, 250),
('Delta Airlines', 102, 180),
('Emirates', 601, 400),
('Frontier Airlines', 801, 165),
('Hawaiian Airlines', 901, 230),
('JetBlue Airways', 501, 190),
('Lufthansa', 501, 350),
('Southwest Airlines', 401, 175),
('Spirit Airlines', 701, 150),
('United Airlines', 201, 300),
('United Airlines', 202, 220),
('United Airlines', 208, 700),
('United Airlines', 737, 777777),
('United Airlines', 777, 3000);

-- --------------------------------------------------------

--
-- 表的结构 `airport`
--

CREATE TABLE `airport` (
  `airport_name` varchar(50) NOT NULL,
  `airport_city` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

--
-- 转存表中的数据 `airport`
--

INSERT INTO `airport` (`airport_name`, `airport_city`) VALUES
('ATL', 'Atlanta'),
('CDG', 'Paris'),
('DXB', 'Dubai'),
('EWR', 'New York'),
('FRA', 'Frankfurt'),
('JFK', 'New York'),
('LAX', 'Los Angeles'),
('LHR', 'London'),
('NGB', 'Ningbo'),
('ORD', 'Chicago'),
('PVG', 'Shanghai'),
('SFO', 'San Francisco');

-- --------------------------------------------------------

--
-- 表的结构 `booking_agent`
--

CREATE TABLE `booking_agent` (
  `email` varchar(50) NOT NULL,
  `password` varchar(50) NOT NULL,
  `booking_agent_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

--
-- 转存表中的数据 `booking_agent`
--

INSERT INTO `booking_agent` (`email`, `password`, `booking_agent_id`) VALUES
('1111@qq.com', '123456', 123),
('agent10@agency.com', 'agentpass10', 1010),
('agent1@agency.com', 'agentpass1', 1001),
('agent1@example.com', 'agent123', 1001),
('agent2@agency.com', 'agentpass2', 1002),
('agent2@example.com', 'agent234', 1002),
('agent3@agency.com', 'agentpass3', 1003),
('agent3@example.com', 'agent345', 1003),
('agent4@agency.com', 'agentpass4', 1004),
('agent5@agency.com', 'agentpass5', 1005),
('agent6@agency.com', 'agentpass6', 1006),
('agent7@agency.com', 'agentpass7', 1007),
('agent8@agency.com', 'agentpass8', 1008),
('agent9@agency.com', 'agentpass9', 1009),
('american_agent@example.com', 'amer555', 1006),
('china_agent@example.com', 'china888', 1007),
('delta_agent@example.com', 'delta999', 1005),
('multiagent@example.com', 'multi789', 1004),
('yw8003@nyu.edu', '123456', 123);

-- --------------------------------------------------------

--
-- 表的结构 `booking_agent_work_for`
--

CREATE TABLE `booking_agent_work_for` (
  `email` varchar(50) NOT NULL,
  `airline_name` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

--
-- 转存表中的数据 `booking_agent_work_for`
--

INSERT INTO `booking_agent_work_for` (`email`, `airline_name`) VALUES
('1111@qq.com', 'Allegiant Air'),
('1111@qq.com', 'American Airlines'),
('1111@qq.com', 'China Eastern'),
('1111@qq.com', 'Delta Airlines'),
('agent10@agency.com', 'American Airlines'),
('agent1@agency.com', 'Delta Airlines'),
('agent1@agency.com', 'United Airlines'),
('agent1@example.com', 'Delta Airlines'),
('agent2@agency.com', 'American Airlines'),
('agent2@example.com', 'United Airlines'),
('agent3@agency.com', 'JetBlue Airways'),
('agent3@agency.com', 'Southwest Airlines'),
('agent3@example.com', 'American Airlines'),
('agent3@example.com', 'United Airlines'),
('agent4@agency.com', 'Alaska Airlines'),
('agent5@agency.com', 'Spirit Airlines'),
('agent6@agency.com', 'Frontier Airlines'),
('agent6@agency.com', 'Hawaiian Airlines'),
('agent7@agency.com', 'Allegiant Air'),
('agent8@agency.com', 'Delta Airlines'),
('agent9@agency.com', 'United Airlines'),
('american_agent@example.com', 'American Airlines'),
('china_agent@example.com', 'China Eastern'),
('delta_agent@example.com', 'Delta Airlines'),
('multiagent@example.com', 'Air France'),
('multiagent@example.com', 'Delta Airlines'),
('multiagent@example.com', 'United Airlines'),
('yw8003@nyu.edu', 'Air France'),
('yw8003@nyu.edu', 'American Airlines');

-- --------------------------------------------------------

--
-- 表的结构 `customer`
--

CREATE TABLE `customer` (
  `email` varchar(50) NOT NULL,
  `name` varchar(50) NOT NULL,
  `password` varchar(50) NOT NULL,
  `building_number` varchar(30) NOT NULL,
  `street` varchar(30) NOT NULL,
  `city` varchar(30) NOT NULL,
  `state` varchar(30) NOT NULL,
  `phone_number` int(11) NOT NULL,
  `passport_number` varchar(30) NOT NULL,
  `passport_expiration` date NOT NULL,
  `passport_country` varchar(50) NOT NULL,
  `date_of_birth` date NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

--
-- 转存表中的数据 `customer`
--

INSERT INTO `customer` (`email`, `name`, `password`, `building_number`, `street`, `city`, `state`, `phone_number`, `passport_number`, `passport_expiration`, `passport_country`, `date_of_birth`) VALUES
('amanda.taylor@email.com', 'Amanda Taylor', 'pass890', '975', 'Aspen Pl', 'Boston', 'MA', 1234509876, 'P01234567', '2024-09-30', 'USA', '1995-02-14'),
('customer1@example.com', 'Alice Johnson', 'pass123', '123', 'Main St', 'New York', 'NY', 1234567890, 'P12345678', '2030-01-01', 'USA', '1990-05-15'),
('customer2@example.com', 'Bob Wilson', 'pass234', '456', 'Oak Ave', 'Los Angeles', 'CA', 2147483647, 'P23456789', '2028-05-20', 'USA', '1985-10-22'),
('customer3@example.com', 'Charlie Brown', 'pass345', '789', 'Pine St', 'Chicago', 'IL', 2147483647, 'P34567890', '2029-08-15', 'USA', '1992-03-30'),
('customer4@example.com', 'Diana Lee', 'pass456', '101', 'Maple Rd', 'Boston', 'MA', 2147483647, 'P45678901', '2027-11-05', 'USA', '1988-12-10'),
('customer5@example.com', 'Edward Chen', 'pass567', '202', 'Bamboo Ln', 'Shanghai', 'SH', 2147483647, 'P56789012', '2026-07-25', 'China', '1995-02-18'),
('customer6@example.com', 'Fiona Mueller', 'pass678', '303', 'Berliner Str', 'Frankfurt', 'HE', 2147483647, 'P67890123', '2028-09-30', 'Germany', '1987-06-05'),
('customer7@example.com', 'George Martin', 'pass789', '404', 'King\'s Rd', 'London', 'LDN', 2147483647, 'P78901234', '2029-04-15', 'UK', '1993-11-12'),
('customer8@example.com', 'Hannah Kim', 'pass890', '505', 'Sunset Blvd', 'Los Angeles', 'CA', 2147483647, 'P89012345', '2027-03-22', 'USA', '1991-08-28'),
('david.brown@email.com', 'David Brown', 'pass345', '654', 'Elm St', 'Denver', 'CO', 2147483647, 'P56789012', '2026-03-20', 'USA', '1988-07-05'),
('emily.wilson@email.com', 'Emily Wilson', 'pass234', '246', 'Spruce Way', 'Miami', 'FL', 2147483647, 'P89012345', '2026-05-18', 'USA', '1978-04-22'),
('james.moore@email.com', 'James Moore', 'pass567', '864', 'Willow Ct', 'Atlanta', 'GA', 2147483647, 'P90123456', '2025-08-25', 'USA', '1986-12-08'),
('jane.smith@email.com', 'Jane Smith', 'pass456', '456', 'Oak Ave', 'Los Angeles', 'CA', 2147483647, 'P23456789', '2026-01-15', 'USA', '1985-08-20'),
('john.doe@email.com', 'John Doe', 'pass123', '123', 'Main St', 'New York', 'NY', 1234567890, 'P12345678', '2025-12-31', 'USA', '1980-05-15'),
('lisa.davis@email.com', 'Lisa Davis', 'pass678', '987', 'Cedar Ln', 'San Francisco', 'CA', 2147483647, 'P67890123', '2025-07-10', 'USA', '1992-01-30'),
('mike.johnson@email.com', 'Mike Johnson', 'pass789', '789', 'Pine Rd', 'Chicago', 'IL', 2147483647, 'P34567890', '2024-11-30', 'USA', '1990-03-10'),
('robert.miller@email.com', 'Robert Miller', 'pass901', '135', 'Birch Blvd', 'Seattle', 'WA', 2147483647, 'P78901234', '2024-10-05', 'USA', '1983-09-12'),
('sarah.williams@email.com', 'Sarah Williams', 'pass012', '321', 'Maple Dr', 'Dallas', 'TX', 2147483647, 'P45678901', '2025-09-15', 'USA', '1975-11-25'),
('yw8003@nyu.edu', 'lauren wang', '123456', '4', 'West Yangsi Road No.567', 'Shanghai', 'Shanghai', 1000000, 'J11', '2024-06-11', 'china', '2024-05-29');

-- --------------------------------------------------------

--
-- 表的结构 `flight`
--

CREATE TABLE `flight` (
  `airline_name` varchar(50) NOT NULL,
  `flight_num` int(11) NOT NULL,
  `departure_airport` varchar(50) NOT NULL,
  `departure_time` datetime NOT NULL,
  `arrival_airport` varchar(50) NOT NULL,
  `arrival_time` datetime NOT NULL,
  `price` decimal(10,0) NOT NULL,
  `status` varchar(50) NOT NULL,
  `airplane_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

--
-- 转存表中的数据 `flight`
--

INSERT INTO `flight` (`airline_name`, `flight_num`, `departure_airport`, `departure_time`, `arrival_airport`, `arrival_time`, `price`, `status`, `airplane_id`) VALUES
('Air France', 701, 'CDG', '2025-05-21 08:00:00', 'JFK', '2025-05-21 10:30:00', 900, 'upcoming', 701),
('Air France', 702, 'JFK', '2025-05-26 19:00:00', 'CDG', '2025-05-27 08:30:00', 920, 'upcoming', 702),
('Air France', 703, 'CDG', '2025-05-30 10:30:00', 'PVG', '2025-05-30 06:30:00', 1050, 'upcoming', 701),
('American Airlines', 301, 'JFK', '2025-05-19 09:30:00', 'ORD', '2025-05-19 11:00:00', 350, 'upcoming', 301),
('American Airlines', 302, 'ORD', '2025-05-23 14:00:00', 'LAX', '2025-05-23 16:30:00', 420, 'upcoming', 301),
('China Eastern', 401, 'PVG', '2025-05-20 00:30:00', 'JFK', '2025-05-20 15:00:00', 1200, 'upcoming', 401),
('China Eastern', 402, 'JFK', '2025-05-25 01:00:00', 'PVG', '2025-05-25 18:30:00', 1250, 'upcoming', 401),
('Delta Airlines', 0, 'LAX', '2025-05-08 22:10:00', 'JFK', '2025-05-09 02:10:00', 2222, 'upcoming', 101),
('Delta Airlines', 101, 'JFK', '2025-05-20 08:00:00', 'LAX', '2025-05-20 11:30:00', 450, 'upcoming', 101),
('Delta Airlines', 102, 'LAX', '2025-05-22 09:00:00', 'JFK', '2025-05-22 17:30:00', 480, 'upcoming', 102),
('Delta Airlines', 103, 'JFK', '2025-05-25 07:00:00', 'ORD', '2025-05-25 08:30:00', 320, 'upcoming', 101),
('Delta Airlines', 104, 'ATL', '2025-06-01 10:00:00', 'LAX', '2025-06-01 12:30:00', 390, 'upcoming', 102),
('Emirates', 601, 'DXB', '2025-05-23 02:00:00', 'JFK', '2025-05-23 14:30:00', 1100, 'upcoming', 601),
('Emirates', 602, 'JFK', '2025-05-28 22:30:00', 'DXB', '2025-05-29 19:00:00', 1150, 'upcoming', 601),
('Lufthansa', 501, 'FRA', '2025-05-22 07:30:00', 'JFK', '2025-05-22 11:00:00', 950, 'upcoming', 501),
('Lufthansa', 502, 'JFK', '2025-05-27 18:00:00', 'FRA', '2025-05-28 08:30:00', 980, 'upcoming', 501),
('United Airlines', 201, 'ORD', '2025-05-18 06:00:00', 'SFO', '2025-05-18 08:30:00', 410, 'upcoming', 201),
('United Airlines', 202, 'SFO', '2025-05-21 13:00:00', 'ORD', '2025-05-21 19:30:00', 430, 'upcoming', 202),
('United Airlines', 203, 'LAX', '2025-05-24 11:00:00', 'JFK', '2025-05-24 19:30:00', 510, 'upcoming', 201),
('United Airlines', 666, 'LAX', '2025-05-11 20:31:00', 'PVG', '2025-05-11 21:31:00', 666, 'upcoming', 201);

-- --------------------------------------------------------

--
-- 表的结构 `permission`
--

CREATE TABLE `permission` (
  `username` varchar(50) NOT NULL,
  `permission_type` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

--
-- 转存表中的数据 `permission`
--

INSERT INTO `permission` (`username`, `permission_type`) VALUES
('airfrance_admin', 'admin'),
('airfrance_admin', 'operator'),
('american_admin', 'admin'),
('ce_admin', 'admin'),
('delta_admin', 'admin'),
('delta_oper', 'operator'),
('emirates_admin', 'admin'),
('lufthansa_admin', 'admin'),
('united_admin', 'admin'),
('united_admin', 'operator');

-- --------------------------------------------------------

--
-- 表的结构 `purchases`
--

CREATE TABLE `purchases` (
  `ticket_id` int(11) NOT NULL,
  `customer_email` varchar(50) NOT NULL,
  `booking_agent_id` int(11) DEFAULT NULL,
  `purchase_date` date NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

--
-- 转存表中的数据 `purchases`
--

INSERT INTO `purchases` (`ticket_id`, `customer_email`, `booking_agent_id`, `purchase_date`) VALUES
(1, 'customer1@example.com', NULL, '2025-04-15'),
(2, 'customer4@example.com', 1004, '2025-04-12'),
(3, 'customer2@example.com', 1004, '2025-04-16'),
(4, 'customer3@example.com', 1004, '2025-04-17'),
(5, 'customer3@example.com', 1003, '2025-04-18'),
(6, 'customer5@example.com', 1007, '2025-04-19'),
(7, 'customer6@example.com', NULL, '2025-04-20'),
(8, 'customer7@example.com', NULL, '2025-04-22'),
(9, 'customer4@example.com', 1001, '2025-04-25'),
(10, 'customer8@example.com', 1004, '2025-04-30'),
(11, 'customer1@example.com', 1001, '2025-04-30'),
(12, 'customer2@example.com', 1001, '2025-05-01'),
(13, 'customer2@example.com', 1004, '2025-05-02'),
(14, 'customer3@example.com', 1003, '2025-05-03'),
(15, 'customer5@example.com', 1007, '2025-05-05'),
(23, 'yw8003@nyu.edu', NULL, '2025-05-11'),
(24, 'customer1@example.com', NULL, '2025-05-11'),
(25, 'customer1@example.com', NULL, '2025-05-11'),
(26, 'customer2@example.com', NULL, '2025-05-11'),
(27, 'customer2@example.com', NULL, '2025-05-11'),
(28, 'customer2@example.com', NULL, '2025-05-11'),
(29, 'customer1@example.com', 123, '2025-05-11'),
(30, 'customer4@example.com', 123, '2025-05-11');

-- --------------------------------------------------------

--
-- 表的结构 `ticket`
--

CREATE TABLE `ticket` (
  `ticket_id` int(11) NOT NULL,
  `airline_name` varchar(50) NOT NULL,
  `flight_num` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

--
-- 转存表中的数据 `ticket`
--

INSERT INTO `ticket` (`ticket_id`, `airline_name`, `flight_num`) VALUES
(9, 'Air France', 701),
(23, 'Air France', 701),
(29, 'Air France', 701),
(10, 'Air France', 702),
(21, 'Air France', 702),
(24, 'Air France', 702),
(22, 'Air France', 703),
(5, 'American Airlines', 301),
(25, 'American Airlines', 301),
(14, 'American Airlines', 302),
(26, 'American Airlines', 302),
(30, 'American Airlines', 302),
(6, 'China Eastern', 401),
(15, 'China Eastern', 402),
(1, 'Delta Airlines', 101),
(16, 'Delta Airlines', 101),
(17, 'Delta Airlines', 101),
(2, 'Delta Airlines', 102),
(20, 'Delta Airlines', 102),
(11, 'Delta Airlines', 103),
(12, 'Delta Airlines', 104),
(8, 'Emirates', 601),
(27, 'Emirates', 601),
(28, 'Emirates', 602),
(7, 'Lufthansa', 501),
(3, 'United Airlines', 201),
(18, 'United Airlines', 201),
(19, 'United Airlines', 201),
(4, 'United Airlines', 202),
(13, 'United Airlines', 203);

--
-- 转储表的索引
--

--
-- 表的索引 `airline`
--
ALTER TABLE `airline`
  ADD PRIMARY KEY (`airline_name`);

--
-- 表的索引 `airline_staff`
--
ALTER TABLE `airline_staff`
  ADD PRIMARY KEY (`username`),
  ADD KEY `airline_name` (`airline_name`);

--
-- 表的索引 `airplane`
--
ALTER TABLE `airplane`
  ADD PRIMARY KEY (`airline_name`,`airplane_id`);

--
-- 表的索引 `airport`
--
ALTER TABLE `airport`
  ADD PRIMARY KEY (`airport_name`);

--
-- 表的索引 `booking_agent`
--
ALTER TABLE `booking_agent`
  ADD PRIMARY KEY (`email`);

--
-- 表的索引 `booking_agent_work_for`
--
ALTER TABLE `booking_agent_work_for`
  ADD PRIMARY KEY (`email`,`airline_name`),
  ADD KEY `airline_name` (`airline_name`);

--
-- 表的索引 `customer`
--
ALTER TABLE `customer`
  ADD PRIMARY KEY (`email`);

--
-- 表的索引 `flight`
--
ALTER TABLE `flight`
  ADD PRIMARY KEY (`airline_name`,`flight_num`),
  ADD KEY `airline_name` (`airline_name`,`airplane_id`),
  ADD KEY `departure_airport` (`departure_airport`),
  ADD KEY `arrival_airport` (`arrival_airport`);

--
-- 表的索引 `permission`
--
ALTER TABLE `permission`
  ADD PRIMARY KEY (`username`,`permission_type`);

--
-- 表的索引 `purchases`
--
ALTER TABLE `purchases`
  ADD PRIMARY KEY (`ticket_id`,`customer_email`),
  ADD KEY `customer_email` (`customer_email`);

--
-- 表的索引 `ticket`
--
ALTER TABLE `ticket`
  ADD PRIMARY KEY (`ticket_id`),
  ADD KEY `airline_name` (`airline_name`,`flight_num`);

--
-- 限制导出的表
--

--
-- 限制表 `airline_staff`
--
ALTER TABLE `airline_staff`
  ADD CONSTRAINT `airline_staff_ibfk_1` FOREIGN KEY (`airline_name`) REFERENCES `airline` (`airline_name`);

--
-- 限制表 `airplane`
--
ALTER TABLE `airplane`
  ADD CONSTRAINT `airplane_ibfk_1` FOREIGN KEY (`airline_name`) REFERENCES `airline` (`airline_name`);

--
-- 限制表 `booking_agent_work_for`
--
ALTER TABLE `booking_agent_work_for`
  ADD CONSTRAINT `booking_agent_work_for_ibfk_1` FOREIGN KEY (`email`) REFERENCES `booking_agent` (`email`),
  ADD CONSTRAINT `booking_agent_work_for_ibfk_2` FOREIGN KEY (`airline_name`) REFERENCES `airline` (`airline_name`);

--
-- 限制表 `flight`
--
ALTER TABLE `flight`
  ADD CONSTRAINT `flight_ibfk_1` FOREIGN KEY (`airline_name`,`airplane_id`) REFERENCES `airplane` (`airline_name`, `airplane_id`),
  ADD CONSTRAINT `flight_ibfk_2` FOREIGN KEY (`departure_airport`) REFERENCES `airport` (`airport_name`),
  ADD CONSTRAINT `flight_ibfk_3` FOREIGN KEY (`arrival_airport`) REFERENCES `airport` (`airport_name`);

--
-- 限制表 `permission`
--
ALTER TABLE `permission`
  ADD CONSTRAINT `permission_ibfk_1` FOREIGN KEY (`username`) REFERENCES `airline_staff` (`username`);

--
-- 限制表 `purchases`
--
ALTER TABLE `purchases`
  ADD CONSTRAINT `purchases_ibfk_1` FOREIGN KEY (`ticket_id`) REFERENCES `ticket` (`ticket_id`),
  ADD CONSTRAINT `purchases_ibfk_2` FOREIGN KEY (`customer_email`) REFERENCES `customer` (`email`);

--
-- 限制表 `ticket`
--
ALTER TABLE `ticket`
  ADD CONSTRAINT `ticket_ibfk_1` FOREIGN KEY (`airline_name`,`flight_num`) REFERENCES `flight` (`airline_name`, `flight_num`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
