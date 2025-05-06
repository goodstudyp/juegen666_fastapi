from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "user" (
    "create_time" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "update_time" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "id" SERIAL NOT NULL PRIMARY KEY,
    "username" VARCHAR(20) NOT NULL UNIQUE,
    "password" VARCHAR(255) NOT NULL,
    "nickname" VARCHAR(20),
    "user_type" INT NOT NULL  DEFAULT 2,
    "user_email" VARCHAR(255)  UNIQUE,
    "user_status" INT NOT NULL  DEFAULT 1,
    "user_phone" VARCHAR(11)  UNIQUE,
    "login_time" TIMESTAMPTZ,
    "avatar" VARCHAR(255),
    "sex" INT,
    "remarks" VARCHAR(255),
    "client_host" VARCHAR(45)
);
CREATE INDEX IF NOT EXISTS "idx_user_usernam_9987ab" ON "user" ("username");
CREATE INDEX IF NOT EXISTS "idx_user_user_em_29aac0" ON "user" ("user_email");
CREATE INDEX IF NOT EXISTS "idx_user_user_ph_6314ba" ON "user" ("user_phone");
COMMENT ON COLUMN "user"."create_time" IS '创建时间';
COMMENT ON COLUMN "user"."update_time" IS '更新时间';
COMMENT ON COLUMN "user"."username" IS '用户名';
COMMENT ON COLUMN "user"."password" IS '密码哈希';
COMMENT ON COLUMN "user"."nickname" IS '昵称';
COMMENT ON COLUMN "user"."user_type" IS '用户类型 超级管理员0 管理员1 普通2';
COMMENT ON COLUMN "user"."user_email" IS '邮箱';
COMMENT ON COLUMN "user"."user_status" IS '0未激活 1正常 2禁用';
COMMENT ON COLUMN "user"."user_phone" IS '手机号';
COMMENT ON COLUMN "user"."login_time" IS '最后登录时间';
COMMENT ON COLUMN "user"."avatar" IS '头像URL';
COMMENT ON COLUMN "user"."sex" IS '性别 1男 2女 0未知';
COMMENT ON COLUMN "user"."remarks" IS '备注';
COMMENT ON COLUMN "user"."client_host" IS '最后登录IP';
COMMENT ON TABLE "user" IS '用户模型 (Tortoise ORM version)';
CREATE TABLE IF NOT EXISTS "test_table1" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(255) NOT NULL,
    "description" TEXT,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP
);
COMMENT ON TABLE "test_table1" IS '测试表';
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSONB NOT NULL
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
