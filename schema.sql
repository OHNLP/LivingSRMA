CREATE DATABASE  IF NOT EXISTS `lnma` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `lnma`;
-- MySQL dump 10.13  Distrib 8.0.20, for macos10.15 (x86_64)
--
-- Host: 172.22.15.10    Database: lnma
-- ------------------------------------------------------
-- Server version	8.0.19

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `admins`
--

DROP TABLE IF EXISTS `admins`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `admins` (
  `uid` varchar(64) NOT NULL,
  `password` varchar(128) DEFAULT NULL,
  `first_name` varchar(45) DEFAULT NULL,
  `last_name` varchar(45) DEFAULT NULL,
  `role` varchar(16) DEFAULT NULL,
  PRIMARY KEY (`uid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `admins`
--

LOCK TABLES `admins` WRITE;
/*!40000 ALTER TABLE `admins` DISABLE KEYS */;
INSERT INTO `admins` VALUES ('hehuan','pbkdf2:sha256:150000$oHLnajng$9be224b50b962de1d83cd745124fc6fe6828e5079c560fa6654d668439b77503','Huan','He','root');
/*!40000 ALTER TABLE `admins` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `notes`
--

DROP TABLE IF EXISTS `notes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `notes` (
  `note_id` varchar(48) NOT NULL COMMENT 'UUID',
  `paper_id` varchar(48) NOT NULL,
  `project_id` varchar(48) NOT NULL,
  `data` json DEFAULT NULL,
  `date_created` datetime NOT NULL,
  `date_updated` datetime NOT NULL,
  `is_deleted` varchar(8) NOT NULL DEFAULT 'no',
  PRIMARY KEY (`note_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `notes`
--

LOCK TABLES `notes` WRITE;
/*!40000 ALTER TABLE `notes` DISABLE KEYS */;
/*!40000 ALTER TABLE `notes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `papers`
--

DROP TABLE IF EXISTS `papers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `papers` (
  `paper_id` varchar(48) NOT NULL,
  `pid` varchar(64) NOT NULL,
  `pid_type` varchar(8) NOT NULL DEFAULT 'pmid',
  `project_id` varchar(32) NOT NULL,
  `title` varchar(256) NOT NULL,
  `pub_date` varchar(32) DEFAULT NULL,
  `authors` text,
  `journal` varchar(128) DEFAULT NULL,
  `meta` json DEFAULT NULL COMMENT 'Use this JSON object to store all the information about this study',
  `ss_st` varchar(8) NOT NULL DEFAULT 'NA' COMMENT 'Screening State Start: for study screening, indicating where the study comes from: b10: batch import/search, b11: other, b12: other manual way, a10: automatic way, a11: auto search',
  `ss_pr` varchar(8) NOT NULL DEFAULT 'NA' COMMENT 'Screening State Process: for study screening, indicating which process the study is in: p30: loaded meta info, p40: checked unique, p50: checked title, p60: checked full text, p70: checked sr, p80: checked ma',
  `ss_rs` varchar(8) NOT NULL DEFAULT 'NA' COMMENT 'Screening State Result: for study screening, indicating what result for the study: e1: excluded for duplicate, e2: excluded for title, e13: excluded for full text, e4: excluded for updates, f1: included in sr, f2: included in ma, f3: included in sr and ma',
  `date_created` datetime NOT NULL,
  `date_updated` datetime NOT NULL,
  `is_deleted` varchar(8) NOT NULL DEFAULT 'no',
  PRIMARY KEY (`paper_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `papers`
--

LOCK TABLES `papers` WRITE;
/*!40000 ALTER TABLE `papers` DISABLE KEYS */;
INSERT INTO `papers` VALUES ('3dbdd662-97f7-11ea-9a4b-98eecba7646f','24019545','pmid','123','','','','',NULL,'a12','na','na','2020-05-16 23:31:14','2020-05-16 23:31:14','no'),('64a46c7a-99e9-11ea-9a4b-98eecba7646f','24019545','pmid','123','','','','',NULL,'a12','na','na','2020-05-19 10:57:08','2020-05-19 10:57:08','no');
/*!40000 ALTER TABLE `papers` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `projects`
--

DROP TABLE IF EXISTS `projects`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `projects` (
  `project_id` varchar(48) NOT NULL,
  `owner_uid` varchar(64) NOT NULL,
  `keystr` varchar(64) NOT NULL DEFAULT 'KEY_STR',
  `title` text NOT NULL,
  `abstract` text,
  `date_created` datetime NOT NULL,
  `date_updated` datetime NOT NULL,
  `settings` json DEFAULT NULL COMMENT 'Store the collector setting and other configs for this project',
  `is_deleted` varchar(8) NOT NULL DEFAULT 'no',
  PRIMARY KEY (`project_id`),
  UNIQUE KEY `key_str_UNIQUE` (`keystr`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `projects`
--

LOCK TABLES `projects` WRITE;
/*!40000 ALTER TABLE `projects` DISABLE KEYS */;
INSERT INTO `projects` VALUES ('0b8098bc-99e9-11ea-9a4b-98eecba7646f','hehuan2112@gmail.com','0B8098BD','The small lung cell project','The small lung cell project','2020-05-19 10:54:39','2020-05-19 10:54:39','{\"collect_template\": {}}','no'),('954af104-99ea-11ea-9a4b-98eecba7646f','hehuan2112@gmail.com','954AF105','The kidney cancer project','The kidney','2020-05-19 11:05:39','2020-05-19 11:05:39','{\"collect_template\": {}}','no');
/*!40000 ALTER TABLE `projects` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `rel_project_users`
--

DROP TABLE IF EXISTS `rel_project_users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `rel_project_users` (
  `project_id` varchar(48) NOT NULL,
  `uid` varchar(64) NOT NULL,
  PRIMARY KEY (`project_id`,`uid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `rel_project_users`
--

LOCK TABLES `rel_project_users` WRITE;
/*!40000 ALTER TABLE `rel_project_users` DISABLE KEYS */;
INSERT INTO `rel_project_users` VALUES ('0b8098bc-99e9-11ea-9a4b-98eecba7646f','hehuan2112@gmail.com'),('954af104-99ea-11ea-9a4b-98eecba7646f','hehuan2112@gmail.com');
/*!40000 ALTER TABLE `rel_project_users` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `uid` varchar(64) NOT NULL,
  `password` varchar(128) DEFAULT NULL,
  `first_name` varchar(45) DEFAULT NULL,
  `last_name` varchar(45) DEFAULT NULL,
  `role` varchar(16) NOT NULL DEFAULT 'user',
  `is_deleted` varchar(8) NOT NULL DEFAULT 'no',
  PRIMARY KEY (`uid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES ('hehuan2112@gmail.com','pbkdf2:sha256:150000$oHLnajng$9be224b50b962de1d83cd745124fc6fe6828e5079c560fa6654d668439b77503','Huan','He','user','no'),('sipra.irbaz@gmail.com','pbkdf2:sha256:150000$oHLnajng$9be224b50b962de1d83cd745124fc6fe6828e5079c560fa6654d668439b77503','Irbaz','Riaz','user','no');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2020-05-19 15:13:19
