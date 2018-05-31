/*
 Navicat Premium Data Transfer

 Source Server         : docker-ubipredb
 Source Server Type    : MySQL
 Source Server Version : 50722
 Source Host           : 192.168.237.129:3306
 Source Schema         : ubi

 Target Server Type    : MySQL
 Target Server Version : 50722
 File Encoding         : 65001

 Date: 01/06/2018 02:26:33
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for apps
-- ----------------------------
DROP TABLE IF EXISTS `apps`;
CREATE TABLE `apps`  (
  `appid` int(11) NOT NULL,
  `name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `labels` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL,
  `types` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL,
  `image` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `is_concerned` int(11) NULL DEFAULT NULL,
  `with_achievement` int(11) NULL DEFAULT 0,
  `crawled_at` bigint(20) NULL DEFAULT 0,
  `created_at` timestamp(0) NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp(0) NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP(0),
  PRIMARY KEY (`appid`) USING BTREE,
  INDEX `is_concerned`(`is_concerned`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for results
-- ----------------------------
DROP TABLE IF EXISTS `results`;
CREATE TABLE `results`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `window_length` int(11) NOT NULL,
  `window_end_date` date NOT NULL,
  `top_up_tags` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL,
  `top_down_tags` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL,
  `top_up_setences` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL,
  `top_down_setences` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL,
  `top_up_reviews` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL,
  `top_down_reviews` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL,
  `created_at` timestamp(0) NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp(0) NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP(0),
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `window`(`window_end_date`, `window_length`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for review_changes
-- ----------------------------
DROP TABLE IF EXISTS `review_changes`;
CREATE TABLE `review_changes`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `appid` int(11) NULL DEFAULT NULL,
  `date` date NULL DEFAULT NULL,
  `new_up` int(11) NULL DEFAULT 0,
  `new_down` int(11) NULL DEFAULT 0,
  `up_to_down` int(11) NULL DEFAULT 0,
  `down_to_up` int(11) NULL DEFAULT 0,
  `created_at` timestamp(0) NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp(0) NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP(0),
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `appid and date`(`appid`, `date`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 15 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for reviews
-- ----------------------------
DROP TABLE IF EXISTS `reviews`;
CREATE TABLE `reviews`  (
  `recommendationid` int(11) NOT NULL,
  `appid` int(11) NOT NULL,
  `steamid` bigint(20) NOT NULL,
  `playtime_forever` int(11) NULL DEFAULT NULL,
  `playtime_last_two_weeks` int(11) NULL DEFAULT NULL,
  `last_played` bigint(20) NULL DEFAULT NULL,
  `achievement_ratio` double NULL DEFAULT NULL,
  `language` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `content` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL,
  `steam_weight` double NULL DEFAULT NULL,
  `weight` double NULL DEFAULT NULL,
  `type` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `vote_up_count` int(11) NULL DEFAULT NULL,
  `vote_funny_count` int(11) NULL DEFAULT NULL,
  `comment_count` int(11) NULL DEFAULT NULL,
  `published_at` bigint(20) NULL DEFAULT NULL,
  `edited_at` bigint(20) NULL DEFAULT NULL,
  `created_at` timestamp(0) NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp(0) NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP(0),
  PRIMARY KEY (`recommendationid`) USING BTREE,
  INDEX `appid and type`(`appid`, `type`) USING BTREE,
  INDEX `language`(`language`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for users
-- ----------------------------
DROP TABLE IF EXISTS `users`;
CREATE TABLE `users`  (
  `steamid` bigint(20) NOT NULL,
  `nickname` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `avatar` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `country` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `level` int(11) NULL DEFAULT NULL,
  `games` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL,
  `review_count` int(11) NULL DEFAULT NULL,
  `screenshot_count` int(11) NULL DEFAULT NULL,
  `workshop_item_count` int(11) NULL DEFAULT NULL,
  `badge_count` int(11) NULL DEFAULT NULL,
  `group_count` int(11) NULL DEFAULT NULL,
  `game_count` int(11) NULL DEFAULT NULL,
  `dlc_count` int(11) NULL DEFAULT 0,
  `friend_count` int(11) NULL DEFAULT NULL,
  `registered_at` int(11) NULL DEFAULT NULL,
  `created_at` timestamp(0) NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp(0) NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP(0),
  PRIMARY KEY (`steamid`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

SET FOREIGN_KEY_CHECKS = 1;
