"""
AttendanceService - Specific operations for attendance data
Built on top of DataService for reusable database operations
"""

from typing import List, Dict, Optional
from datetime import datetime, date
from app.services.data_service import DataService

class AttendanceService:
    """Service class for attendance-related database operations"""
    
    @staticmethod
    def get_all_attendance(limit: int = 100) -> List[Dict]:
        """Get all attendance records with student info"""
        query = """
            SELECT 
                a.id,
                a.student_id AS student_pk,
                a.timestamp,
                a.status,
                s.student_id AS student_no,
                s.first_name,
                s.last_name,
                s.section
            FROM attendance a
            JOIN students s ON a.student_id = s.id
            ORDER BY a.timestamp DESC
            LIMIT %s
        """
        return DataService.execute_query(query, (limit,)) or []
    
    @staticmethod
    def get_today_attendance() -> List[Dict]:
        """Get today's attendance records"""
        today = date.today()
        query = """
            SELECT 
                a.id,
                a.student_id AS student_pk,
                a.timestamp,
                a.status,
                s.student_id AS student_no,
                s.first_name,
                s.last_name,
                s.section
            FROM attendance a
            JOIN students s ON a.student_id = s.id
            WHERE DATE(a.timestamp) = %s
            ORDER BY a.timestamp DESC
        """
        return DataService.execute_query(query, (today,)) or []
    
    @staticmethod
    def get_attendance_by_student(student_id: int, limit: int = 50) -> List[Dict]:
        """Get attendance records for specific student"""
        query = """
            SELECT 
                a.id,
                a.timestamp,
                a.status,
                s.student_id AS student_no,
                s.first_name,
                s.last_name
            FROM attendance a
            JOIN students s ON a.student_id = s.id
            WHERE a.student_id = %s
            ORDER BY a.timestamp DESC
            LIMIT %s
        """
        return DataService.execute_query(query, (student_id, limit)) or []
    
    @staticmethod
    def create_attendance(student_id: int, status: str = "present") -> bool:
        """Create new attendance record"""
        attendance_data = {
            "student_id": student_id,
            "status": status,
            "timestamp": datetime.now()
        }
        return DataService.create("attendance", attendance_data)

    @staticmethod
    def create_today_once(student_id: int, status: str = "present") -> bool:
        """
        Create attendance for today only once per student.
        Returns True if a new record was created, False if already exists or on error.
        """
        try:
            today = date.today()
            # Check existing record for today
            check_query = """
                SELECT id FROM attendance
                WHERE student_id = %s AND DATE(timestamp) = %s
                LIMIT 1
            """
            exists = DataService.execute_query(check_query, (student_id, today))
            if exists:
                return False
            return AttendanceService.create_attendance(student_id, status)
        except Exception:
            return False
    
    @staticmethod
    def update_attendance(attendance_id: int, status: str) -> bool:
        """Update attendance status"""
        return DataService.update("attendance", attendance_id, {"status": status})
    
    @staticmethod
    def delete_attendance(attendance_id: int) -> bool:
        """Delete attendance record"""
        return DataService.delete("attendance", attendance_id)
    
    @staticmethod
    def get_attendance_stats(target_date: date = None) -> Dict[str, int]:
        """Get attendance statistics for a specific date"""
        if target_date is None:
            target_date = date.today()
        
        # Count by status
        query = """
            SELECT 
                status,
                COUNT(*) as count
            FROM attendance 
            WHERE DATE(timestamp) = %s
            GROUP BY status
        """
        results = DataService.execute_query(query, (target_date,)) or []
        
        # Convert to dictionary with default values
        stats = {"present": 0, "late": 0, "absent": 0}
        for row in results:
            stats[row["status"]] = row["count"]
        
        # Add total
        stats["total"] = sum(stats.values())
        
        return stats
    
    @staticmethod
    def get_attendance_for_table(limit: int = 100) -> List[List]:
        """Get attendance data formatted for table display"""
        attendance = AttendanceService.get_all_attendance(limit)
        
        # Convert to list of lists for table display
        table_data = []
        for record in attendance:
            # Format timestamp
            timestamp = record.get("timestamp", "")
            if timestamp:
                formatted_time = timestamp.strftime("%Y-%m-%d %H:%M:%S") if hasattr(timestamp, 'strftime') else str(timestamp)
            else:
                formatted_time = ""
            
            # Format status with emoji
            status = record.get("status", "")
            status_display = {
                "present": "✅ Present",
                "late": "⏰ Late", 
                "absent": "❌ Absent"
            }.get(status, status)
            
            row = [
                record.get("id", ""),
                record.get("student_no", ""),
                f"{record.get('first_name', '')} {record.get('last_name', '')}".strip(),
                record.get("section", ""),
                formatted_time,
                status_display
            ]
            table_data.append(row)
        
        return table_data
    
    @staticmethod
    def get_table_headers() -> List[str]:
        """Get table headers for attendance table"""
        return ["ID", "Student Number", "Full Name", "Section", "Timestamp", "Status"]
    
    @staticmethod
    def search_attendance(search_term: str, limit: int = 100) -> List[Dict]:
        """Search attendance by student name or number"""
        query = """
            SELECT 
                a.id,
                a.student_id AS student_pk,
                a.timestamp,
                a.status,
                s.student_id AS student_no,
                s.first_name,
                s.last_name,
                s.section
            FROM attendance a
            JOIN students s ON a.student_id = s.id
            WHERE s.first_name LIKE %s 
               OR s.last_name LIKE %s 
               OR s.student_id LIKE %s
            ORDER BY a.timestamp DESC
            LIMIT %s
        """
        search_param = f"%{search_term}%"
        return DataService.execute_query(query, (search_param, search_param, search_param, limit)) or []
    
    @staticmethod
    def get_attendance_by_date_range(start_date: date, end_date: date) -> List[Dict]:
        """Get attendance records within date range"""
        query = """
            SELECT 
                a.id,
                a.student_id AS student_pk,
                a.timestamp,
                a.status,
                s.student_id AS student_no,
                s.first_name,
                s.last_name,
                s.section
            FROM attendance a
            JOIN students s ON a.student_id = s.id
            WHERE DATE(a.timestamp) BETWEEN %s AND %s
            ORDER BY a.timestamp DESC
        """
        return DataService.execute_query(query, (start_date, end_date)) or []

# Convenience functions for easy access
def get_today_attendance():
    """Convenience function to get today's attendance"""
    return AttendanceService.get_today_attendance()

def get_attendance_stats():
    """Convenience function to get attendance stats"""
    return AttendanceService.get_attendance_stats()

def create_attendance(student_id, status="present"):
    """Convenience function to create attendance"""
    return AttendanceService.create_attendance(student_id, status)
