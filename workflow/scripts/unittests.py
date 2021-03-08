#!/usr/bin/env python3

import unittest

import genotype_union as gt

################# UNIT TESTS #################


class TestGenotypeUnion(unittest.TestCase):
    def test_check_file_pass(self):
        self.assertEqual(
            gt.check_file(
                "/DCEG/CGF/Bioinformatics/Production/Bari/Germline_pipeline_v4_dev/germlineCallingV4/tests/data/all_callers.vcf"
            ),
            0,
        )

    def test_check_file_fail(self):
        self.assertNotEqual(
            gt.check_file("/DCEG/CGF/Bioinformatics/Production/Bari/pretend_file.vcff"), 0
        )

    def test_get_header_pass(self):
        self.assertListEqual(
            gt.get_header(
                "/DCEG/CGF/Bioinformatics/Production/Bari/Germline_pipeline_v4_dev/germlineCallingV4/tests/data/all_callers.vcf"
            ),
            [
                "#CHROM",
                "POS",
                "ID",
                "REF",
                "ALT",
                "QUAL",
                "FILTER",
                "INFO",
                "FORMAT",
                "CHM1_CHM13_2",
                "CHM1_CHM13_3",
                "2:CHM1_CHM13_2",
                "2:CHM1_CHM13_3",
            ],
        )

    def test_get_header_fail(self):
        self.assertEqual(
            gt.get_header(
                "/DCEG/CGF/Bioinformatics/Production/Bari/Germline_pipeline_v4_dev/germlineCallingV4/tests/data/no_headers.vcf"
            ),
            1,
        )

    def test_vcf_check_pass(self):
        self.assertEqual(
            gt.vcf_check(
                [
                    "#CHROM",
                    "POS",
                    "ID",
                    "REF",
                    "ALT",
                    "QUAL",
                    "FILTER",
                    "INFO",
                    "FORMAT",
                    "CHM1_CHM13_2",
                    "CHM1_CHM13_3",
                ]
            ),
            0,
        )

    def test_vcf_check_fail_unpaired(self):
        self.assertEqual(
            gt.vcf_check(
                [
                    "#CHROM",
                    "POS",
                    "ID",
                    "REF",
                    "ALT",
                    "QUAL",
                    "FILTER",
                    "INFO",
                    "FORMAT",
                    "CHM1_CHM13_2",
                    "CHM1_CHM13_3",
                    "othersample",
                ]
            ),
            1,
        )

    def test_vcf_check_fail_too_few(self):
        self.assertEqual(
            gt.vcf_check(
                [
                    "#CHROM",
                    "POS",
                    "ID",
                    "REF",
                    "ALT",
                    "QUAL",
                    "FILTER",
                    "INFO",
                    "FORMAT",
                    "CHM1_CHM13_2",
                ]
            ),
            1,
        )

    def test_find_genotype_indices(self):
        self.assertEqual(
            gt.find_genotype_indices(
                [
                    "#CHROM",
                    "POS",
                    "ID",
                    "REF",
                    "ALT",
                    "QUAL",
                    "FILTER",
                    "INFO",
                    "FORMAT",
                    "1",
                    "2",
                    "3",
                    "4",
                    "5",
                    "6",
                ]
            ),
            (9, 12, 12, 15),
        )

    def test_add_set_tag(self):
        self.assertListEqual(
            gt.add_set_tag(
                "HC-DV",
                [
                    "1",
                    "12719",
                    ".",
                    "G",
                    "C",
                    "32.29",
                    ".",
                    "HC_AN=4;HC_DP=12;DV_AF=0.25",
                    "GT",
                    "0/1",
                    "0/0",
                    "0/0",
                    "0/1",
                ],
            ),
            [
                "1",
                "12719",
                ".",
                "G",
                "C",
                "32.29",
                ".",
                "HC_AN=4;HC_DP=12;DV_AF=0.25;set=HC-DV",
                "GT",
                "0/1",
                "0/0",
                "0/0",
                "0/1",
            ],
        )

    def test_remove_empty_genotypes(self):
        self.assertListEqual(
            gt.remove_empty_genotypes(
                [
                    "1",
                    "12719",
                    ".",
                    "G",
                    "C",
                    "32.29",
                    ".",
                    "HC_AN=4;HC_DP=12;DV_AF=0.25;set=HC-DV",
                    "GT",
                    "0/1",
                    "0/0",
                    "0/1",
                    "0/1",
                    ".",
                    "./.",
                    ".:.:.",
                    "./.:.:.:..",
                ],
                9,
                13,
                13,
                17,
            ),
            [
                "1",
                "12719",
                ".",
                "G",
                "C",
                "32.29",
                ".",
                "HC_AN=4;HC_DP=12;DV_AF=0.25;set=HC-DV",
                "GT",
                "0/1",
                "0/0",
                "0/1",
                "0/1",
            ],
        )

    def test_remove_empty_genotypes_blank_genos(self):
        self.assertEqual(
            gt.remove_empty_genotypes(
                [
                    "1",
                    "12719",
                    ".",
                    "G",
                    "C",
                    "32.29",
                    ".",
                    "HC_AN=4;HC_DP=12;DV_AF=0.25;set=HC-DV",
                    "GT",
                    ".",
                    "./.",
                    ".:.:.",
                    "./.:.:.:..",
                    ".",
                    "./.",
                    ".:.:.",
                    "./.:.:.:..",
                ],
                9,
                13,
                13,
                17,
            ),
            1,
        )

    def test_combine_genotypes_concordantGT(self):
        self.assertListEqual(
            gt.combine_genotypes(
                [
                    "1",
                    "12719",
                    ".",
                    "G",
                    "C",
                    "32.29",
                    ".",
                    "HC_AN=4;HC_DP=12;DV_AF=0.25;set=HC-DV",
                    "GT:DV_GT:DV_DP:DV_AD:DV_GQ:DV_PL:DV_RNC:HC_GT:HC_AD:HC_DP:HC_GQ:HC_PGT:HC_PID:HC_PL",
                    "0/1:0/1:38:29,9:5:3,0,29:..:.:.:.:.:.:.:.",
                    "0/1:0/1:43:37,6:4:1,0,29:..:.:.:.:.:.:.:.",
                    "0/1:.:.:.:.:.:.:0/1:28,8:36:99:.:.:135,0,1201",
                    "0/1:.:.:.:.:.:.:0/1:36,6:42:52:0|1:13110_G_A:52,0,1741",
                ],
                9,
                11,
                11,
                13,
            ),
            [
                "1",
                "12719",
                ".",
                "G",
                "C",
                "32.29",
                ".",
                "HC_AN=4;HC_DP=12;DV_AF=0.25;set=HC-DV",
                "GT:DV_GT:DV_DP:DV_AD:DV_GQ:DV_PL:DV_RNC:HC_GT:HC_AD:HC_DP:HC_GQ:HC_PGT:HC_PID:HC_PL",
                "0/1:0/1:38:29,9:5:3,0,29:..:0/1:28,8:36:99:.:.:135,0,1201",
                "0/1:0/1:43:37,6:4:1,0,29:..:0/1:36,6:42:52:0|1:13110_G_A:52,0,1741",
            ],
        )

    def test_combine_genotypes_discordantGT(self):
        self.assertListEqual(
            gt.combine_genotypes(
                [
                    "1",
                    "12719",
                    ".",
                    "G",
                    "C",
                    "32.29",
                    ".",
                    "HC_AN=4;HC_DP=12;DV_AF=0.25;set=HC-DV",
                    "GT:DV_GT:DV_DP:DV_AD:DV_GQ:DV_PL:DV_RNC:HC_GT:HC_AD:HC_DP:HC_GQ:HC_PGT:HC_PID:HC_PL",
                    "0/1:0/1:38:29,9:5:3,0,29:..:.:.:.:.:.:.:.",
                    "0/0:0/1:43:37,6:4:1,0,29:..:.:.:.:.:.:.:.",
                    "1/1:.:.:.:.:.:.:0/1:28,8:36:99:.:.:135,0,1201",
                    "0/1:.:.:.:.:.:.:0/1:36,6:42:52:0|1:13110_G_A:52,0,1741",
                ],
                9,
                11,
                11,
                13,
            ),
            [
                "1",
                "12719",
                ".",
                "G",
                "C",
                "32.29",
                ".",
                "HC_AN=4;HC_DP=12;DV_AF=0.25;set=HC-DV",
                "GT:DV_GT:DV_DP:DV_AD:DV_GQ:DV_PL:DV_RNC:HC_GT:HC_AD:HC_DP:HC_GQ:HC_PGT:HC_PID:HC_PL",
                "./.:0/1:38:29,9:5:3,0,29:..:0/1:28,8:36:99:.:.:135,0,1201",
                "./.:0/1:43:37,6:4:1,0,29:..:0/1:36,6:42:52:0|1:13110_G_A:52,0,1741",
            ],
        )

    def test_evaluate_variant_line_DV(self):
        self.assertListEqual(
            gt.evaluate_variant_line(
                [
                    "1",
                    "2055702",
                    "1_2055702_C_T",
                    "C",
                    "T",
                    "9",
                    ".",
                    "DV_AF=0.5;DV_AQ=9",
                    "GT:DV_GT:DV_DP:DV_AD:DV_GQ:DV_PL:DV_RNC",
                    "0/0:0/0:2:0,2:12:0,20,11:..",
                    "1/1:1/1:2:0,2:8:9,12,0:..",
                    "./.:.:.:.:.:.:.",
                    "./.:.:.:.:.:.:.",
                ],
                9,
                11,
                11,
                13,
            ),
            [
                "1",
                "2055702",
                ".",
                "C",
                "T",
                "9",
                ".",
                "DV_AF=0.5;DV_AQ=9;set=DV",
                "GT:DV_GT:DV_DP:DV_AD:DV_GQ:DV_PL:DV_RNC",
                "0/0:0/0:2:0,2:12:0,20,11:..",
                "1/1:1/1:2:0,2:8:9,12,0:..",
            ],
        )

    def test_evaluate_variant_line_HC(self):
        self.assertListEqual(
            gt.evaluate_variant_line(
                [
                    "1",
                    "829169",
                    ".",
                    "AAAAAAAAAAAAAATATATATATATATATATATATAT",
                    "*",
                    "702.03",
                    ".",
                    "HC_AN=4;HC_DP=54;HC_ExcessHet=3.0103;HC_FS=0;HC_MQ=60.22;HC_QD=14.63;HC_SOR=1.562;HC_AC=2;HC_AF=0.5;HC_MLEAC=2;HC_MLEAF=0.5",
                    "GT:HC_GT:HC_AD:HC_DP:HC_GQ:HC_PL",
                    "./.:.:.:.:.:.",
                    "./.:.:.:.:.:.",
                    "0/1:0/1:0,15:30:99:1254,456,401",
                    "0/1:0/1:0,9:18:99:719,260,246",
                ],
                9,
                11,
                11,
                13,
            ),
            [
                "1",
                "829169",
                ".",
                "AAAAAAAAAAAAAATATATATATATATATATATATAT",
                "*",
                "702.03",
                ".",
                "HC_AN=4;HC_DP=54;HC_ExcessHet=3.0103;HC_FS=0;HC_MQ=60.22;HC_QD=14.63;HC_SOR=1.562;HC_AC=2;HC_AF=0.5;HC_MLEAC=2;HC_MLEAF=0.5;set=HC",
                "GT:HC_GT:HC_AD:HC_DP:HC_GQ:HC_PL",
                "0/1:0/1:0,15:30:99:1254,456,401",
                "0/1:0/1:0,9:18:99:719,260,246",
            ],
        )

    def test_evaluate_variant_line_both(self):
        self.assertListEqual(
            gt.evaluate_variant_line(
                [
                    "1",
                    "12719",
                    "1_12719_G_C",
                    "G",
                    "C",
                    "32.29",
                    ".",
                    "HC_AN=4;HC_DP=12;DV_AF=0.25",
                    "GT:DV_GT:DV_DP:DV_AD:DV_GQ:DV_PL:DV_RNC:HC_GT:HC_AD:HC_DP:HC_GQ:HC_PGT:HC_PID:HC_PL",
                    "0/1:0/1:38:29,9:5:3,0,29:..:.:.:.:.:.:.:.",
                    "0/1:0/1:43:37,6:4:1,0,29:..:.:.:.:.:.:.:.",
                    "0/1:.:.:.:.:.:.:0/1:28,8:36:99:.:.:135,0,1201",
                    "0/1:.:.:.:.:.:.:0/1:36,6:42:52:0|1:13110_G_A:52,0,1741",
                ],
                9,
                11,
                11,
                13,
            ),
            [
                "1",
                "12719",
                ".",
                "G",
                "C",
                "32.29",
                ".",
                "HC_AN=4;HC_DP=12;DV_AF=0.25;set=HC-DV",
                "GT:DV_GT:DV_DP:DV_AD:DV_GQ:DV_PL:DV_RNC:HC_GT:HC_AD:HC_DP:HC_GQ:HC_PGT:HC_PID:HC_PL",
                "0/1:0/1:38:29,9:5:3,0,29:..:0/1:28,8:36:99:.:.:135,0,1201",
                "0/1:0/1:43:37,6:4:1,0,29:..:0/1:36,6:42:52:0|1:13110_G_A:52,0,1741",
            ],
        )

    def test_evaluate_variant_line_neither(self):
        self.assertEqual(
            gt.evaluate_variant_line(
                [
                    "1",
                    "12719",
                    ".",
                    "G",
                    "C",
                    "32.29",
                    ".",
                    "HC_AN=4;HC_DP=12;DV_AF=0.25",
                    "GT",
                    "0/1",
                    "0/0",
                    "0/0",
                    "0/1",
                ],
                9,
                11,
                11,
                13,
            ),
            1,
        )

    def test_add_headers(self):
        self.assertListEqual(
            gt.add_headers(
                "test:time:stamp", "test.version", "genotype_union.py", "python gt.py -do -stuff"
            ),
            [
                '##INFO=<ID=set,Number=3,Type=String,Description="Set of callers that identified a variant (HC, DV, or HC-DV)">',
                "##genotype_union.py_Version=test.version, Union of HC and DV genotype data, test:time:stamp",
                "##genotype_union.py_Command=python gt.py -do -stuff",
            ],
        )

    # def test_(self):
    # self.assert(gt.())

    # def test_(self):
    # self.assert(gt.())

    # def test_(self):
    # self.assert(gt.())


################# BLACK BOX TESTS #################

# class TestScript(unittest.TestCase):

#     def test_script(self):
#         output=runScript('genotype_union.py /DCEG/CGF/Bioinformatics/Production/Bari/Germline_pipeline_v4_dev/germlineCallingV4/test_data/dv_and_hc.vcf  /DCEG/CGF/Bioinformatics/Production/Bari/Germline_pipeline_v4_dev/germlineCallingV4/test_data/harmonized.vcf')
#         self.assertEqual(output, '8')


if __name__ == "__main__":
    unittest.main()

    # suite = unittest.TestLoader().loadTestsFromTestCase(ScriptTest)
    # unittest.TextTestRunner(verbosity=2).run(suite)
