-- =====================================================================
-- 트러블슈팅 CaseDB — Phase 1 스키마 (PostgreSQL)
-- 실행 순서: 001_schema.sql → 002_seed.sql
-- =====================================================================

BEGIN;

-- ---------------------------------------------------------------------
-- 1. 코드/마스터 테이블 (드롭다운 옵션, FK가 참조하는 대상)
-- ---------------------------------------------------------------------

CREATE TABLE project (
  project_id   SERIAL PRIMARY KEY,
  project_name VARCHAR(200) NOT NULL
);

CREATE TABLE occurrence_phase (
  phase_id   SERIAL PRIMARY KEY,
  phase_name VARCHAR(50) NOT NULL
);

CREATE TABLE location (
  location_id   SERIAL PRIMARY KEY,
  location_name VARCHAR(100) NOT NULL
);

CREATE TABLE responsible_dept (
  dept_id   SERIAL PRIMARY KEY,
  dept_name VARCHAR(100) NOT NULL
);

CREATE TABLE tech_dept (
  dept_id   SERIAL PRIMARY KEY,
  dept_name VARCHAR(100) NOT NULL
);

CREATE TABLE production_tech_owner (
  owner_id   SERIAL PRIMARY KEY,
  owner_name VARCHAR(100) NOT NULL
);

CREATE TABLE status (
  status_id   SERIAL PRIMARY KEY,
  status_name VARCHAR(50) NOT NULL
);

CREATE TABLE priority (
  priority_id   SERIAL PRIMARY KEY,
  priority_name VARCHAR(50) NOT NULL
);

-- ---------------------------------------------------------------------
-- 2. Issue 메인 테이블
-- ---------------------------------------------------------------------

CREATE TABLE issue (
  issue_id                  SERIAL PRIMARY KEY,
  project_id                INTEGER REFERENCES project(project_id),
  issue_description         TEXT NOT NULL,
  occurred_date              DATE NOT NULL,
  phase_id                  INTEGER REFERENCES occurrence_phase(phase_id),
  location_id               INTEGER REFERENCES location(location_id),
  root_cause                 TEXT,
  responsible_dept_id       INTEGER REFERENCES responsible_dept(dept_id),
  tech_dept_id               INTEGER REFERENCES tech_dept(dept_id),
  production_tech_owner_id  INTEGER REFERENCES production_tech_owner(owner_id),
  status_id                 INTEGER NOT NULL REFERENCES status(status_id),
  temp_action                 TEXT,
  is_long_term               BOOLEAN NOT NULL DEFAULT FALSE,
  priority_id                INTEGER REFERENCES priority(priority_id),
  completed_date              DATE,
  root_countermeasure         TEXT,
  purchase_request_no         VARCHAR(50),
  object_insert               TEXT,
  created_at                  TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at                  TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ---------------------------------------------------------------------
-- 3. 이미지 테이블 (Issue : Image = 1:N)
-- ---------------------------------------------------------------------

CREATE TABLE issue_image (
  image_id   SERIAL PRIMARY KEY,
  issue_id   INTEGER NOT NULL REFERENCES issue(issue_id) ON DELETE CASCADE,
  image_path VARCHAR(500) NOT NULL
);

-- ---------------------------------------------------------------------
-- 4. 필드 메타데이터 테이블 (목록/상세 화면 노출 및 입력 타입 제어)
-- ---------------------------------------------------------------------

CREATE TABLE issue_field_config (
  field_key     VARCHAR(100) PRIMARY KEY,
  label         VARCHAR(100) NOT NULL,
  show_in_list  BOOLEAN NOT NULL DEFAULT FALSE,
  list_order    INTEGER,
  detail_order  INTEGER,
  input_type    VARCHAR(20) NOT NULL,
  option_source VARCHAR(100)
);

-- ---------------------------------------------------------------------
-- 인덱스 (자주 필터/정렬에 쓰이는 컬럼)
-- ---------------------------------------------------------------------

CREATE INDEX idx_issue_status_id ON issue(status_id);
CREATE INDEX idx_issue_priority_id ON issue(priority_id);
CREATE INDEX idx_issue_responsible_dept_id ON issue(responsible_dept_id);
CREATE INDEX idx_issue_project_id ON issue(project_id);
CREATE INDEX idx_issue_occurred_date ON issue(occurred_date);
CREATE INDEX idx_issue_image_issue_id ON issue_image(issue_id);

COMMIT;