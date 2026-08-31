BEGIN;

-- project
INSERT INTO project (project_id, project_name) VALUES (1, '예시 프로젝트 A');
INSERT INTO project (project_id, project_name) VALUES (2, '예시 프로젝트 B');

-- occurrence_phase
INSERT INTO occurrence_phase (phase_id, phase_name) VALUES (1, 'Part(입고)');
INSERT INTO occurrence_phase (phase_id, phase_name) VALUES (2, '제조(조립)');
INSERT INTO occurrence_phase (phase_id, phase_name) VALUES (3, 'Turn On(출하)');

-- location
INSERT INTO location (location_id, location_name) VALUES (1, '본사');
INSERT INTO location (location_id, location_name) VALUES (2, '고객사Site');

-- responsible_dept
INSERT INTO responsible_dept (dept_id, dept_name) VALUES (1, '설계');
INSERT INTO responsible_dept (dept_id, dept_name) VALUES (2, '제어');
INSERT INTO responsible_dept (dept_id, dept_name) VALUES (3, '비전');
INSERT INTO responsible_dept (dept_id, dept_name) VALUES (4, '선행개발');
INSERT INTO responsible_dept (dept_id, dept_name) VALUES (5, '연구소');

-- tech_dept
INSERT INTO tech_dept (dept_id, dept_name) VALUES (1, '설계');
INSERT INTO tech_dept (dept_id, dept_name) VALUES (2, '제어');
INSERT INTO tech_dept (dept_id, dept_name) VALUES (3, '비전');
INSERT INTO tech_dept (dept_id, dept_name) VALUES (4, '선행개발');
INSERT INTO tech_dept (dept_id, dept_name) VALUES (5, '연구소');

-- production_tech_owner
INSERT INTO production_tech_owner (owner_id, owner_name) VALUES (1, '홍길동');
INSERT INTO production_tech_owner (owner_id, owner_name) VALUES (2, '김철수');

-- status
INSERT INTO status (status_id, status_name) VALUES (1, '접수');
INSERT INTO status (status_id, status_name) VALUES (2, '원인분석중');
INSERT INTO status (status_id, status_name) VALUES (3, '조치진행중');
INSERT INTO status (status_id, status_name) VALUES (4, '효과검증중');
INSERT INTO status (status_id, status_name) VALUES (5, '종결');

-- priority
INSERT INTO priority (priority_id, priority_name) VALUES (1, '중요');
INSERT INTO priority (priority_id, priority_name) VALUES (2, '일반');

-- issue
INSERT INTO issue (issue_id, project_id, author, approval_yn, approved_by, approved_message, issue_description, occurred_date, phase_id, location_id, root_cause, responsible_dept_id, tech_dept_id, production_tech_owner_id, status_id, temp_action, is_long_term, priority_id, completed_date, root_countermeasure, purchase_request_no, object_insert) VALUES (1, 1, '홍길동', TRUE, '관리자', '검토 완료', '비전 카메라 초점 불량으로 검사 이미지 흐림 발생', '2026-03-10', 2, 1, '렌즈 마운트 나사 풀림', 3, 3, 1, 3, '렌즈 마운트 재조립 및 초점 재조정', FALSE, 1, NULL, NULL, NULL, NULL);
INSERT INTO issue (issue_id, project_id, author, approval_yn, approved_by, approved_message, issue_description, occurred_date, phase_id, location_id, root_cause, responsible_dept_id, tech_dept_id, production_tech_owner_id, status_id, temp_action, is_long_term, priority_id, completed_date, root_countermeasure, purchase_request_no, object_insert) VALUES (2, 2, '김철수', FALSE, NULL, NULL, '고객사 Site 출하 검사 중 조명 밝기 불균일', '2026-04-02', 3, 2, '조명 드라이버 노후화로 출력 저하', 1, 2, 2, 5, '조명 드라이버 임시 교체', TRUE, 2, '2026-04-15', '조명 드라이버 정기 교체 주기 수립', 'PR-2026-0142', NULL);

-- issue_image
INSERT INTO issue_image (image_id, issue_id, image_path) VALUES (1, 1, '/uploads/issue_1/photo_1.jpg');
INSERT INTO issue_image (image_id, issue_id, image_path) VALUES (2, 1, '/uploads/issue_1/photo_2.jpg');
INSERT INTO issue_image (image_id, issue_id, image_path) VALUES (3, 2, '/uploads/issue_2/photo_1.jpg');

