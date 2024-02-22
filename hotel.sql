-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1:3308
-- Generation Time: Nov 22, 2023 at 06:24 AM
-- Server version: 10.4.28-MariaDB
-- PHP Version: 8.2.4

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `hotel`
--

DELIMITER $$
-- Procedures
CREATE DEFINER=`root`@`localhost` PROCEDURE `CalculateAmount` (IN `reservationID` INT, OUT `totalAmount` DECIMAL(10,2))   BEGIN
    DECLARE checkinDate DATE;
    DECLARE checkoutDate DATE;
    DECLARE dailyRate DECIMAL(10, 2);
    DECLARE stayDuration INT;
    -- Get check-in date, check-out date, and daily rate from the Reservation table
    SELECT Checkin_Date, Checkout_Date, Amount INTO checkinDate, checkoutDate, dailyRate
    FROM Reservation
    WHERE Reservation_id = reservationID;
    -- Calculate the duration of stay in days
    SET stayDuration = DATEDIFF(checkoutDate, checkinDate);
    -- Calculate the total amount based on daily rate and stay duration
    SET totalAmount = dailyRate * stayDuration; -- Calculate the totalAmount
    -- Return the totalAmount using the OUT parameter
    SET @totalAmount = totalAmount; -- Assign the calculated totalAmount to the OUT parameter
END$$

CREATE DEFINER=`root`@`localhost` PROCEDURE `InsertPayment` (IN `p_Reservation_id` INT, IN `p_Amount` DECIMAL(10,2))   BEGIN
    -- Insert the payment record into the Payment table
    INSERT INTO Payment (Reservation_id, Amount, Duration)
    VALUES (p_Reservation_id, p_Amount, NOW());
END$$

CREATE DEFINER=`root`@`localhost` PROCEDURE `UpdateRoomInfo` (IN `roomID` INT, IN `newDescription` VARCHAR(255), IN `newPrice` DECIMAL(10,2), IN `newAc` TINYINT)   BEGIN
    UPDATE room
    SET
        Room_Type = newDescription,
        Price = newPrice,
        AC = newAc
    WHERE
        Room_No = roomID;
END$$
DELIMITER ;

-- --------------------------------------------------------

--
-- Table structure for table `admin`
--

