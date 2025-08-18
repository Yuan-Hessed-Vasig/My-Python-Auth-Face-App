"""
StudentsService - Specific operations for students data
Built on top of DataService for reusable database operations
"""

from typing import List, Dict, Optional
from app.services.data_service import DataService

class StudentsService:
    """Service class for student-related database operations"""
    
    @staticmethod
    def get_all_students(order_by: str = "student_number") -> List[Dict]:
        """Get all students ordered by student number"""
        return DataService.get_all("students", order_by)
    
    @staticmethod
    def get_student_by_id(student_id: int) -> Optional[Dict]:
        """Get student by ID"""
        return DataService.get_by_id("students", student_id)
    
    @staticmethod
    def get_student_by_number(student_number: str) -> Optional[Dict]:
        """Get student by student number"""
        return DataService.get_by_id("students", student_number, "student_number")
    
    @staticmethod
    def search_students(search_term: str) -> List[Dict]:
        """Search students by name, student number, or section"""
        search_columns = ["first_name", "last_name", "student_number", "section"]
        return DataService.search("students", search_term, search_columns)
    
    @staticmethod
    def create_student(student_data: Dict) -> bool:
        """Create new student"""
        required_fields = ["student_number", "first_name", "last_name"]
        
        # Validate required fields
        for field in required_fields:
            if field not in student_data or not student_data[field]:
                print(f"❌ Missing required field: {field}")
                return False
        
        return DataService.create("students", student_data)
    
    @staticmethod
    def update_student(student_id: int, student_data: Dict) -> bool:
        """Update existing student"""
        return DataService.update("students", student_id, student_data)
    
    @staticmethod
    def delete_student(student_id: int) -> bool:
        """Delete student"""
        return DataService.delete("students", student_id)
    
    @staticmethod
    def get_students_by_section(section: str) -> List[Dict]:
        """Get all students in a specific section"""
        query = "SELECT * FROM students WHERE section = %s ORDER BY last_name, first_name"
        return DataService.execute_query(query, (section,))
    
    @staticmethod
    def get_students_count() -> Dict[str, int]:
        """Get student statistics"""
        total = DataService.count("students")
        
        # Count by sections
        sections_query = """
            SELECT section, COUNT(*) as count 
            FROM students 
            WHERE section IS NOT NULL 
            GROUP BY section
        """
        sections_data = DataService.execute_query(sections_query)
        
        return {
            "total": total,
            "active": total,  # Assuming all are active for now
            "inactive": 0,
            "sections": {row["section"]: row["count"] for row in sections_data} if sections_data else {}
        }
    
    @staticmethod
    def get_students_for_table() -> List[List]:
        """Get students data formatted for table display"""
        students = StudentsService.get_all_students()
        
        # Convert to list of lists for table display
        table_data = []
        for student in students:
            row = [
                student.get("id", ""),
                student.get("student_number", ""),
                f"{student.get('first_name', '')} {student.get('last_name', '')}".strip(),
                student.get("section", ""),
                student.get("created_at", "").strftime("%Y-%m-%d") if student.get("created_at") else ""
            ]
            table_data.append(row)
        
        return table_data
    
    @staticmethod
    def get_table_headers() -> List[str]:
        """Get table headers for students table"""
        return ["ID", "Student Number", "Full Name", "Section", "Created Date"]

# Convenience functions for easy access
def get_all_students():
    """Convenience function to get all students"""
    return StudentsService.get_all_students()

def search_students(term):
    """Convenience function to search students"""
    return StudentsService.search_students(term)

def get_students_count():
    """Convenience function to get students count"""
    return StudentsService.get_students_count()