-- issue_field_config
INSERT INTO issue_field_config (field_key, label, show_in_list, list_order, detail_order, input_type, option_source) VALUES ('author', '작성자', TRUE, 0, 1, 'text', NULL);
INSERT INTO issue_field_config (field_key, label, show_in_list, list_order, detail_order, input_type, option_source) VALUES ('project_id', '프로젝트명', FALSE, NULL, 2, 'dropdown', 'project');
INSERT INTO issue_field_config (field_key, label, show_in_list, list_order, detail_order, input_type, option_source) VALUES ('occurred_date', '발생일자', TRUE, 5, 3, 'date', NULL);
INSERT INTO issue_field_config (field_key, label, show_in_list, list_order, detail_order, input_type, option_source) VALUES ('phase_id', '발생시점', FALSE, NULL, 4, 'dropdown', 'occurrence_phase');
INSERT INTO issue_field_config (field_key, label, show_in_list, list_order, detail_order, input_type, option_source) VALUES ('location_id', '발생위치', FALSE, NULL, 5, 'dropdown', 'location');
INSERT INTO issue_field_config (field_key, label, show_in_list, list_order, detail_order, input_type, option_source) VALUES ('issue_description', '이슈내용', TRUE, 1, 6, 'textarea', NULL);
INSERT INTO issue_field_config (field_key, label, show_in_list, list_order, detail_order, input_type, option_source) VALUES ('responsible_dept_id', '책임부서', TRUE, 4, 6, 'dropdown', 'responsible_dept');
INSERT INTO issue_field_config (field_key, label, show_in_list, list_order, detail_order, input_type, option_source) VALUES ('tech_dept_id', '기술부서', FALSE, NULL, 7, 'dropdown', 'tech_dept');
INSERT INTO issue_field_config (field_key, label, show_in_list, list_order, detail_order, input_type, option_source) VALUES ('production_tech_owner_id', '생산기술담당자', FALSE, NULL, 8, 'dropdown', 'production_tech_owner');
INSERT INTO issue_field_config (field_key, label, show_in_list, list_order, detail_order, input_type, option_source) VALUES ('status_id', '현재상태', TRUE, 2, 9, 'dropdown', 'status');
INSERT INTO issue_field_config (field_key, label, show_in_list, list_order, detail_order, input_type, option_source) VALUES ('approval_yn', '승인상태', TRUE, 3, 999, 'boolean', NULL);
INSERT INTO issue_field_config (field_key, label, show_in_list, list_order, detail_order, input_type, option_source) VALUES ('priority_id', '우선순위', TRUE, 4, 10, 'dropdown', 'priority');
INSERT INTO issue_field_config (field_key, label, show_in_list, list_order, detail_order, input_type, option_source) VALUES ('is_long_term', '장기이슈여부', FALSE, NULL, 11, 'boolean', NULL);
INSERT INTO issue_field_config (field_key, label, show_in_list, list_order, detail_order, input_type, option_source) VALUES ('root_cause', '발생원인', FALSE, NULL, 12, 'textarea', NULL);
INSERT INTO issue_field_config (field_key, label, show_in_list, list_order, detail_order, input_type, option_source) VALUES ('temp_action', '임시조치내용', FALSE, NULL, 13, 'textarea', NULL);
INSERT INTO issue_field_config (field_key, label, show_in_list, list_order, detail_order, input_type, option_source) VALUES ('root_countermeasure', '근본대책', FALSE, NULL, 14, 'textarea', NULL);
INSERT INTO issue_field_config (field_key, label, show_in_list, list_order, detail_order, input_type, option_source) VALUES ('completed_date', '완료일자', FALSE, NULL, 15, 'date', NULL);
INSERT INTO issue_field_config (field_key, label, show_in_list, list_order, detail_order, input_type, option_source) VALUES ('purchase_request_no', '구매의뢰번호', FALSE, NULL, 16, 'text', NULL);
INSERT INTO issue_field_config (field_key, label, show_in_list, list_order, detail_order, input_type, option_source) VALUES ('object_insert', '개체삽입', FALSE, NULL, 17, 'text', NULL);

-- SERIAL 시퀀스를 지금까지 삽입한 최대 id에 맞춰 보정
SELECT setval(pg_get_serial_sequence('project', 'project_id'), COALESCE((SELECT MAX(project_id) FROM project), 1), true);
SELECT setval(pg_get_serial_sequence('occurrence_phase', 'phase_id'), COALESCE((SELECT MAX(phase_id) FROM occurrence_phase), 1), true);
SELECT setval(pg_get_serial_sequence('location', 'location_id'), COALESCE((SELECT MAX(location_id) FROM location), 1), true);
SELECT setval(pg_get_serial_sequence('responsible_dept', 'dept_id'), COALESCE((SELECT MAX(dept_id) FROM responsible_dept), 1), true);
SELECT setval(pg_get_serial_sequence('tech_dept', 'dept_id'), COALESCE((SELECT MAX(dept_id) FROM tech_dept), 1), true);
SELECT setval(pg_get_serial_sequence('production_tech_owner', 'owner_id'), COALESCE((SELECT MAX(owner_id) FROM production_tech_owner), 1), true);
SELECT setval(pg_get_serial_sequence('status', 'status_id'), COALESCE((SELECT MAX(status_id) FROM status), 1), true);
SELECT setval(pg_get_serial_sequence('priority', 'priority_id'), COALESCE((SELECT MAX(priority_id) FROM priority), 1), true);
SELECT setval(pg_get_serial_sequence('issue', 'issue_id'), COALESCE((SELECT MAX(issue_id) FROM issue), 1), true);
SELECT setval(pg_get_serial_sequence('issue_image', 'image_id'), COALESCE((SELECT MAX(image_id) FROM issue_image), 1), true);

COMMIT;