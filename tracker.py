import sqlite3
from datetime import datetime
from typing import List, Tuple, Dict, Optional


class JobTracker:
    """Manages job applications using an SQLite database."""

    VALID_STATUSES = ("Applied", "Interview", "Offer", "Rejected", "Withdrawn")

    def __init__(self, db_name: str = "applications.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self._create_table()

    def _create_table(self) -> None:
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company TEXT NOT NULL,
                role TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Applied',
                date_applied TEXT NOT NULL,
                notes TEXT DEFAULT ''
            )
        """)
        self.conn.commit()

    def add_application(
        self, company: str, role: str, status: str = "Applied", notes: str = ""
    ) -> int:
        if status not in self.VALID_STATUSES:
            raise ValueError(f"Invalid status. Choose from: {', '.join(self.VALID_STATUSES)}")
        date_applied = datetime.now().strftime("%Y-%m-%d")
        self.cursor.execute(
            """
            INSERT INTO applications (company, role, status, date_applied, notes)
            VALUES (?, ?, ?, ?, ?)
            """,
            (company.strip(), role.strip(), status, date_applied, notes.strip()),
        )
        self.conn.commit()
        return self.cursor.lastrowid

    def search_applications(
        self, keyword: Optional[str] = None, status: Optional[str] = None
    ) -> List[Tuple]:
        query = "SELECT id, company, role, status, date_applied, notes FROM applications WHERE 1=1"
        params = []

        if keyword:
            query += " AND (company LIKE ? OR role LIKE ? OR notes LIKE ?)"
            like_term = f"%{keyword.strip()}%"
            params.extend([like_term, like_term, like_term])

        if status:
            query += " AND status = ?"
            params.append(status)

        query += " ORDER BY date_applied DESC, id DESC"
        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def update_status(self, app_id: int, new_status: str, notes: Optional[str] = None) -> bool:
        if new_status not in self.VALID_STATUSES:
            raise ValueError(f"Invalid status. Choose from: {', '.join(self.VALID_STATUSES)}")

        if notes is not None:
            self.cursor.execute(
                "UPDATE applications SET status = ?, notes = ? WHERE id = ?",
                (new_status, notes.strip(), app_id),
            )
        else:
            self.cursor.execute(
                "UPDATE applications SET status = ? WHERE id = ?",
                (new_status, app_id),
            )
        self.conn.commit()
        return self.cursor.rowcount > 0

    def delete_application(self, app_id: int) -> bool:
        self.cursor.execute("DELETE FROM applications WHERE id = ?", (app_id,))
        self.conn.commit()
        return self.cursor.rowcount > 0

    def get_summary(self) -> Dict[str, int]:
        self.cursor.execute(
            "SELECT status, COUNT(*) FROM applications GROUP BY status"
        )
        counts = dict(self.cursor.fetchall())
        total = sum(counts.values())
        return {"Total": total, **counts}

    def close(self) -> None:
        self.conn.close()


def print_applications(rows: List[Tuple]) -> None:
    if not rows:
        print("\nNo applications found.")
        return

    print(f"\n{'ID':<4} {'Company':<20} {'Role':<22} {'Status':<12} {'Date':<12} {'Notes'}")
    print("-" * 85)
    for app_id, company, role, status, date_applied, notes in rows:
        print(f"{app_id:<4} {company:<20} {role:<22} {status:<12} {date_applied:<12} {notes}")


def main() -> None:
    tracker = JobTracker()
    try:
        while True:
            print("\n=== Job Application Tracker ===")
            print("1. Add Application")
            print("2. View / Search Applications")
            print("3. Update Application Status")
            print("4. Delete Application")
            print("5. View Summary")
            print("6. Exit")

            choice = input("\nSelect an option (1-6): ").strip()

            if choice == "1":
                company = input("Company name: ").strip()
                role = input("Role / Position: ").strip()
                print(f"Statuses: {', '.join(JobTracker.VALID_STATUSES)}")
                status = input("Status (default: Applied): ").strip() or "Applied"
                notes = input("Notes (optional): ").strip()
                try:
                    app_id = tracker.add_application(company, role, status, notes)
                    print(f"Application added with ID: {app_id}")
                except ValueError as e:
                    print(f"Error: {e}")

            elif choice == "2":
                keyword = input("Search keyword (leave blank for all): ").strip() or None
                status = input("Filter by status (leave blank for all): ").strip() or None
                results = tracker.search_applications(keyword=keyword, status=status)
                print_applications(results)

            elif choice == "3":
                try:
                    app_id = int(input("Enter Application ID to update: ").strip())
                    print(f"Statuses: {', '.join(JobTracker.VALID_STATUSES)}")
                    new_status = input("New status: ").strip()
                    notes = input("Updated notes (leave blank to keep existing): ").strip()
                    updated = tracker.update_status(
                        app_id, new_status, notes if notes else None
                    )
                    print("Application updated." if updated else "Application ID not found.")
                except ValueError as e:
                    print(f"Error: {e}")

            elif choice == "4":
                try:
                    app_id = int(input("Enter Application ID to delete: ").strip())
                    deleted = tracker.delete_application(app_id)
                    print("Application deleted." if deleted else "Application ID not found.")
                except ValueError:
                    print("Error: Please enter a valid numeric ID.")

            elif choice == "5":
                summary = tracker.get_summary()
                print("\n--- Application Summary ---")
                for key, count in summary.items():
                    print(f"{key:<12}: {count}")

            elif choice == "6":
                print("Goodbye!")
                break
            else:
                print("Invalid choice. Please enter a number from 1 to 6.")
    finally:
        tracker.close()


if __name__ == "__main__":
    main()
