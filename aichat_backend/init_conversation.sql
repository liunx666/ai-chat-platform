-- =============================================
-- AI Chat 对话功能数据库表结构
-- 创建时间：2026-05-28
-- 说明：包含对话信息表和消息表，支持多租户
-- =============================================

-- ---------------------------------------------
-- 1. AI 对话信息表（ai_conversations）
-- ---------------------------------------------
CREATE TABLE IF NOT EXISTS `ai_conversations` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '对话ID',
    `tenant_id` VARCHAR(64) NOT NULL DEFAULT 'default' COMMENT '租户ID',
    `user_id` BIGINT NOT NULL COMMENT '用户ID',
    `title` VARCHAR(255) DEFAULT '新对话' COMMENT '对话标题/名字',
    `is_deleted` TINYINT DEFAULT 0 COMMENT '软删除标记：0=未删除，1=已删除',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最后更新时间',
    PRIMARY KEY (`id`),
    KEY `idx_tenant_user` (`tenant_id`, `user_id`) COMMENT '按租户+用户查询索引',
    KEY `idx_user_updated` (`user_id`, `updated_at`) COMMENT '按用户+更新时间查询索引',
    KEY `idx_tenant_deleted` (`tenant_id`, `is_deleted`) COMMENT '按租户+删除状态查询索引'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='AI对话信息表';

-- ---------------------------------------------
-- 2. AI 对话消息表（ai_messages）
-- 合并存储：用户问题和AI回复在同一行
-- ---------------------------------------------
CREATE TABLE IF NOT EXISTS `ai_messages` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '消息主键ID',
    `tenant_id` VARCHAR(64) NOT NULL DEFAULT 'default' COMMENT '租户ID',
    `user_id` BIGINT NOT NULL COMMENT '用户ID',
    `conversation_id` BIGINT NOT NULL COMMENT '对话ID',
    `role` ENUM('user', 'assistant', 'system') DEFAULT 'user' COMMENT '消息角色：user=用户,assistant=AI,system=系统',
    `content` TEXT NOT NULL COMMENT '用户问题内容',
    `ai_response` TEXT COMMENT 'AI回复内容（合并存储）',
    `thinking_content` TEXT COMMENT 'AI推理过程（深度思考内容）',
    `token_count` INT DEFAULT 0 COMMENT '消耗token数量（便于统计和计费）',
    `model` VARCHAR(64) DEFAULT 'glm-5.1' COMMENT '使用的AI模型',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间（用户提问时间）',
    `responded_at` DATETIME COMMENT 'AI回复时间',
    PRIMARY KEY (`id`),
    KEY `idx_conversation` (`conversation_id`) COMMENT '按对话查询索引',
    KEY `idx_tenant_user` (`tenant_id`, `user_id`) COMMENT '按租户+用户查询索引',
    KEY `idx_conversation_created` (`conversation_id`, `created_at`) COMMENT '按对话+创建时间排序索引',
    CONSTRAINT `fk_message_conversation` FOREIGN KEY (`conversation_id`) REFERENCES `ai_conversations` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='AI对话消息表（合并存储）';

-- ---------------------------------------------
-- 3. 修改 user 表增加租户字段和角色字段
-- ---------------------------------------------
-- 添加租户ID字段
ALTER TABLE `user` ADD COLUMN `tenant_id` VARCHAR(64) DEFAULT 'default' COMMENT '所属租户ID' AFTER `password`;

-- 添加角色字段（admin=管理员，user=普通用户）
ALTER TABLE `user` ADD COLUMN `role` ENUM('admin', 'user') DEFAULT 'user' COMMENT '用户角色：admin=管理员，user=普通用户' AFTER `tenant_id`;

-- 为 user 表添加索引
ALTER TABLE `user` ADD INDEX `idx_tenant` (`tenant_id`);
ALTER TABLE `user` ADD INDEX `idx_role` (`role`);

-- ---------------------------------------------
-- 4. 已有数据库升级脚本（如果表已存在）
-- ---------------------------------------------
-- 为 ai_messages 表添加 ai_response 字段（合并存储AI回复）
-- ALTER TABLE `ai_messages` ADD COLUMN `ai_response` TEXT COMMENT 'AI回复内容（合并存储）' AFTER `content`;

-- 为 ai_messages 表添加 responded_at 字段（AI回复时间）
-- ALTER TABLE `ai_messages` ADD COLUMN `responded_at` DATETIME COMMENT 'AI回复时间' AFTER `created_at`;

-- 修改 content 字段注释
-- ALTER TABLE `ai_messages` MODIFY COLUMN `content` TEXT NOT NULL COMMENT '用户问题内容';
