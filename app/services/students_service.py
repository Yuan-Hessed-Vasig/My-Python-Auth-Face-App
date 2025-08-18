"""
StudentsService - Specific operations for students data
Built on top of DataService for reusable database operations
Now with pagination support!
"""

from typing import List, Dict, Optional
from app.services.data_service import DataService
from app.services.pagination import PaginationParams, PaginationResult, PaginationService, get_pagination_defaults

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
    
    # ========== PAGINATION METHODS ==========
    
    @staticmethod
    def get_students_paginated(pagination_params: PaginationParams = None) -> PaginationResult:
        """
        Get students with pagination - like axios.get('/students', { params: { page, limit, search } })
        
        Args:
            pagination_params: Pagination parameters (optional, uses defaults if None)
        
        Returns:
            PaginationResult with students data and pagination metadata
        """
        if pagination_params is None:
            defaults = get_pagination_defaults("students")
            pagination_params = PaginationService.create_params(**defaults)
        
        # Define searchable columns
        search_columns = ["first_name", "last_name", "student_number", "section"]
        
        # Define allowed sort columns
        allowed_sort_columns = ["id", "student_number", "first_name", "last_name", "section", "created_at"]
        
        # Use DataService pagination
        return DataService.get_paginated(
            table_name="students",
            pagination_params=pagination_params,
            search_columns=search_columns,
            allowed_sort_columns=allowed_sort_columns
        )
    
    @staticmethod
    def get_students_for_table_paginated(pagination_params: PaginationParams = None) -> tuple:
        """
        Get paginated students data formatted for table display
        
        Returns:
            Tuple of (table_data, pagination_result)
        """
        result = StudentsService.get_students_paginated(pagination_params)
        
        # Convert to table format
        table_data = []
        for student in result.data:
            row = [
                student.get("id", ""),
                student.get("student_number", ""),
                f"{student.get('first_name', '')} {student.get('last_name', '')}".strip(),
                student.get("section", ""),
                student.get("created_at", "").strftime("%Y-%m-%d") if student.get("created_at") else ""
            ]
            table_data.append(row)
        
        return table_data, result
    
    @staticmethod
    def search_students_paginated(
        search_term: str, 
        pagination_params: PaginationParams = None
    ) -> PaginationResult:
        """
        Search students with pagination
        
        Args:
            search_term: Search term
            pagination_params: Pagination parameters (optional)
        
        Returns:
            PaginationResult with matching students
        """
        if pagination_params is None:
            defaults = get_pagination_defaults("students")
            pagination_params = PaginationService.create_params(**defaults)
        
        # Set search term in pagination params
        pagination_params.search_term = search_term
        
        return StudentsService.get_students_paginated(pagination_params)
    
    @staticmethod
    def get_students_by_section_paginated(
        section: str,
        pagination_params: PaginationParams = None
    ) -> PaginationResult:
        """
        Get students by section with pagination
        
        Args:
            section: Section name
            pagination_params: Pagination parameters (optional)
        
        Returns:
            PaginationResult with students from the section
        """
        if pagination_params is None:
            defaults = get_pagination_defaults("students")
            pagination_params = PaginationService.create_params(**defaults)
        
        # Add section filter
        pagination_params.filters = {"section": section}
        
        return StudentsService.get_students_paginated(pagination_params)

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
