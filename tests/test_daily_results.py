import unittest

from bot import daily_pnl, day_summary, daily_panel, results_md


def sell(day, pnl):
    return {"time": f"{day}T12:00:00-05:00", "side": "SELL", "sym": "SPY", "qty": 1, "price": 1, "pnl": pnl, "why": "x"}


STATE = {"cash": 10000.0, "pos": {}, "prices": {}, "started": "2026-11-04T15:00:00-05:00",
         "spy_start": None, "last_run": None, "log": [],
         "trades": [{"time": "2026-11-04T10:00:00-05:00", "side": "BUY", "sym": "SPY", "qty": 1, "price": 1, "why": "x"},
                    sell("2026-11-05", 10.0), sell("2026-11-05", -4.0), sell("2026-11-06", -3.0)]}


class DailyResultsTests(unittest.TestCase):
    def test_groups_sells_by_day_newest_first(self):
        days = daily_pnl(STATE)
        self.assertEqual([d["day"] for d in days], ["2026-11-06", "2026-11-05"])
        self.assertAlmostEqual(days[1]["pnl"], 6.0)
        self.assertEqual((days[1]["wins"], days[1]["sells"]), (1, 2))

    def test_counts_green_and_red_days(self):
        green, red = day_summary(daily_pnl(STATE))
        self.assertEqual((len(green), len(red)), (1, 1))

    def test_panel_and_results_render(self):
        self.assertIn("Profitable days", daily_panel(STATE))
        self.assertIn("1 profitable day, 1 negative day", results_md(STATE))


if __name__ == "__main__":
    unittest.main()
