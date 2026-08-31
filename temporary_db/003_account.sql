-- =====================================================================
-- Account 스키마/시드 분리 파일
-- 실행 순서: 001_schema.sql -> 002_seed.sql -> 003_account.sql
-- =====================================================================

BEGIN;

CREATE TABLE IF NOT EXISTS account (
  account_id VARCHAR(100) PRIMARY KEY,
  password_hash VARCHAR(255) NOT NULL,
  display_name VARCHAR(100),
  is_active BOOLEAN NOT NULL DEFAULT TRUE
);

-- 기본 로그인 계정 (id: enscape / pw: enscape123!)
-- PBKDF2 해시값은 backend/app/security.py 형식과 호환됩니다.
INSERT INTO account (account_id, password_hash, display_name, is_active)
VALUES (
  'enscape',
  'pbkdf2_sha256$120000$2eI4lkIN0s0y-UPf3f__tQ==$szyIeBVMQoAuTCm3IrBE7Xc0IzsEifqB1NyfttSKv6Q=',
  'enscape',
  TRUE
)
ON CONFLICT (account_id) DO UPDATE
SET
  password_hash = EXCLUDED.password_hash,
  display_name = EXCLUDED.display_name,
  is_active = EXCLUDED.is_active;

COMMIT;
