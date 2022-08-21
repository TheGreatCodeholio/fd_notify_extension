-- phpMyAdmin SQL Dump
-- version 5.1.1deb5ubuntu1
-- https://www.phpmyadmin.net/
--
-- Host: localhost:3306
-- Generation Time: Aug 11, 2022 at 10:51 PM
-- Server version: 10.6.7-MariaDB-2ubuntu1.1
-- PHP Version: 8.1.8

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `fd_tone_notify`
--

-- --------------------------------------------------------

--
-- Table structure for table `fd_notify_detections`
--

CREATE TABLE `fd_notify_detections` (
  `detection_id` int(11) NOT NULL COMMENT 'Detection ID',
  `detection_tone_name` varchar(255) NOT NULL COMMENT 'Detector Name',
  `detection_tone_data` text DEFAULT NULL COMMENT 'Custom Data Json',
  `detection_mp3_url` varchar(255) DEFAULT NULL COMMENT 'MP3 URL Path',
  `detection_transcription` mediumtext DEFAULT NULL COMMENT 'Deepgram Audio Transcription',
  `detection_timestamp` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Detection Timestamp'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `fd_notify_detections`
--
ALTER TABLE `fd_notify_detections`
  ADD PRIMARY KEY (`detection_id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `fd_notify_detections`
--
ALTER TABLE `fd_notify_detections`
  MODIFY `detection_id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'Detection ID';
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
