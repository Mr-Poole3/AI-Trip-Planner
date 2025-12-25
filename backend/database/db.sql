-- AI-Trip-Planner 用户系统建表 SQL
-- 创建日期: 2025-12-25
CREATE DATABASE IF NOT EXISTS `ai_trip_planner`
-- 1. 用户表
CREATE TABLE IF NOT EXISTS `users` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '用户ID',
  `username` VARCHAR(64) NOT NULL COMMENT '用户名',
  `email` VARCHAR(255) NOT NULL COMMENT '登录邮箱',
  `password_hash` VARCHAR(255) DEFAULT NULL COMMENT '密码哈希值(第三方登录可为空)',
  `avatar_url` VARCHAR(512) DEFAULT NULL COMMENT '头像URL',
  `status` TINYINT NOT NULL DEFAULT 1 COMMENT '状态:1正常,0禁用',
  `oauth_provider` VARCHAR(32) DEFAULT NULL COMMENT '第三方登录提供商 (如: google, wechat)',
  `oauth_id` VARCHAR(128) DEFAULT NULL COMMENT '第三方登录唯一ID',
  `last_login_at` DATETIME DEFAULT NULL COMMENT '最近登录时间',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `is_deleted` TINYINT NOT NULL DEFAULT 0 COMMENT '软删除标记:0否,1是',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_username` (`username`),
  UNIQUE KEY `uk_email` (`email`),
  KEY `idx_oauth` (`oauth_provider`, `oauth_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';

-- 2. 用户 Token 表 (用于管理 Refresh Token)
CREATE TABLE IF NOT EXISTS `user_tokens` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `user_id` BIGINT UNSIGNED NOT NULL COMMENT '用户ID',
  `token` VARCHAR(512) NOT NULL COMMENT 'refresh token 或其标识',
  `user_agent` VARCHAR(512) DEFAULT NULL COMMENT '用户UA信息',
  `ip` VARCHAR(64) DEFAULT NULL COMMENT '登录IP',
  `expires_at` DATETIME NOT NULL COMMENT '过期时间',
  `revoked` TINYINT NOT NULL DEFAULT 0 COMMENT '是否已吊销',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  KEY `idx_user` (`user_id`),
  KEY `idx_token` (`token`(191))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户Token表';

-- 3. 密码重置 Token 表
CREATE TABLE IF NOT EXISTS `password_reset_tokens` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `user_id` BIGINT UNSIGNED NOT NULL COMMENT '用户ID',
  `reset_token` VARCHAR(255) NOT NULL COMMENT '密码重置token',
  `expires_at` DATETIME NOT NULL COMMENT '过期时间',
  `used` TINYINT NOT NULL DEFAULT 0 COMMENT '是否已使用',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_reset_token` (`reset_token`),
  KEY `idx_user` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='密码重置Token表';

-- 4. LLM 调用历史表
CREATE TABLE IF NOT EXISTS `llm_call_logs` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `user_id` BIGINT UNSIGNED NOT NULL COMMENT '用户ID',
  `model` VARCHAR(128) NOT NULL COMMENT '模型名称',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '调用时间',
  PRIMARY KEY (`id`),
  KEY `idx_user_created` (`user_id`, `created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='LLM调用历史表';
