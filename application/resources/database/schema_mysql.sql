-- MySQL dump 10.13  Distrib 5.7.24, for Linux (x86_64)
--
-- Host: localhost    Database: db_vg_stats
-- ------------------------------------------------------
-- Server version	5.7.24

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `tbl_submit_document_stat`
--

DROP TABLE IF EXISTS `tbl_submit_document_stat`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tbl_submit_document_stat` (
  `submission_id` bigint(20) unsigned NOT NULL,
  `submission_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `job_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `uuid` CHAR(32) NOT NULL,

  `process_status` CHAR(20) NOT NULL DEFAULT "NOT PROCESSED",

  `length_by_sentence` bigint(20) unsigned NOT NULL,
  `length_by_distinct_token` bigint(20) unsigned NOT NULL,
  `length_by_word` bigint(20) unsigned NOT NULL,
  `length_by_character` bigint(20) unsigned NOT NULL,
  `lexical_diversity` float unsigned NOT NULL,
  `data_by_sentence` json NOT NULL,
  `data_by_fdist` json NOT NULL,

  `wordfrequency_all` float unsigned NOT NULL,
  `wordfrequency_content` float unsigned NOT NULL,
  `wordfrequency_function` float unsigned NOT NULL,
  `wordrangescore` float unsigned NOT NULL,
  `academicwordscore` float unsigned NOT NULL,
  `academic_sublists_score` float unsigned NOT NULL,
  `familiarityscore` float unsigned NOT NULL,
  `concretenessscore` float unsigned NOT NULL,
  `imagabilityscore` float unsigned NOT NULL,
  `meaningfulnesscscore` float unsigned NOT NULL,
  `meaningfulnesspscore` float unsigned NOT NULL,
  `ageofacquisitionscore` float unsigned NOT NULL,
  `grammar_errorrate` float unsigned NOT NULL,
  `flesch_reading_ease` float unsigned NOT NULL,
  `flesch_kincaid_grade_level` float unsigned NOT NULL,
  `smog` float unsigned NOT NULL,
  `coleman_liau` float unsigned NOT NULL,
  `ari` float unsigned NOT NULL,
  `semanticoverlap` float unsigned NOT NULL,
  `typetokenratio` float unsigned NOT NULL,
  `holistic_score` float unsigned NOT NULL,

  PRIMARY KEY (`uuid`),
  UNIQUE KEY `UNIQUE_ID` (`uuid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;


DROP TABLE IF EXISTS document;

CREATE TABLE document (
  id INTEGER PRIMARY KEY AUTO_INCREMENT,
  `submission_id` bigint(20) unsigned NOT NULL,
  `uuid` CHAR(32) NOT NULL,
  `filename` TEXT NOT NULL DEFAULT "",
  `filepath` TEXT NOT NULL DEFAULT "",
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  process_status CHAR(20) NOT NULL DEFAULT "NOT PROCESSED",
  title TEXT,
  body TEXT NOT NULL,
  processed_body TEXT
);

DROP TABLE IF EXISTS user_tasks;

CREATE TABLE user_tasks (
  id INTEGER PRIMARY KEY AUTO_INCREMENT,
  `submission_id` bigint(20) unsigned NOT NULL,
  `user_id` CHAR(32) NOT NULL,
  `uuid` CHAR(32) NOT NULL,
  `process_status` CHAR(20) NOT NULL DEFAULT "NOT PROCESSED",
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);


/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2020-03-23  6:21:06
