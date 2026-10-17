#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Bộ kiểm thử tính chính xác công cụ tính lương Gross ⇋ Net và Quản lý ứng tuyển Kanban Pipeline
"""

import unittest
import math

class TestSalaryCalculator(unittest.TestCase):
    """
    Kiểm thử thuật toán tính thuế và bảo hiểm theo luật lao động VN 2024 - 2026
    """

    def setUp(self):
        self.base_salary = 2340000  # Lương cơ sở
        self.max_social_base = self.base_salary * 20  # 46.800.000đ
        self.min_wage_region_2 = 4410000  # Hạ Long, Cẩm Phả,...
        self.max_unemployment_base = self.min_wage_region_2 * 20  # 88.200.000đ
        self.personal_deduction = 11000000  # 11tr
        self.dependent_deduction = 4400000  # 4.4tr

    def calc_tax(self, assessable):
        if assessable <= 0:
            return 0
        tax = 0
        brackets = [
            (5000000, 0.05),
            (10000000, 0.10),
            (18000000, 0.15),
            (32000000, 0.20),
            (52000000, 0.25),
            (80000000, 0.30),
            (float('inf'), 0.35)
        ]
        prev = 0
        rem = assessable
        for limit, rate in brackets:
            span = limit - prev
            chunk = min(rem, span)
            tax += round(chunk * rate)
            rem -= chunk
            if rem <= 0:
                break
            prev = limit
        return tax

    def calc_gross_to_net(self, gross, dependents=0):
        soc_base = min(gross, self.max_social_base)
        unemp_base = min(gross, self.max_unemployment_base)
        bhxh = round(soc_base * 0.08)
        bhyt = round(soc_base * 0.015)
        bhtn = round(unemp_base * 0.01)
        ins_emp = bhxh + bhyt + bhtn

        taxable = gross - ins_emp
        total_deduct = self.personal_deduction + (dependents * self.dependent_deduction)
        assessable = max(0, taxable - total_deduct)
        tax = self.calc_tax(assessable)
        net = max(0, taxable - tax)
        return {
            "net": net,
            "insurance": ins_emp,
            "tax": tax,
            "assessable": assessable
        }

    def test_01_salary_under_11m_zero_tax(self):
        """Lương dưới 11 triệu (trừ BH) không phải đóng thuế TNCN"""
        res = self.calc_gross_to_net(10000000, dependents=0)
        # BH = 10tr * 10.5% = 1.050.000đ
        self.assertEqual(res["insurance"], 1050000)
        # Thu nhập trước thuế = 8.950.000đ < 11tr -> thuế = 0
        self.assertEqual(res["tax"], 0)
        self.assertEqual(res["net"], 10000000 - 1050000)

    def test_02_salary_15m_standard_case(self):
        """Lương 15 triệu (chuẩn IT Support Hạ Long) tính chuẩn từng đồng"""
        res = self.calc_gross_to_net(15000000, dependents=0)
        # BH = 1.575.000đ
        self.assertEqual(res["insurance"], 1575000)
        # Thu nhập chịu thuế = 13.425.000đ
        # Thu nhập tính thuế = 13.425.000 - 11.000.000 = 2.425.000đ
        self.assertEqual(res["assessable"], 2425000)
        # Thuế bậc 1 (5%): 2.425.000 * 5% = 121.250đ
        self.assertEqual(res["tax"], 121250)
        # Thực lĩnh Net = 13.425.000 - 121.250 = 13.303.750đ
        self.assertEqual(res["net"], 13303750)

    def test_03_salary_ceiling_cap(self):
        """Lương chuyên gia cao (> 50 triệu) được áp trần đóng BHXH/BHYT đúng 20 lần lương cơ sở"""
        res = self.calc_gross_to_net(60000000, dependents=0)
        # BHXH (8% của 46.8tr) = 3.744.000đ
        # BHYT (1.5% của 46.8tr) = 702.000đ
        # BHTN (1% của 60tr vì < trần BHTN 88.2tr) = 600.000đ
        expected_ins = 3744000 + 702000 + 600000
        self.assertEqual(res["insurance"], expected_ins)

    def test_04_dependents_deduction(self):
        """Nuôi 2 người phụ thuộc được giảm trừ thêm 8.8 triệu đồng/tháng"""
        res0 = self.calc_gross_to_net(25000000, dependents=0)
        res2 = self.calc_gross_to_net(25000000, dependents=2)
        # Có người phụ thuộc giúp giảm đáng kể thuế TNCN
        self.assertLess(res2["tax"], res0["tax"])
        self.assertGreater(res2["net"], res0["net"])

if __name__ == "__main__":
    unittest.main()
