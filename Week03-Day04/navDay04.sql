-- Generated from database settings workbook
-- Source file: 데이터베이스 설정.xlsx
-- Source sheets: place_data, road_data, waypoint_data

CREATE DATABASE IF NOT EXISTS nav DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE nav;

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS road_data;
DROP TABLE IF EXISTS waypoint_data;
DROP TABLE IF EXISTS place_data;
SET FOREIGN_KEY_CHECKS = 1;

CREATE TABLE place_data (
    place_id VARCHAR(255) NOT NULL,
    place_name VARCHAR(255) NULL,
    latitude DOUBLE NULL,
    longitude DOUBLE NULL,
    altitude DOUBLE NULL,
    PRIMARY KEY (place_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE waypoint_data (
    place_id VARCHAR(255) NOT NULL,
    place_name VARCHAR(255) NULL,
    latitude DOUBLE NULL,
    longitude DOUBLE NULL,
    PRIMARY KEY (place_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE road_data (
    road_id INT NOT NULL AUTO_INCREMENT,
    from_place VARCHAR(255) NOT NULL,
    to_place VARCHAR(255) NOT NULL,
    road_type VARCHAR(255) NULL,
    distance INT NULL,
    `time` INT NULL,
    twoway BOOLEAN NOT NULL DEFAULT 0,
    indoor BOOLEAN NOT NULL DEFAULT 0,
    stair BOOLEAN NOT NULL DEFAULT 0,
    slope INT NULL,
    curve INT NULL,
    PRIMARY KEY (road_id),
    INDEX idx_road_from_place (from_place),
    INDEX idx_road_to_place (to_place)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO place_data (place_id, place_name, latitude, longitude, altitude) VALUES
    ('GATE', '정문', 35.1137542, 128.9657807, NULL),
    ('BS31', '동아대학교정문(하단역방향) 버스정류장', 35.1137168, 128.9653213, NULL),
    ('S31', '수위실', 35.1138723, 128.965961, NULL),
    ('S01', '대학본부 및 인문과학대학', 35.114667, 128.9655648, NULL),
    ('S01-B1F', '대학본부 및 인문과학대학 지하 출입구(카페 앞)', 35.1145705, 128.9656752, NULL),
    ('S01-01F', '대학본부 및 인문과학대학 출입구(청촌홀 앞)', 35.114799, 128.9658282, NULL),
    ('S01-02F', '대학본부 및 인문과학대학 출입구(부산은행 앞)', 35.1149076, 128.9658027, NULL),
    ('S01-03F', '대학본부 및 인문과학대학(서점방향)', 35.1149184, 128.9655033, NULL),
    ('S01-04F', '대학본부 및 인문과학대학 4층(S02방향)', 35.1149692, 128.9656818, NULL),
    ('EL01', '대학본부 및 인문과학대학 엘리베이터', 35.1146257, 128.9653431, NULL),
    ('BS01', '대학본부 버스정류장', 35.1145013, 128.9656515, NULL),
    ('PL01', '대학본부 및 인문과학대학 주차장', 35.1151173, 128.9656982, NULL),
    ('S02', '학생회관', 35.1154974, 128.9659497, NULL),
    ('S02-B1F01E', '학생회관 지하1층 출입구(보건실, 서점)', 35.1152517, 128.9659909, NULL),
    ('S02-B1F02E', '학생회관 지하1층 출입구(S01방향)', 35.1153183, 128.9657487, NULL),
    ('S02-01F01E', '학생회관 1층 출입구(학생식당)', 35.1153703, 128.9660601, NULL),
    ('S02-01F02E', '학생회관 1층 출입구(동편계단)', 35.1155265, 128.9661124, NULL),
    ('S02-02F', '학생회관 2층 출입구(S01방향)', 35.1152835, 128.9659788, NULL),
    ('S02-03F', '학생회관 3층 출입구(S03방향)', 35.1156861, 128.9661518, NULL),
    ('ST02', '계단', 35.1154974, 128.9659497, NULL),
    ('S03', '공대1호관', 35.115911, 128.9664875, NULL),
    ('S03-01F01E', '공대1호관 1층 출입구1', 35.1158947, 128.9665429, NULL),
    ('S03-01F02E', '공대1호관 1층 출입구2', 35.1160088, 128.9667139, NULL),
    ('S03-01F03E', '공대 1호관 1층 출입구3(먹방라운지)', 35.1156998, 128.966158, NULL),
    ('S03-01F04E', '공대1호관 1층 뒷편 출입구(S02방향)', 35.1158962, 128.966319, NULL),
    ('S03-02F', '공대1호관 2층 뒷편 출입구(하늘정원방향)', 35.1160975, 128.9666147, NULL),
    ('S03-03F', '공대1호관 3층 S04방향 통로', 35.1161365, 128.9667555, NULL),
    ('ST03', '계단', 35.115911, 128.9664875, NULL),
    ('PL03', '공대1호관 주차장', 35.1159991, 128.9667242, NULL),
    ('S04', '공대2호관', 35.1165089, 128.9673645, NULL),
    ('S04-B1F', '공대2호관 지하1층 출입구', 35.1161852, 128.9673784, NULL),
    ('S04-01F01E', '공대2호관 1층 S03방향 통로', 35.1162818, 128.9669634, NULL),
    ('S04-01F02E', '공대2호관 1층 S05방향 출입구', 35.1166377, 128.9677157, NULL),
    ('S04-04F', '공대2호관 1층 하늘정원방향 출입구', 35.1166511, 128.9672348, NULL),
    ('EL04', '공대2호관 엘리베이터', 35.1165432, 128.9675056, NULL),
    ('BS04', '공대2호관 버스정류장', 35.1160491, 128.9669632, NULL),
    ('PL04', '공대2호관 주차장', 35.1163664, 128.9677508, NULL),
    ('S05', '공대3호관', 35.1167415, 128.9680056, NULL),
    ('S05-01F01E', '공대 4호관 1층 출입구(S06방향)', 35.1169996, 128.9678248, NULL),
    ('S05-01F02E', '공대 4호관 1층 출입구(흡연장)', 35.1167182, 128.9678932, NULL),
    ('S05-04F01E', '공대 4호관 4층 S12방향 입구', 35.1164983, 128.9682634, NULL),
    ('S05-04F', '공대 4호관 4층 S06방향 입구', 35.1170078, 128.9677953, NULL),
    ('S06', '공대5호관', 35.1172636, 128.9678098, NULL),
    ('PL06-01', '공대 5호관 지하주차장 출입구(S04 방향)', 35.1168636, 128.9675066, NULL),
    ('PL06-02', '공대 5호관 지하주차장 출입구(S05 방향)', 35.1170259, 128.9680658, NULL),
    ('S06-03F', '공대 5호관 3층 통로(CR05과 연결)', 35.1170968, 128.9677385, NULL),
    ('S06-04F', '공대 5호관 4층 출입구(야외정원 방향)', 35.1168739, 128.9672012, NULL),
    ('S06-06F01E', '공대 5호관 6층 출입구(정문)', 35.1173935, 128.9681542, NULL),
    ('S06-06F02E', '공대 5호관 6층 출입구(흡연장, 주차장)', 35.1174699, 128.9679079, NULL),
    ('S06-06F03E', '공대 5호관 6층 출입구(버스정류장)', 35.1171378, 128.9683784, NULL),
    ('EL06', '공대5호관 엘리베이터', 35.117408, 128.9679435, NULL),
    ('BS06', '산학협력관 버스정류장', 35.1172815, 128.9683187, NULL),
    ('PL06-03', '공대5호관 지상주차장', 35.1174768, 128.9678338, NULL),
    ('S07', '예술체육대학1관', 35.1141591, 128.966407, NULL),
    ('S07-01F', '예술체육대학1관 1층', 35.113978, 128.9661384, NULL),
    ('S07-04F', '예술체육대학1관 4층', 35.1145172, 128.9659782, NULL),
    ('S07-07F', '예술체육대학1관 7층', 35.114566, 128.9664898, NULL),
    ('EL07', '예술체육대학1관 엘리베이터', 35.1144201, 128.9661217, NULL),
    ('PL07', '예술체육대학1관 및 뉴턴공원 주차장', 35.1144106, 128.9669991, NULL),
    ('S08', '교수회관', 35.1141481, 128.9678956, NULL),
    ('S08-B1F', '정문 오른쪽 004번(다우 미디어센터) 입구', 35.1141294, 128.9678315, NULL),
    ('S08-01F', '정문 105번(출판부 사무실) 입구', 35.1142742, 128.9678208, NULL),
    ('S08-02F', '정문 옆 왼쪽 계단 대학일자리 센터 입구', 35.1144497, 128.9679173, NULL),
    ('S08-03F', '1층 입구 왼쪽 오르막길', 35.114283, 128.9680676, NULL),
    ('EL08', '교수회관 엘리베이터', 35.1142084, 128.9680193, NULL),
    ('S09', '생명자연과학대학 및 건강과학대학', 35.1148041, 128.9683918, NULL),
    ('S09-01F01E', '생명자연과학대학 및 건강과학대학 1층 정문', 35.1148965, 128.9683418, NULL),
    ('S09-01F02E', '생명자연과학대학 및 건강과학대학 1층 뒷문', 35.1147194, 128.9683908, NULL),
    ('S09-02F', '생명자연과학대학 및 건강과학대학 2층 쪽문', 35.1151955, 128.9682674, NULL),
    ('S09-03F01E', '생명자연과학대학 및 건강과학대학 3층 출입구(S17 방향)', 35.1148532, 128.9686355, NULL),
    ('S09-03F02E', '생명자연과학대학 및 건강과학대학 3층 출입구(S11 방향)', 35.1152646, 128.9683284, NULL),
    ('EL09', '생명자연과학대학 및 건강과학대학 엘리베이터', 35.1149646, 128.9684504, NULL),
    ('S10', '한림도서관', 35.115447, 128.9675737, NULL),
    ('S10-01F01E', '한림도서관 서편 출입구', 35.1152303, 128.9677499, NULL),
    ('S10-02F', '한림도서관 2층 출입구(S11방향)', 35.1155203, 128.9677307, NULL),
    ('S11', '자연과학대학', 35.1157059, 128.9679975, NULL),
    ('S11-B1F', '자연과학대학 지하1층 출입구(버스정류장 방향)', 35.1160579, 128.9676438, NULL),
    ('S11-01F', '자연과학대학 1층 출입구(도서관 방향)', 35.1156586, 128.9678745, NULL),
    ('S11-04F01E', '자연과학대학 4층 1번 출입구(S12 방향)', 35.1157628, 128.9681387, NULL),
    ('S11-04F02E', '자연과학대학 4층 2번 출입구(S12 방향)', 35.1157732, 128.9681038, NULL),
    ('S11-03F', '자연과학대학 3층 출입구(S09 방향)', 35.1153135, 128.9682922, NULL),
    ('BS11', ' 공과대학 버스정류장', 35.1160458, 128.9675606, NULL),
    ('S12', '공과대학4호관', 35.1160547, 128.968306, NULL),
    ('S12-B2F', '공과대학 4호관 지하주차장 출입구', 35.1163974, 128.9680689, NULL),
    ('S12-B1F', '공과대학 4호관 지하1층 출입구(흡연실)', 35.1159712, 128.9681085, NULL),
    ('S12-01F', '공과대학 4호관 1층 출입구(정문)', 35.1162439, 128.968249, NULL),
    ('S12-02F', '공과대학 4호관 2층 출입구', 35.1158873, 128.9684283, NULL),
    ('S12-04F', '공과대학 4호관 4층 출입구(승학산 방면)', 35.1161966, 128.9684585, NULL),
    ('EL12', '공과대학 4호관 엘리베이터', 35.1161017, 128.9683559, NULL),
    ('S13', '창업관', 35.1162945, 128.9698374, NULL),
    ('S14', '산학관', 35.1172686, 128.9694216, NULL),
    ('S15', '한림생활관 승학1관', 35.1186392, 128.9694701, NULL),
    ('S15-01F', '한림생활관 승학1관 1층 출입구(계단)', 35.1183119, 128.9695556, NULL),
    ('S15-B1F01E', '한림생활관 승학1관 지하1층 출입구(E동)', 35.118901, 128.9689441, NULL),
    ('S15-B1F02E', '한림생활관 승학1관 지하1층 출입구(F동)', 35.1190217, 128.9690996, NULL),
    ('S15-B1F03E', '한림생활관 승학1관 지하1층 출입구(D동)', 35.1185653, 128.9696226, NULL),
    ('S15-B1F04E', '한림생활관 승학1관 지하1층 출입구(테라스)', 35.1187891, 128.9688609, NULL),
    ('S15-B1F05E', '한림생활관 승학1관 지하1층 출입구(행정실)', 35.1184219, 128.969388, NULL),
    ('BS15', '생활관 버스정류장', 35.1180595, 128.9692505, NULL),
    ('S16', '학생군사교육단(ROTC)', 35.1191724, 128.9687566, NULL),
    ('S17', '예술체육대학2관', 35.1153877, 128.9687619, NULL),
    ('S17-01F', '예술체육대학2관 1층 출입구(정문)', 35.1154718, 128.9686429, NULL),
    ('S17-04F01E', '예술체육대학2관 4층 출입구(주차장, S12방향)', 35.1158614, 128.9691289, NULL),
    ('S17-04F02E', '예술체육대학2관 4층 출입구(주차장, S12 반대방향)', 35.1149552, 128.9692711, NULL),
    ('S17-07F', '예술체육대학2관 7층(축구장)', 35.1158767, 128.9693408, NULL),
    ('EL17-01', '예술체육대학2관 엘리베이터', 35.1156454, 128.9687381, NULL),
    ('EL17-02', '예술체육대학2관 엘리베이터', 35.1154463, 128.9687314, NULL),
    ('S18', '예술체육대학 실습동', 35.1154631, 128.9691363, NULL),
    ('S19', '한림생활관 승학2관(S19)', 35.1180677, 128.9681519, NULL),
    ('S19-01F', '한림생활관 승학2관(S19) 1층(정문)', 35.1184269552, 128.9685437683, NULL),
    ('S19-08F', '한림생활관 승학2관(S19) 8층 (옆문)', 35.1186765, 128.9683425, NULL),
    ('PL19', '한림생활관 승학2관(S19) 주차장', 35.1180961, 128.9682989, NULL),
    ('S20', '한림생활관 승학2관(S20)', 35.1185043, 128.9684442, NULL),
    ('S20-B2F', '한림생활관 승학2관(S20) 지하2층(정문)', 35.1184269552, 128.9685437683, NULL),
    ('S20-06F', '한림생활관 승학2관(S20) 6층 (옆문)', 35.1186765, 128.9683425, NULL),
    ('S21', '고압수소시험동', 35.1160312, 128.9694565, NULL),
    ('S22', 'L2M Platform', 35.1165939, 128.9696818, NULL),
    ('CR00', NULL, 35.1137911, 128.9647939, NULL),
    ('CR01-01', NULL, 35.1147423, 128.9659342, NULL),
    ('CR01-02', NULL, 35.1149118, 128.9660503, NULL),
    ('CR01-03', NULL, 35.1150445, 128.9660543, NULL),
    ('CR01-04', NULL, 35.1145114, 128.9657391, NULL),
    ('CR02-01', NULL, 35.1152019, 128.9660952, NULL),
    ('CR02-02', NULL, 35.1155234, 128.9662863, NULL),
    ('CR03-01', NULL, 35.1159172, 128.9667953, NULL),
    ('CR03-02', NULL, 35.1159214, 128.9662935, NULL),
    ('CR03-03', NULL, 35.1161222, 128.9665684, NULL),
    ('CR04-01', NULL, 35.1160619, 128.9673637, NULL),
    ('CR04-02', NULL, 35.1161255, 128.9674549, NULL),
    ('CR04-03', NULL, 35.1162538, 128.9676373, NULL),
    ('CR05-01', NULL, 35.116448, 128.9679149, NULL),
    ('CR05-02', NULL, 35.1165303, 128.9684051, NULL),
    ('CR05-03', NULL, 35.1171391, 128.967927, NULL),
    ('CR05-04', NULL, 35.1166453, 128.9677252, NULL),
    ('CR06-01', NULL, 35.1174013, 128.9683152, NULL),
    ('CR06-02', NULL, 35.1171479, 128.9684279, NULL),
    ('CR06-03', NULL, 35.1177594, 128.9683132, NULL),
    ('CR07-01', NULL, 35.1136805, 128.9663284, NULL),
    ('CR07-02', NULL, 35.1136877, 128.966488, NULL),
    ('CR07-03', NULL, 35.1145049, 128.9675603, NULL),
    ('CR07-04', NULL, 35.11467, 128.9658927, NULL),
    ('CR07-05', NULL, 35.1141202, 128.9658172, NULL),
    ('CR08-01', NULL, 35.1149503, 128.9677688, NULL),
    ('CR09', NULL, 35.1151961, 128.9679686, NULL),
    ('CR10', NULL, 35.1149953, 128.9676038, NULL),
    ('CR11', NULL, 35.1155394, 128.9678036, NULL),
    ('CR14-01', NULL, 35.1170744, 128.9690429, NULL),
    ('CR14-02', NULL, 35.1179201, 128.9691716, NULL),
    ('CR15', NULL, 35.1183008, 128.9690187, NULL),
    ('CR18', NULL, 35.1158896, 128.9689061, NULL),
    ('CR21', NULL, 35.1162955, 128.9693245, NULL),
    ('CR22', NULL, 35.1169669, 128.9691073, NULL),
    ('CR23', NULL, 35.1156974, 128.9661353, NULL),
    ('CR46', NULL, 35.1167489, 128.9671284, NULL),
    ('CR78', NULL, 35.1141956, 128.9675609, NULL);

INSERT INTO waypoint_data (place_id, place_name, latitude, longitude) VALUES
    ('WP1', 'WP1', NULL, NULL),
    ('WP2', 'WP2', NULL, NULL),
    ('WP3', 'WP3', NULL, NULL),
    ('WP4', 'WP4', NULL, NULL),
    ('WP5', 'WP5', NULL, NULL),
    ('WP6', 'WP6', NULL, NULL),
    ('WP7', 'WP7', NULL, NULL),
    ('WP8', 'WP8', NULL, NULL),
    ('WP9', 'WP9', NULL, NULL),
    ('WP10', 'WP10', NULL, NULL),
    ('WP11', 'WP11', NULL, NULL),
    ('WP12', 'WP12', NULL, NULL),
    ('WP13', 'WP13', NULL, NULL),
    ('WP14', 'WP14', NULL, NULL),
    ('WP15', 'WP15', NULL, NULL),
    ('WP16', 'WP16', NULL, NULL),
    ('WP17', 'WP17', NULL, NULL),
    ('WP18', 'WP18', NULL, NULL),
    ('WP19', 'WP19', NULL, NULL),
    ('WP20', 'WP20', NULL, NULL),
    ('WP21', 'WP21', NULL, NULL),
    ('WP22', 'WP22', NULL, NULL),
    ('WP23', 'WP23', NULL, NULL),
    ('WP24', 'WP24', NULL, NULL),
    ('WP25', 'WP25', NULL, NULL),
    ('WP26', 'WP26', NULL, NULL),
    ('WP27', 'WP27', NULL, NULL),
    ('WP28', 'WP28', NULL, NULL),
    ('WP29', 'WP29', NULL, NULL),
    ('WP30', 'WP30', NULL, NULL),
    ('WP31', 'WP31', NULL, NULL),
    ('WP32', 'WP32', NULL, NULL),
    ('WP33', 'WP33', NULL, NULL),
    ('WP34', 'WP34', NULL, NULL),
    ('WP35', 'WP35', NULL, NULL),
    ('WP36', 'WP36', NULL, NULL),
    ('WP37', 'WP37', NULL, NULL),
    ('WP38', 'WP38', NULL, NULL),
    ('WP39', 'WP39', NULL, NULL),
    ('WP40', 'WP40', NULL, NULL),
    ('WP41', 'WP41', NULL, NULL),
    ('WP42', 'WP42', NULL, NULL),
    ('WP43', 'WP43', NULL, NULL),
    ('WP44', 'WP44', NULL, NULL),
    ('WP45', 'WP45', NULL, NULL),
    ('WP46', 'WP46', NULL, NULL),
    ('WP47', 'WP47', NULL, NULL),
    ('WP48', 'WP48', NULL, NULL),
    ('WP49', 'WP49', NULL, NULL),
    ('WP50', 'WP50', NULL, NULL),
    ('WP51', 'WP51', NULL, NULL),
    ('WP52', 'WP52', NULL, NULL),
    ('WP53', 'WP53', NULL, NULL),
    ('WP54', 'WP54', NULL, NULL),
    ('WP55', 'WP55', NULL, NULL),
    ('WP56', 'WP56', NULL, NULL),
    ('WP57', 'WP57', NULL, NULL),
    ('WP58', 'WP58', NULL, NULL),
    ('WP59', 'WP59', NULL, NULL),
    ('WP60', 'WP60', NULL, NULL),
    ('WP61', 'WP61', NULL, NULL),
    ('WP62', 'WP62', NULL, NULL),
    ('WP63', 'WP63', NULL, NULL),
    ('WP64', 'WP64', NULL, NULL),
    ('WP65', 'WP65', NULL, NULL),
    ('WP66', 'WP66', NULL, NULL),
    ('WP67', 'WP67', NULL, NULL),
    ('WP68', 'WP68', NULL, NULL),
    ('WP69', 'WP69', NULL, NULL),
    ('WP70', 'WP70', NULL, NULL),
    ('WP71', 'WP71', NULL, NULL),
    ('WP72', 'WP72', NULL, NULL),
    ('WP73', 'WP73', NULL, NULL),
    ('WP74', 'WP74', NULL, NULL),
    ('WP75', 'WP75', NULL, NULL),
    ('WP76', 'WP76', NULL, NULL),
    ('WP77', 'WP77', NULL, NULL),
    ('WP78', 'WP78', NULL, NULL),
    ('WP79', 'WP79', NULL, NULL),
    ('WP80', 'WP80', NULL, NULL),
    ('WP81', 'WP81', NULL, NULL),
    ('WP82', 'WP82', NULL, NULL),
    ('WP83', 'WP83', NULL, NULL),
    ('WP84', 'WP84', NULL, NULL),
    ('WP85', 'WP85', NULL, NULL),
    ('WP86', 'WP86', NULL, NULL),
    ('WP87', 'WP87', NULL, NULL),
    ('WP88', 'WP88', NULL, NULL),
    ('WP89', 'WP89', NULL, NULL),
    ('WP90', 'WP90', NULL, NULL),
    ('WP91', 'WP91', NULL, NULL),
    ('WP92', 'WP92', NULL, NULL),
    ('WP93', 'WP93', NULL, NULL),
    ('WP94', 'WP94', NULL, NULL),
    ('WP95', 'WP95', NULL, NULL),
    ('WP96', 'WP96', NULL, NULL),
    ('WP97', 'WP97', NULL, NULL),
    ('WP98', 'WP98', NULL, NULL),
    ('WP99', 'WP99', NULL, NULL),
    ('WP100', 'WP100', NULL, NULL),
    ('WP101', 'WP101', NULL, NULL),
    ('WP102', 'WP102', NULL, NULL),
    ('WP103', 'WP103', NULL, NULL),
    ('WP104', 'WP104', NULL, NULL),
    ('WP105', 'WP105', NULL, NULL),
    ('WP106', 'WP106', NULL, NULL),
    ('WP107', 'WP107', NULL, NULL),
    ('WP108', 'WP108', NULL, NULL),
    ('WP109', 'WP109', NULL, NULL),
    ('WP110', 'WP110', NULL, NULL),
    ('WP111', 'WP111', NULL, NULL),
    ('WP112', 'WP112', NULL, NULL);

INSERT INTO road_data (road_id, from_place, to_place, road_type, distance, `time`, indoor, stair, slope) VALUES
    (1, 'GATE', 'CR07-01', '차량', 55, 10, 0, 0, NULL),
    (2, 'CR07-01', 'CR07-02', '차량', 10, 2, 0, 0, NULL),
    (3, 'CR07-02', 'CR07-03', '차량', 150, 27, 0, 0, NULL),
    (4, 'CR07-03', 'CR08-01', '차량', 70, 13, 0, 0, NULL),
    (5, 'CR08-01', 'CR09', '차량', 20, 4, 0, 0, NULL),
    (6, 'CR09', 'CR11', '차량', 40, 7, 0, 0, NULL),
    (7, 'CR11', 'CR04-01', '차량', 68, 12, 0, 0, NULL),
    (8, 'CR04-01', 'BS04', '차량', 30, 5, 0, 0, NULL),
    (9, 'BS04', 'CR03-01', '차량', 24, 4, 0, 0, NULL),
    (10, 'CR03-01', 'CR02-02', '차량', 65, 12, 0, 0, NULL),
    (11, 'CR02-02', 'CR02-01', '차량', 37, 7, 0, 0, NULL),
    (12, 'CR02-01', 'CR01-03', '차량', 20, 4, 0, 0, NULL),
    (13, 'CR01-03', 'CR01-02', '차량', 12, 2, 0, 0, NULL),
    (14, 'CR01-02', 'CR01-01', '차량', 23, 4, 0, 0, NULL),
    (15, 'CR01-01', 'CR07-04', '차량', 10, 2, 0, 0, NULL),
    (16, 'CR07-04', 'CR01-04', '차량', 22, 4, 0, 0, NULL),
    (17, 'CR01-04', 'BS01', '차량', 6, 1, 0, 0, NULL),
    (18, 'BS01', 'CR00', '차량', 110, 20, 0, 0, NULL),
    (19, 'CR00', 'BS31', '차량', 48, 9, 0, 0, NULL),
    (20, 'BS31', 'GATE', '차량', 40, 7, 0, 0, NULL),
    (21, 'CR07-03', 'PL07', '차량', 77, 14, 0, 0, NULL),
    (22, 'PL07', 'CR01-02', '차량', 117, 21, 0, 0, NULL),
    (23, 'CR03-01', 'PL03', '차량', 10, 2, 0, 0, NULL),
    (24, 'CR01-03', 'PL01', '차량', 42, 8, 0, 0, NULL),
    (25, 'CR04-01', 'BS11', '차량', 6, 1, 0, 0, NULL),
    (26, 'BS11', 'CR04-03', '차량', 18, 3, 0, 0, NULL),
    (27, 'CR04-03', 'CR05-02', '차량', 85, 15, 0, 0, NULL),
    (28, 'CR05-02', 'CR18', '차량', 80, 14, 0, 0, NULL),
    (29, 'CR18', 'CR21', '차량', 74, 13, 0, 0, NULL),
    (30, 'CR21', 'CR22', '차량', 70, 13, 0, 0, NULL),
    (31, 'CR22', 'CR14-01', '차량', 14, 3, 0, 0, NULL),
    (32, 'CR14-01', 'CR14-02', '차량', 100, 18, 0, 0, NULL),
    (33, 'CR14-02', 'BS15', '차량', 10, 2, 0, 0, NULL),
    (34, 'BS15', 'CR15', '차량', 30, 5, 0, 0, NULL),
    (35, 'CR15', 'CR06-03', '차량', 100, 18, 0, 0, NULL),
    (36, 'CR06-03', 'CR06-01', '차량', 42, 8, 0, 0, NULL),
    (37, 'CR06-01', 'BS06', '차량', 10, 2, 0, 0, NULL),
    (38, 'BS06', 'CR06-02', '차량', 10, 2, 0, 0, NULL),
    (39, 'CR06-02', 'CR05-02', '차량', 70, 13, 0, 0, NULL),
    (40, 'CR04-03', 'CR04-02', '차량', 18, 3, 0, 0, NULL),
    (41, 'CR04-02', 'CR04-01', '차량', 6, 1, 0, 0, NULL),
    (42, 'CR04-03', 'PL04', '차량', 20, 4, 0, 0, NULL),
    (43, 'PL04', 'CR05-01', '차량', 21, 4, 0, 0, NULL),
    (44, 'CR05-01', 'PL06-02', '차량', 70, 13, 0, 0, NULL),
    (45, 'PL06-02', 'CR05-03', '차량', 24, 4, 0, 0, NULL),
    (46, 'CR05-03', 'PL06-01', '차량', 47, 8, 0, 0, NULL),
    (47, 'PL06-01', 'CR05-04', '차량', 25, 4, 0, 0, NULL),
    (48, 'CR05-04', 'CR05-01', '차량', 32, 6, 0, 0, NULL),
    (49, 'GATE', 'CR07-01', '도보', 55, 98, 0, 0, NULL),
    (50, 'CR07-01', 'CR07-02', '도보', 10, 18, 0, 0, NULL),
    (51, 'CR07-02', 'CR07-03', '도보', 150, 268, 0, 0, NULL),
    (52, 'CR07-03', 'CR08-01', '도보', 70, 125, 0, 0, NULL),
    (53, 'CR08-01', 'CR09', '도보', 20, 36, 0, 0, NULL),
    (54, 'CR09', 'CR11', '도보', 40, 71, 0, 0, NULL),
    (55, 'CR11', 'CR04-01', '도보', 68, 121, 0, 0, NULL),
    (56, 'CR04-01', 'BS04', '도보', 30, 54, 0, 0, NULL),
    (57, 'BS04', 'CR03-01', '도보', 24, 43, 0, 0, NULL),
    (58, 'CR03-01', 'CR02-02', '도보', 65, 116, 0, 0, NULL),
    (59, 'CR02-02', 'CR02-01', '도보', 37, 66, 0, 0, NULL),
    (60, 'CR02-01', 'CR01-03', '도보', 20, 36, 0, 0, NULL),
    (61, 'CR01-03', 'CR01-02', '도보', 12, 21, 0, 0, NULL),
    (62, 'CR01-02', 'CR01-01', '도보', 23, 41, 0, 0, NULL),
    (63, 'CR01-01', 'CR07-04', '도보', 10, 18, 0, 0, NULL),
    (64, 'CR07-04', 'CR01-04', '도보', 22, 39, 0, 0, NULL),
    (65, 'CR01-04', 'BS01', '도보', 6, 11, 0, 0, NULL),
    (66, 'BS01', 'CR00', '도보', 110, 196, 0, 0, NULL),
    (67, 'CR00', 'BS31', '도보', 48, 86, 0, 0, NULL),
    (68, 'BS31', 'GATE', '도보', 40, 71, 0, 0, NULL),
    (69, 'CR07-03', 'PL07', '도보', 77, 138, 0, 0, NULL),
    (70, 'PL07', 'CR01-02', '도보', 117, 209, 0, 0, NULL),
    (71, 'CR03-01', 'PL03', '도보', 10, 18, 0, 0, NULL),
    (72, 'CR01-03', 'PL01', '도보', 42, 75, 0, 0, NULL),
    (73, 'CR04-01', 'BS11', '도보', 6, 11, 0, 0, NULL),
    (74, 'BS11', 'CR04-03', '도보', 18, 32, 0, 0, NULL),
    (75, 'CR04-03', 'CR05-02', '도보', 85, 152, 0, 0, NULL),
    (76, 'CR05-02', 'CR18', '도보', 80, 143, 0, 0, NULL),
    (77, 'CR18', 'CR21', '도보', 74, 132, 0, 0, NULL),
    (78, 'CR21', 'CR22', '도보', 70, 125, 0, 0, NULL),
    (79, 'CR22', 'CR14-01', '도보', 14, 25, 0, 0, NULL),
    (80, 'CR14-01', 'CR14-02', '도보', 100, 179, 0, 0, NULL),
    (81, 'CR14-02', 'BS15', '도보', 10, 18, 0, 0, NULL),
    (82, 'BS15', 'CR15', '도보', 30, 54, 0, 0, NULL),
    (83, 'CR15', 'CR06-03', '도보', 100, 179, 0, 0, NULL),
    (84, 'CR06-03', 'CR06-01', '도보', 42, 75, 0, 0, NULL),
    (85, 'CR06-01', 'BS06', '도보', 10, 18, 0, 0, NULL),
    (86, 'BS06', 'CR06-02', '도보', 10, 18, 0, 0, NULL),
    (87, 'CR06-02', 'CR05-02', '도보', 70, 125, 0, 0, NULL),
    (88, 'CR04-03', 'CR04-02', '도보', 18, 32, 0, 0, NULL),
    (89, 'CR04-02', 'CR04-01', '도보', 6, 11, 0, 0, NULL),
    (90, 'CR04-03', 'PL04', '도보', 20, 36, 0, 0, NULL),
    (91, 'PL04', 'CR05-01', '도보', 21, 37, 0, 0, NULL),
    (92, 'CR05-01', 'PL06-02', '도보', 70, 125, 0, 0, NULL),
    (93, 'PL06-02', 'CR05-03', '도보', 24, 43, 0, 0, NULL),
    (94, 'CR05-03', 'PL06-01', '도보', 47, 84, 0, 0, NULL),
    (95, 'PL06-01', 'CR05-04', '도보', 25, 45, 0, 0, NULL),
    (96, 'CR05-04', 'CR05-01', '도보', 32, 57, 0, 0, NULL),
    (97, 'CR07-01', 'S07-01F', '도보', 30, 54, 0, 0, NULL),
    (98, 'CR07-01', 'PL07', '도보', 90, 161, 0, 1, NULL),
    (99, 'GATE', 'CR07-05', '도보', 40, 71, 0, 1, NULL),
    (100, 'CR07-05', 'S07-01F', '도보', 40, 71, 0, 0, NULL),
    (101, 'S07-01F', 'EL07', '도보', 63, 112, 1, 0, NULL),
    (102, 'EL07', 'S07-04F', '도보', 32, 57, 1, 0, NULL),
    (103, 'EL07', 'S07-07F', '도보', 38, 68, 1, 0, NULL),
    (104, 'S07-04F', 'CR07-04', '도보', 20, 36, 0, 1, NULL),
    (105, 'GATE', 'CR01-04', '도보', 88, 157, 0, 1, NULL),
    (106, 'BS01', 'S01-B1F', '도보', 7, 12, 0, 1, NULL),
    (107, 'CR01-01', 'S01-01F', '도보', 17, 30, 0, 1, NULL),
    (108, 'CR01-02', 'S01-02F', '도보', 30, 54, 0, 0, NULL),
    (109, 'S01-B1F', 'EL01', '도보', 40, 71, 1, 0, NULL),
    (110, 'S01-01F', 'EL01', '도보', 30, 54, 1, 0, NULL),
    (111, 'S01-02F', 'EL01', '도보', 40, 71, 1, 0, NULL),
    (112, 'EL01', 'S01-03F', '도보', 30, 54, 1, 0, NULL),
    (113, 'EL01', 'S01-04F', '도보', 30, 54, 1, 0, NULL),
    (114, 'S01-03F', 'S02-B1F02E', '도보', 60, 107, 0, 0, NULL),
    (115, 'S01-04F', 'S02-02F', '도보', 45, 80, 1, 0, NULL),
    (116, 'S02-B1F01E', 'S02-B1F02E', '도보', 32, 57, 1, 0, NULL),
    (117, 'S02-B1F01E', 'ST02', '도보', 28, 50, 1, 1, NULL),
    (118, 'S02-B1F02E', 'ST02', '도보', 28, 50, 1, 1, NULL),
    (119, 'S02-01F01E', 'S02-01F02E', '도보', 20, 36, 1, 0, NULL),
    (120, 'S02-01F01E', 'ST02', '도보', 12, 21, 1, 1, NULL),
    (121, 'S02-01F02E', 'ST02', '도보', 10, 18, 1, 1, NULL),
    (122, 'S02-02F', 'ST02', '도보', 50, 89, 1, 1, NULL),
    (123, 'ST02', 'S02-03F', '도보', 28, 50, 1, 1, NULL),
    (124, 'CR02-01', 'S02-B1F01E', '도보', 12, 21, 0, 1, NULL),
    (125, 'CR02-02', 'S02-01F01E', '도보', 27, 48, 0, 1, NULL),
    (126, 'CR02-02', 'S02-01F02E', '도보', 15, 27, 0, 0, NULL),
    (127, 'S02-03F', 'CR23', '도보', 4, 7, 0, 1, NULL),
    (128, 'CR02-02', 'CR23', '도보', 45, 80, 0, 0, NULL),
    (129, 'CR02-02', 'CR03-02', '도보', 80, 143, 0, 0, NULL),
    (130, 'CR23', 'CR03-02', '도보', 85, 152, 0, 0, NULL),
    (131, 'CR23', 'S03-01F03E', '도보', 3, 5, 0, 0, NULL),
    (132, 'CR03-01', 'PL03', '도보', 10, 18, 0, 0, NULL),
    (133, 'PL03', 'S03-01F02E', '도보', 5, 9, 0, 0, NULL),
    (134, 'CR23', 'S03-01F01E', '도보', 63, 112, 0, 0, NULL),
    (135, 'CR03-02', 'S03-01F04E', '도보', 5, 9, 0, 0, NULL),
    (136, 'CR03-03', 'S03-02F', '도보', 5, 9, 0, 1, NULL),
    (137, 'S03-03F', 'S04-01F01E', '도보', 27, 48, 1, 0, NULL),
    (138, 'S03-01F01E', 'ST03', '도보', 20, 36, 1, 1, NULL),
    (139, 'S03-01F02E', 'ST03', '도보', 10, 18, 1, 1, NULL),
    (140, 'S03-01F03E', 'ST03', '도보', 40, 71, 1, 1, NULL),
    (141, 'S03-01F04E', 'ST03', '도보', 5, 9, 1, 1, NULL),
    (142, 'S03-02F', 'ST03', '도보', 2, 4, 1, 1, NULL),
    (143, 'S03-03F', 'ST03', '도보', 20, 36, 1, 1, NULL),
    (144, 'S03-01F01E', 'S03-01F02E', '도보', 25, 45, 1, 0, NULL),
    (145, 'S03-01F01E', 'S03-01F03E', '도보', 45, 80, 1, 0, NULL),
    (146, 'S03-01F01E', 'S03-01F04E', '도보', 28, 50, 1, 0, NULL),
    (147, 'S03-01F02E', 'S03-01F03E', '도보', 61, 109, 1, 0, NULL),
    (148, 'S03-01F02E', 'S03-01F04E', '도보', 43, 77, 1, 0, NULL),
    (149, 'S03-01F03E', 'S03-01F04E', '도보', 35, 62, 1, 0, NULL),
    (150, 'CR03-02', 'CR03-03', '도보', 34, 61, 0, 0, NULL),
    (151, 'CR03-03', 'CR46', '도보', 130, 232, 0, 1, NULL),
    (152, 'S04-01F01E', 'EL04', '도보', 78, 139, 1, 0, NULL),
    (153, 'EL04', 'S04-01F02E', '도보', 20, 36, 1, 0, NULL),
    (154, 'S04-B1F', 'EL04', '도보', 55, 98, 1, 1, NULL),
    (155, 'S04-B1F', 'S04-01F01E', '도보', 62, 111, 1, 1, NULL),
    (156, 'EL04', 'S04-04F', '도보', 80, 143, 1, 0, NULL),
    (157, 'S04-01F02E', 'CR05-04', '도보', 2, 4, 0, 0, NULL),
    (158, 'S04-04F', 'CR46', '도보', 15, 27, 0, 1, NULL),
    (159, 'PL06-01', 'EL06', '도보', 96, 171, 1, 0, NULL),
    (160, 'PL06-02', 'EL06', '도보', 55, 98, 1, 0, NULL),
    (161, 'CR46', 'S06-04F', '도보', 33, 59, 0, 1, NULL),
    (162, 'S06-04F', 'EL06', '도보', 107, 191, 1, 0, NULL),
    (163, 'S06-06F01E', 'EL06', '도보', 20, 36, 1, 0, NULL),
    (164, 'S06-06F02E', 'EL06', '도보', 55, 98, 1, 0, NULL),
    (165, 'S06-06F03E', 'EL06', '도보', 2, 4, 1, 1, NULL),
    (166, 'S06-06F01E', 'S06-06F02E', '도보', 60, 107, 1, 0, NULL),
    (167, 'S06-06F01E', 'S06-06F03E', '도보', 18, 32, 1, 1, NULL),
    (168, 'S06-06F02E', 'S06-06F03E', '도보', 57, 102, 1, 1, NULL),
    (169, 'S06-06F01E', 'CR06-01', '도보', 14, 25, 0, 0, NULL),
    (170, 'S06-06F02E', 'CR06-02', '도보', 9, 16, 0, 1, NULL),
    (171, 'S06-06F03E', 'PL06-03', '도보', 8, 14, 0, 0, NULL);

UPDATE road_data SET twoway = 0, curve = NULL WHERE road_id = 1;
UPDATE road_data SET twoway = 0, curve = NULL WHERE road_id = 2;
UPDATE road_data SET twoway = 0, curve = NULL WHERE road_id = 3;
UPDATE road_data SET twoway = 0, curve = NULL WHERE road_id = 4;
UPDATE road_data SET twoway = 0, curve = NULL WHERE road_id = 5;
UPDATE road_data SET twoway = 0, curve = NULL WHERE road_id = 6;
UPDATE road_data SET twoway = 0, curve = NULL WHERE road_id = 7;
UPDATE road_data SET twoway = 0, curve = NULL WHERE road_id = 8;
UPDATE road_data SET twoway = 0, curve = NULL WHERE road_id = 9;
UPDATE road_data SET twoway = 0, curve = NULL WHERE road_id = 10;
UPDATE road_data SET twoway = 0, curve = NULL WHERE road_id = 11;
UPDATE road_data SET twoway = 0, curve = NULL WHERE road_id = 12;
UPDATE road_data SET twoway = 0, curve = NULL WHERE road_id = 13;
UPDATE road_data SET twoway = 0, curve = NULL WHERE road_id = 14;
UPDATE road_data SET twoway = 0, curve = NULL WHERE road_id = 15;
UPDATE road_data SET twoway = 0, curve = NULL WHERE road_id = 16;
UPDATE road_data SET twoway = 0, curve = NULL WHERE road_id = 17;
UPDATE road_data SET twoway = 0, curve = NULL WHERE road_id = 18;
UPDATE road_data SET twoway = 0, curve = NULL WHERE road_id = 19;
UPDATE road_data SET twoway = 0, curve = NULL WHERE road_id = 20;
UPDATE road_data SET twoway = 1, curve = NULL WHERE road_id = 21;
UPDATE road_data SET twoway = 1, curve = NULL WHERE road_id = 22;
UPDATE road_data SET twoway = 1, curve = NULL WHERE road_id = 23;
UPDATE road_data SET twoway = 0, curve = NULL WHERE road_id = 24;
UPDATE road_data SET twoway = 0, curve = NULL WHERE road_id = 25;
UPDATE road_data SET twoway = 0, curve = NULL WHERE road_id = 26;
UPDATE road_data SET twoway = 1, curve = NULL WHERE road_id = 27;
UPDATE road_data SET twoway = 0, curve = NULL WHERE road_id = 28;
UPDATE road_data SET twoway = 0, curve = NULL WHERE road_id = 29;
UPDATE road_data SET twoway = 0, curve = NULL WHERE road_id = 30;
UPDATE road_data SET twoway = 0, curve = NULL WHERE road_id = 31;
UPDATE road_data SET twoway = 0, curve = NULL WHERE road_id = 32;
UPDATE road_data SET twoway = 0, curve = NULL WHERE road_id = 33;
UPDATE road_data SET twoway = 0, curve = NULL WHERE road_id = 34;
UPDATE road_data SET twoway = 0, curve = NULL WHERE road_id = 35;
UPDATE road_data SET twoway = 0, curve = NULL WHERE road_id = 36;
UPDATE road_data SET twoway = 0, curve = NULL WHERE road_id = 37;
UPDATE road_data SET twoway = 0, curve = NULL WHERE road_id = 38;
UPDATE road_data SET twoway = 0, curve = NULL WHERE road_id = 39;
UPDATE road_data SET twoway = 0, curve = NULL WHERE road_id = 40;
UPDATE road_data SET twoway = 0, curve = NULL WHERE road_id = 41;
UPDATE road_data SET twoway = 1, curve = NULL WHERE road_id = 42;
UPDATE road_data SET twoway = 1, curve = NULL WHERE road_id = 43;
UPDATE road_data SET twoway = 0, curve = NULL WHERE road_id = 44;
UPDATE road_data SET twoway = 0, curve = NULL WHERE road_id = 45;
UPDATE road_data SET twoway = 0, curve = NULL WHERE road_id = 46;
UPDATE road_data SET twoway = 0, curve = NULL WHERE road_id = 47;
UPDATE road_data SET twoway = 0, curve = NULL WHERE road_id = 48;
UPDATE road_data SET twoway = 1, curve = NULL WHERE road_id = 49;
UPDATE road_data SET twoway = 1, curve = NULL WHERE road_id = 50;
UPDATE road_data SET twoway = 1, curve = NULL WHERE road_id = 51;
UPDATE road_data SET twoway = 1, curve = NULL WHERE road_id = 52;
UPDATE road_data SET twoway = 1, curve = NULL WHERE road_id = 53;
UPDATE road_data SET twoway = 1, curve = NULL WHERE road_id = 54;
UPDATE road_data SET twoway = 1, curve = NULL WHERE road_id = 55;
UPDATE road_data SET twoway = 1, curve = NULL WHERE road_id = 56;
UPDATE road_data SET twoway = 1, curve = NULL WHERE road_id = 57;
UPDATE road_data SET twoway = 1, curve = NULL WHERE road_id = 58;
UPDATE road_data SET twoway = 1, curve = NULL WHERE road_id = 59;
UPDATE road_data SET twoway = 1, curve = NULL WHERE road_id = 60;
UPDATE road_data SET twoway = 1, curve = NULL WHERE road_id = 61;
UPDATE road_data SET twoway = 1, curve = NULL WHERE road_id = 62;
UPDATE road_data SET twoway = 1, curve = NULL WHERE road_id = 63;
UPDATE road_data SET twoway = 1, curve = NULL WHERE road_id = 64;
UPDATE road_data SET twoway = 1, curve = NULL WHERE road_id = 65;
UPDATE road_data SET twoway = 1, curve = NULL WHERE road_id = 66;
UPDATE road_data SET twoway = 1, curve = NULL WHERE road_id = 67;
UPDATE road_data SET twoway = 1, curve = NULL WHERE road_id = 68;
UPDATE road_data SET twoway = 1, curve = NULL WHERE road_id = 69;
UPDATE road_data SET twoway = 1, curve = NULL WHERE road_id = 70;
UPDATE road_data SET twoway = 1, curve = NULL WHERE road_id = 71;
UPDATE road_data SET twoway = 1, curve = NULL WHERE road_id = 72;
UPDATE road_data SET twoway = 0, curve = NULL WHERE road_id = 73;
UPDATE road_data SET twoway = 0, curve = NULL WHERE road_id = 74;
UPDATE road_data SET twoway = 1, curve = NULL WHERE road_id = 75;
UPDATE road_data SET twoway = 1, curve = NULL WHERE road_id = 76;
UPDATE road_data SET twoway = 1, curve = NULL WHERE road_id = 77;
UPDATE road_data SET twoway = 1, curve = NULL WHERE road_id = 78;
UPDATE road_data SET twoway = 1, curve = NULL WHERE road_id = 79;
UPDATE road_data SET twoway = 1, curve = NULL WHERE road_id = 80;
UPDATE road_data SET twoway = 1, curve = NULL WHERE road_id = 81;
UPDATE road_data SET twoway = 1, curve = NULL WHERE road_id = 82;
UPDATE road_data SET twoway = 1, curve = NULL WHERE road_id = 83;
UPDATE road_data SET twoway = 1, curve = NULL WHERE road_id = 84;
UPDATE road_data SET twoway = 1, curve = NULL WHERE road_id = 85;
UPDATE road_data SET twoway = 1, curve = NULL WHERE road_id = 86;
UPDATE road_data SET twoway = 1, curve = NULL WHERE road_id = 87;
UPDATE road_data SET twoway = 0, curve = NULL WHERE road_id = 88;
UPDATE road_data SET twoway = 0, curve = NULL WHERE road_id = 89;
UPDATE road_data SET twoway = 1, curve = NULL WHERE road_id = 90;
UPDATE road_data SET twoway = 1, curve = NULL WHERE road_id = 91;
UPDATE road_data SET twoway = 1, curve = NULL WHERE road_id = 92;
UPDATE road_data SET twoway = 1, curve = NULL WHERE road_id = 93;
UPDATE road_data SET twoway = 1, curve = NULL WHERE road_id = 94;
UPDATE road_data SET twoway = 1, curve = NULL WHERE road_id = 95;
UPDATE road_data SET twoway = 1, curve = NULL WHERE road_id = 96;
UPDATE road_data SET twoway = 1, curve = NULL WHERE road_id = 97;
UPDATE road_data SET twoway = 1, curve = NULL WHERE road_id = 98;
UPDATE road_data SET twoway = 1, curve = NULL WHERE road_id = 99;
UPDATE road_data SET twoway = 1, curve = NULL WHERE road_id = 100;
UPDATE road_data SET twoway = 1, curve = NULL WHERE road_id = 101;
UPDATE road_data SET twoway = 1, curve = NULL WHERE road_id = 102;
UPDATE road_data SET twoway = 1, curve = NULL WHERE road_id = 103;
UPDATE road_data SET twoway = 1, curve = NULL WHERE road_id = 104;
UPDATE road_data SET twoway = 1, curve = NULL WHERE road_id = 105;
UPDATE road_data SET twoway = 1, curve = NULL WHERE road_id = 106;
UPDATE road_data SET twoway = 1, curve = NULL WHERE road_id = 107;
UPDATE road_data SET twoway = 1, curve = NULL WHERE road_id = 108;
UPDATE road_data SET twoway = 1, curve = NULL WHERE road_id = 109;
UPDATE road_data SET twoway = 1, curve = NULL WHERE road_id = 110;
UPDATE road_data SET twoway = 1, curve = NULL WHERE road_id = 111;
UPDATE road_data SET twoway = 1, curve = NULL WHERE road_id = 112;
UPDATE road_data SET twoway = 1, curve = NULL WHERE road_id = 113;
UPDATE road_data SET twoway = 1, curve = NULL WHERE road_id = 114;
UPDATE road_data SET twoway = 1, curve = NULL WHERE road_id = 115;
UPDATE road_data SET twoway = 1, curve = NULL WHERE road_id = 116;
UPDATE road_data SET twoway = 1, curve = NULL WHERE road_id = 117;
UPDATE road_data SET twoway = 1, curve = NULL WHERE road_id = 118;
UPDATE road_data SET twoway = 1, curve = NULL WHERE road_id = 119;
UPDATE road_data SET twoway = 1, curve = NULL WHERE road_id = 120;
UPDATE road_data SET twoway = 1, curve = NULL WHERE road_id = 121;
UPDATE road_data SET twoway = 1, curve = NULL WHERE road_id = 122;
UPDATE road_data SET twoway = 1, curve = NULL WHERE road_id = 123;
UPDATE road_data SET twoway = 1, curve = NULL WHERE road_id = 124;
UPDATE road_data SET twoway = 1, curve = NULL WHERE road_id = 125;
UPDATE road_data SET twoway = 1, curve = NULL WHERE road_id = 126;
UPDATE road_data SET twoway = 1, curve = NULL WHERE road_id = 127;
UPDATE road_data SET twoway = 1, curve = NULL WHERE road_id = 128;
UPDATE road_data SET twoway = 1, curve = NULL WHERE road_id = 129;
UPDATE road_data SET twoway = 1, curve = NULL WHERE road_id = 130;
UPDATE road_data SET twoway = 1, curve = NULL WHERE road_id = 131;
UPDATE road_data SET twoway = 1, curve = NULL WHERE road_id = 132;
UPDATE road_data SET twoway = 1, curve = NULL WHERE road_id = 133;
UPDATE road_data SET twoway = 1, curve = NULL WHERE road_id = 134;
UPDATE road_data SET twoway = 1, curve = NULL WHERE road_id = 135;
UPDATE road_data SET twoway = 1, curve = NULL WHERE road_id = 136;
UPDATE road_data SET twoway = 1, curve = NULL WHERE road_id = 137;
UPDATE road_data SET twoway = 1, curve = NULL WHERE road_id = 138;
UPDATE road_data SET twoway = 1, curve = NULL WHERE road_id = 139;
UPDATE road_data SET twoway = 1, curve = NULL WHERE road_id = 140;
UPDATE road_data SET twoway = 1, curve = NULL WHERE road_id = 141;
UPDATE road_data SET twoway = 1, curve = NULL WHERE road_id = 142;
UPDATE road_data SET twoway = 1, curve = NULL WHERE road_id = 143;
UPDATE road_data SET twoway = 1, curve = NULL WHERE road_id = 144;
UPDATE road_data SET twoway = 1, curve = NULL WHERE road_id = 145;
UPDATE road_data SET twoway = 1, curve = NULL WHERE road_id = 146;
UPDATE road_data SET twoway = 1, curve = NULL WHERE road_id = 147;
UPDATE road_data SET twoway = 1, curve = NULL WHERE road_id = 148;
UPDATE road_data SET twoway = 1, curve = NULL WHERE road_id = 149;
UPDATE road_data SET twoway = 1, curve = NULL WHERE road_id = 150;
UPDATE road_data SET twoway = 1, curve = NULL WHERE road_id = 151;
UPDATE road_data SET twoway = 1, curve = NULL WHERE road_id = 152;
UPDATE road_data SET twoway = 1, curve = NULL WHERE road_id = 153;
UPDATE road_data SET twoway = 1, curve = NULL WHERE road_id = 154;
UPDATE road_data SET twoway = 1, curve = NULL WHERE road_id = 155;
UPDATE road_data SET twoway = 1, curve = NULL WHERE road_id = 156;
UPDATE road_data SET twoway = 1, curve = NULL WHERE road_id = 157;
UPDATE road_data SET twoway = 1, curve = NULL WHERE road_id = 158;
UPDATE road_data SET twoway = 1, curve = NULL WHERE road_id = 159;
UPDATE road_data SET twoway = 1, curve = NULL WHERE road_id = 160;
UPDATE road_data SET twoway = 1, curve = NULL WHERE road_id = 161;
UPDATE road_data SET twoway = 1, curve = NULL WHERE road_id = 162;
UPDATE road_data SET twoway = 1, curve = NULL WHERE road_id = 163;
UPDATE road_data SET twoway = 1, curve = NULL WHERE road_id = 164;
UPDATE road_data SET twoway = 1, curve = NULL WHERE road_id = 165;
UPDATE road_data SET twoway = 1, curve = NULL WHERE road_id = 166;
UPDATE road_data SET twoway = 1, curve = NULL WHERE road_id = 167;
UPDATE road_data SET twoway = 1, curve = NULL WHERE road_id = 168;
UPDATE road_data SET twoway = 1, curve = NULL WHERE road_id = 169;
UPDATE road_data SET twoway = 1, curve = NULL WHERE road_id = 170;
UPDATE road_data SET twoway = 1, curve = NULL WHERE road_id = 171;

SELECT COUNT(*) AS place_count FROM place_data;
SELECT COUNT(*) AS waypoint_count FROM waypoint_data;
SELECT COUNT(*) AS road_count FROM road_data;
