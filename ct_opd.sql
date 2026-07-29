/*
 Navicat Premium Dump SQL

 Source Server         : localhost
 Source Server Type    : MySQL
 Source Server Version : 90600 (9.6.0)
 Source Host           : localhost:3306
 Source Schema         : ppid

 Target Server Type    : MySQL
 Target Server Version : 90600 (9.6.0)
 File Encoding         : 65001

 Date: 29/07/2026 06:30:47
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for ct_opd
-- ----------------------------
DROP TABLE IF EXISTS `ct_opd`;
CREATE TABLE `ct_opd` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `nm_opd` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `user_id` int unsigned NOT NULL,
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=123 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------
-- Records of ct_opd
-- ----------------------------
BEGIN;
INSERT INTO `ct_opd` (`id`, `nm_opd`, `user_id`, `created_at`, `updated_at`) VALUES (1, 'Dinas Pendidikan dan Kebudayaan', 1, NULL, '2021-03-24 16:59:15');
INSERT INTO `ct_opd` (`id`, `nm_opd`, `user_id`, `created_at`, `updated_at`) VALUES (9, 'Dinas Kesehatan', 1, NULL, '2021-03-24 16:59:15');
INSERT INTO `ct_opd` (`id`, `nm_opd`, `user_id`, `created_at`, `updated_at`) VALUES (16, 'Dinas Pekerjaan Umum dan Penataan Ruang', 1, NULL, '2021-03-24 16:59:15');
INSERT INTO `ct_opd` (`id`, `nm_opd`, `user_id`, `created_at`, `updated_at`) VALUES (25, 'Dinas Perumahan Rakyat dan Kawasan Permukiman', 1, NULL, '2021-03-24 16:59:15');
INSERT INTO `ct_opd` (`id`, `nm_opd`, `user_id`, `created_at`, `updated_at`) VALUES (26, 'Satuan Polisi Pamong Praja', 1, NULL, '2021-03-24 16:59:15');
INSERT INTO `ct_opd` (`id`, `nm_opd`, `user_id`, `created_at`, `updated_at`) VALUES (27, 'Badan Penanggulangan Bencana Daerah', 1, NULL, '2021-03-24 16:59:15');
INSERT INTO `ct_opd` (`id`, `nm_opd`, `user_id`, `created_at`, `updated_at`) VALUES (28, 'Dinas Sosial', 1, NULL, '2021-03-24 16:59:15');
INSERT INTO `ct_opd` (`id`, `nm_opd`, `user_id`, `created_at`, `updated_at`) VALUES (31, 'Dinas Tenaga Kerja dan Transmigrasi', 1, NULL, '2021-03-24 16:59:15');
INSERT INTO `ct_opd` (`id`, `nm_opd`, `user_id`, `created_at`, `updated_at`) VALUES (37, 'Dinas Pemberdayaan Perempuan, Perlindungan Anak, Kependudukan dan Keluarga Berencana', 1, NULL, '2021-03-24 16:59:15');
INSERT INTO `ct_opd` (`id`, `nm_opd`, `user_id`, `created_at`, `updated_at`) VALUES (38, 'Dinas Ketahanan Pangan', 1, NULL, '2021-03-24 16:59:15');
INSERT INTO `ct_opd` (`id`, `nm_opd`, `user_id`, `created_at`, `updated_at`) VALUES (40, 'Dinas Lingkungan Hidup dan Kehutanan', 1, NULL, '2021-03-24 16:59:15');
INSERT INTO `ct_opd` (`id`, `nm_opd`, `user_id`, `created_at`, `updated_at`) VALUES (46, 'Dinas Pemberdayaan Masyarakat dan Desa', 1, NULL, '2021-03-24 16:59:15');
INSERT INTO `ct_opd` (`id`, `nm_opd`, `user_id`, `created_at`, `updated_at`) VALUES (47, 'Dinas Perhubungan', 1, NULL, '2021-03-24 16:59:15');
INSERT INTO `ct_opd` (`id`, `nm_opd`, `user_id`, `created_at`, `updated_at`) VALUES (49, 'Dinas Komunikasi, Informatika, Statistik dan Persandian', 1, NULL, '2021-03-24 16:59:15');
INSERT INTO `ct_opd` (`id`, `nm_opd`, `user_id`, `created_at`, `updated_at`) VALUES (50, 'Dinas Koperasi, Usaha Kecil dan Menengah', 1, NULL, '2021-03-24 16:59:15');
INSERT INTO `ct_opd` (`id`, `nm_opd`, `user_id`, `created_at`, `updated_at`) VALUES (51, 'Dinas Penanaman Modal dan Pelayanan Terpadu Satu Pintu', 1, NULL, '2021-03-24 16:59:15');
INSERT INTO `ct_opd` (`id`, `nm_opd`, `user_id`, `created_at`, `updated_at`) VALUES (52, 'Dinas Kepemudaan dan Olahraga', 1, NULL, '2021-03-24 16:59:15');
INSERT INTO `ct_opd` (`id`, `nm_opd`, `user_id`, `created_at`, `updated_at`) VALUES (54, 'Dinas Perpustakaan dan Kearsipan', 1, NULL, '2021-03-24 16:59:15');
INSERT INTO `ct_opd` (`id`, `nm_opd`, `user_id`, `created_at`, `updated_at`) VALUES (55, 'Dinas Kelautan dan Perikanan', 1, NULL, '2021-03-24 16:59:15');
INSERT INTO `ct_opd` (`id`, `nm_opd`, `user_id`, `created_at`, `updated_at`) VALUES (61, 'Dinas Pariwisata', 1, NULL, '2021-03-24 16:59:15');
INSERT INTO `ct_opd` (`id`, `nm_opd`, `user_id`, `created_at`, `updated_at`) VALUES (62, 'Dinas Pertanian', 1, NULL, '2021-03-24 16:59:15');
INSERT INTO `ct_opd` (`id`, `nm_opd`, `user_id`, `created_at`, `updated_at`) VALUES (67, 'Dinas Energi dan Sumber Daya Mineral', 1, NULL, '2021-03-24 16:59:15');
INSERT INTO `ct_opd` (`id`, `nm_opd`, `user_id`, `created_at`, `updated_at`) VALUES (68, 'Dinas Perindustrian dan Perdagangan', 1, NULL, '2021-03-24 16:59:15');
INSERT INTO `ct_opd` (`id`, `nm_opd`, `user_id`, `created_at`, `updated_at`) VALUES (71, 'Biro Hukum Sekretariat Daerah', 1122, NULL, '2025-04-24 12:51:43');
INSERT INTO `ct_opd` (`id`, `nm_opd`, `user_id`, `created_at`, `updated_at`) VALUES (79, 'Sekretariat DPRD', 1, NULL, '2021-03-24 16:59:15');
INSERT INTO `ct_opd` (`id`, `nm_opd`, `user_id`, `created_at`, `updated_at`) VALUES (80, 'Badan Perencanaan Pembangunan Daerah', 1, NULL, '2021-03-24 16:59:15');
INSERT INTO `ct_opd` (`id`, `nm_opd`, `user_id`, `created_at`, `updated_at`) VALUES (81, 'Badan Pengelolaan Keuangan dan Aset Daerah', 1, NULL, '2021-03-24 16:59:15');
INSERT INTO `ct_opd` (`id`, `nm_opd`, `user_id`, `created_at`, `updated_at`) VALUES (82, 'Badan Pendapatan Daerah', 1, NULL, '2021-03-24 16:59:15');
INSERT INTO `ct_opd` (`id`, `nm_opd`, `user_id`, `created_at`, `updated_at`) VALUES (95, 'Badan Kepegawaian Daerah', 1, NULL, '2022-07-15 02:34:15');
INSERT INTO `ct_opd` (`id`, `nm_opd`, `user_id`, `created_at`, `updated_at`) VALUES (96, 'Badan Pengembangan Sumber Daya Manusia Daerah', 1, NULL, '2021-03-24 16:59:15');
INSERT INTO `ct_opd` (`id`, `nm_opd`, `user_id`, `created_at`, `updated_at`) VALUES (97, 'Badan Penghubung Daerah', 1, NULL, '2021-03-24 16:59:15');
INSERT INTO `ct_opd` (`id`, `nm_opd`, `user_id`, `created_at`, `updated_at`) VALUES (98, 'Inspektorat', 1, NULL, '2021-03-24 16:59:15');
INSERT INTO `ct_opd` (`id`, `nm_opd`, `user_id`, `created_at`, `updated_at`) VALUES (99, 'Badan Kesatuan Bangsa dan Politik', 1, NULL, '2021-03-24 16:59:15');
INSERT INTO `ct_opd` (`id`, `nm_opd`, `user_id`, `created_at`, `updated_at`) VALUES (103, 'Biro Pengadaan Barang/ Jasa dan LPSE Sekretariat Daerah', 1122, '2022-10-04 18:52:48', '2023-07-13 13:38:34');
INSERT INTO `ct_opd` (`id`, `nm_opd`, `user_id`, `created_at`, `updated_at`) VALUES (104, 'Biro Administrasi Pimpinan dan Protokol Sekretariat Daerah', 1122, '2022-10-04 18:54:11', '2024-10-07 11:11:57');
INSERT INTO `ct_opd` (`id`, `nm_opd`, `user_id`, `created_at`, `updated_at`) VALUES (105, 'Biro Organisasi dan Reformasi Sekretariat Daerah', 1122, '2022-10-04 18:58:16', '2022-10-06 18:36:22');
INSERT INTO `ct_opd` (`id`, `nm_opd`, `user_id`, `created_at`, `updated_at`) VALUES (106, 'Biro Umum dan Perlengkapan Sekretariat Daerah', 1122, '2022-10-06 18:31:00', '2023-07-13 13:38:51');
INSERT INTO `ct_opd` (`id`, `nm_opd`, `user_id`, `created_at`, `updated_at`) VALUES (109, 'Biro Pemerintahan dan Otonomi Daerah Sekretariat Daerah', 1122, '2022-10-06 18:40:53', '2024-07-24 11:26:21');
INSERT INTO `ct_opd` (`id`, `nm_opd`, `user_id`, `created_at`, `updated_at`) VALUES (110, 'Biro Perekonomian dan Administrasi Pembangunan Sekretariat Daerah', 1122, '2022-10-18 16:25:30', '2022-10-18 16:25:30');
INSERT INTO `ct_opd` (`id`, `nm_opd`, `user_id`, `created_at`, `updated_at`) VALUES (115, 'PPID Utama', 1122, '2024-07-12 10:07:00', '2024-07-12 10:53:00');
INSERT INTO `ct_opd` (`id`, `nm_opd`, `user_id`, `created_at`, `updated_at`) VALUES (116, 'Biro Hukum', 1122, '2024-09-20 10:09:43', '2024-09-20 10:20:43');
COMMIT;

SET FOREIGN_KEY_CHECKS = 1;
