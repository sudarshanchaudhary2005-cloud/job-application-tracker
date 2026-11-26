import unittest
from tracker import JobTracker


class TestJobTracker(unittest.TestCase):
    def setUp(self):
        # Use an in-memory SQLite database for isolated, fast tests
        self.tracker = JobTracker(db_name=":memory:")

    def tearDown(self):
        self.tracker.close()

    def test_add_and_search_application(self):
        app_id = self.tracker.add_application("Google", "SWE Intern", "Applied", "Referral")
        self.assertEqual(app_id, 1)

        results = self.tracker.search_applications(keyword="Google")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0][1], "Google")
        self.assertEqual(results[0][2], "SWE Intern")

    def test_add_invalid_status_raises_error(self):
        with self.assertRaises(ValueError):
            self.tracker.add_application("Microsoft", "Cloud Intern", status="Pending")

    def test_update_status(self):
        app_id = self.tracker.add_application("Amazon", "SDE Intern")
        updated = self.tracker.update_status(app_id, "Interview", "Round 1 scheduled")
        self.assertTrue(updated)

        results = self.tracker.search_applications(status="Interview")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0][3], "Interview")
        self.assertEqual(results[0][5], "Round 1 scheduled")

    def test_delete_application(self):
        app_id = self.tracker.add_application("Meta", "ML Intern")
        self.assertTrue(self.tracker.delete_application(app_id))
        self.assertEqual(len(self.tracker.search_applications()), 0)

    def test_get_summary(self):
        self.tracker.add_application("Company A", "Intern", "Applied")
        self.tracker.add_application("Company B", "Intern", "Applied")
        self.tracker.add_application("Company C", "Intern", "Interview")

        summary = self.tracker.get_summary()
        self.assertEqual(summary["Total"], 3)
        self.assertEqual(summary["Applied"], 2)
        self.assertEqual(summary["Interview"], 1)


if __name__ == "__main__":
    unittest.main()