CREATE TABLE `admin` (
  `admin_id` int(10) NOT NULL,
  `name` varchar(255) NOT NULL,
  `email` varchar(255) NOT NULL,
  `password` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
INSERT INTO `admin` (`admin_id`, `name`, `email`, `password`) VALUES
(1, 'Admin1', 'admin1@gmail.com', 'Admin1'),
(2, 'Jake Paul', 'Jakepaul@gmail.com', '12345678'),
(3, 'skanda', 'skandasshetty@gmail.com', '12345678'),
(4, 'sujan', 'skandasshetty@gmail.', '1234');

-- Table structure for table `all_bookings`
CREATE TABLE `all_bookings` (
  `Payment_id` int(11) NOT NULL,
  `Reservation_id` int(11) NOT NULL,
  `cus_id` int(11) NOT NULL,
  `fname` varchar(255) NOT NULL,
  `lname` varchar(255) NOT NULL,
  `Age` int(11) NOT NULL,
  `Address` varchar(255) NOT NULL,
  `Room_No` int(11) NOT NULL,
  `Checkin_Date` int(11) NOT NULL,
  `Checkout_Date` int(11) NOT NULL,
  `Total_Amount` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
INSERT INTO `all_bookings` (`Payment_id`, `Reservation_id`, `cus_id`, `fname`, `lname`, `Age`, `Address`, `Room_No`, `Checkin_Date`, `Checkout_Date`, `Total_Amount`) VALUES
(1, 1, 1, 'Jake', 'Paul', 29, 'Las Vegas', 5, 20231112, 20231114, 6000),
(2, 2, 2, 'Skanda', 'Shetty', 20, 'Udupi', 3, 20231115, 20231120, 5000),
(4, 3, 3, 'Vishwajith', 'Patil', 20, 'Bidar', 11, 20231117, 20231119, 1600),
(5, 4, 3, 'Vishwajith', 'Patil', 20, 'Bidar', 12, 20231120, 20231128, 9600);

-- --------------------------------------------------------

--
-- Table structure for table `customer`
--

CREATE TABLE `customer` (
  `Cus_id` int(11) NOT NULL,
  `email` varchar(255) NOT NULL,
  `fname` varchar(255) NOT NULL,
  `lname` varchar(255) NOT NULL,
  `Age` int(11) NOT NULL,
  `Address` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
INSERT INTO `customer` (`Cus_id`, `email`, `fname`, `lname`, `Age`, `Address`) VALUES
(1, 'jake@gmail.com', 'Jake', 'Paul', 29, 'Las Vegas'),
(2, 'skandasshetty@gmail.com', 'Skanda', 'Shetty', 20, 'Udupi'),
(3, 'vishwajith@gmail.com', 'Vishwajith', 'Patil', 20, 'Bidar'),
(5, 'skandasshetty@gmail.', 'Loki', 'Patil', 67, 'Udupi');

CREATE TABLE `payment` (
  `Payment_id` int(255) NOT NULL,
  `Reservation_id` int(255) NOT NULL,
  `Amount` int(11) NOT NULL,
  `Duration` datetime NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
INSERT INTO `payment` (`Payment_id`, `Reservation_id`, `Amount`, `Duration`) VALUES
(1, 1, 6000, '2023-11-10 00:18:22'),
(2, 2, 5000, '2023-11-10 00:26:12'),
(4, 3, 1600, '2023-11-16 23:20:27'),
(5, 4, 9600, '2023-11-20 00:58:26');

--
-- Triggers `payment`
--
DELIMITER $$
CREATE TRIGGER `InsertAllBookingsAfterPayment` AFTER INSERT ON `payment` FOR EACH ROW BEGIN
    -- Retrieve additional details from the Reservation and Customer tables
    DECLARE v_reservation_id INT;
    DECLARE v_cus_id INT;
    DECLARE v_fname VARCHAR(255);
    DECLARE v_lname VARCHAR(255);
    DECLARE v_age INT;
    DECLARE v_address VARCHAR(255);
    DECLARE v_room_no INT;
    DECLARE v_checkin_date DATE;
    DECLARE v_checkout_date DATE;
    DECLARE v_total_amount DECIMAL(10, 2);

    -- Retrieve the necessary values based on Payment_id
    SELECT r.Reservation_id, c.cus_id, c.fname, c.lname, c.Age, c.Address, r.Room_No, r.Checkin_Date, r.Checkout_Date, NEW.Amount
    INTO v_reservation_id, v_cus_id, v_fname, v_lname, v_age, v_address, v_room_no, v_checkin_date, v_checkout_date, v_total_amount
    FROM Reservation AS r
    JOIN Customer AS c ON r.Cus_id = c.Cus_id
    WHERE r.Reservation_id = NEW.Reservation_id;

    -- Insert the retrieved values into the all_bookings table
    INSERT INTO all_bookings (Payment_id, Reservation_id, cus_id, fname, lname, Age, Address, Room_No, Checkin_Date, Checkout_Date, Total_Amount)
    VALUES (NEW.Payment_id, v_reservation_id, v_cus_id, v_fname, v_lname, v_age, v_address, v_room_no, v_checkin_date, v_checkout_date, v_total_amount);
END
$$
DELIMITER ;

-- --------------------------------------------------------

--
-- Table structure for table `reservation`
--

CREATE TABLE `reservation` (
  `Reservation_id` int(11) NOT NULL,
  `Cus_id` int(11) NOT NULL,
  `Room_No` int(11) NOT NULL,
  `Amount` int(11) NOT NULL,
  `Checkin_Date` date NOT NULL,
  `Checkout_Date` datetime NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `reservation`
--

INSERT INTO `reservation` (`Reservation_id`, `Cus_id`, `Room_No`, `Amount`, `Checkin_Date`, `Checkout_Date`) VALUES
(1, 1, 5, 3000, '2023-11-12', '2023-11-14 00:00:00'),
(2, 2, 3, 1000, '2023-11-15', '2023-11-20 00:00:00'),
(3, 3, 11, 800, '2023-11-17', '2023-11-19 00:00:00'),
(4, 3, 12, 1200, '2023-11-20', '2023-11-28 00:00:00'),
(5, 5, 11, 800, '2023-11-20', '2023-11-30 00:00:00');

-- --------------------------------------------------------

--
-- Table structure for table `room`
--

CREATE TABLE `room` (
  `Room_No` int(11) NOT NULL,
  `Room_Type` varchar(255) NOT NULL,
  `AC` int(1) DEFAULT NULL,
  `Price` int(11) NOT NULL,
  `room_reserved_dates` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`room_reserved_dates`)),
  `Comments` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `room`
--

INSERT INTO `room` (`Room_No`, `Room_Type`, `AC`, `Price`, `room_reserved_dates`, `Comments`) VALUES
(1, 'Standard', 1, 1000, '[{\"check_in_date\": \"20-10-2023\", \"check_out_date\": \"22-10-2023\"}]', NULL),
(2, 'Standard', 0, 1000, '[{\"check_in_date\": \"21-10-2023\", \"check_out_date\": \"28-10-2023\"}, {\"check_in_date\": \"2023-11-09\", \"check_out_date\": \"2023-11-20\"}]', NULL),
(3, 'Deluxe', 1, 2000, '[{\"check_in_date\": \"2023-11-15\", \"check_out_date\": \"2023-11-20\"}]', NULL),
(4, 'Deluxe', 1, 2000, NULL, NULL),
(5, 'Super Deluxe', 1, 3000, '[{\"check_in_date\": \"2023-11-12\", \"check_out_date\": \"2023-11-14\"}]', NULL),
(6, 'Super Deluxe', 1, 3000, NULL, NULL),
(11, 'Standard', 0, 800, '[{\"check_in_date\": \"2023-11-17\", \"check_out_date\": \"2023-11-19\"}, {\"check_in_date\": \"2023-11-20\", \"check_out_date\": \"2023-11-30\"}]', NULL),
(12, 'Standard', 1, 1200, '[{\"check_in_date\": \"2023-11-20\", \"check_out_date\": \"2023-11-28\"}]', NULL),
(13, 'Standard', 0, 1000, NULL, NULL),
(14, 'Deluxe', 1, 2000, NULL, NULL),
(15, 'Super Deluxe', 1, 3500, NULL, NULL),
(16, 'Super Deluxe', 1, 3500, NULL, NULL);

--
-- Indexes for dumped tables
--

--
-- Indexes for table `admin`
--
ALTER TABLE `admin`
  ADD PRIMARY KEY (`admin_id`);
-
ALTER TABLE `all_bookings`
  ADD PRIMARY KEY (`Payment_id`),
  ADD UNIQUE KEY `Reservation_id` (`Reservation_id`);
--
ALTER TABLE `customer`
  ADD PRIMARY KEY (`Cus_id`),
  ADD UNIQUE KEY `email` (`email`);
--
ALTER TABLE `payment`
  ADD PRIMARY KEY (`Payment_id`),
  ADD UNIQUE KEY `Reservation_id` (`Reservation_id`);
--
ALTER TABLE `reservation`
  ADD PRIMARY KEY (`Reservation_id`);
--
ALTER TABLE `room`
  ADD PRIMARY KEY (`Room_No`);
--
ALTER TABLE `admin`
  MODIFY `admin_id` int(10) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;
--
ALTER TABLE `all_bookings`
  MODIFY `Payment_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;
--
ALTER TABLE `customer`
  MODIFY `Cus_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;
--
ALTER TABLE `payment`
  MODIFY `Payment_id` int(255) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;
--
ALTER TABLE `reservation`
  MODIFY `Reservation_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
