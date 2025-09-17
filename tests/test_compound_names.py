#!/usr/bin/env python3
"""
Test script to demonstrate compound name matching for face recognition
"""
import sys
import os

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.services.face.recognition_algorithm import find_student_by_folder_name

def test_compound_name_matching():
    """Test the compound name matching functionality"""
    
    # Sample student data with compound names
    students = [
        {
            'id': 1,
            'first_name': 'Maria Elena',
            'last_name': 'Garcia',
            'student_id': '2024-001',
            'section': 'A'
        },
        {
            'id': 2,
            'first_name': 'John Paul',
            'last_name': 'Smith',
            'student_id': '2024-002',
            'section': 'B'
        },
        {
            'id': 3,
            'first_name': 'Ana',
            'last_name': 'Maria Rodriguez',
            'student_id': '2024-003',
            'section': 'A'
        },
        {
            'id': 4,
            'first_name': 'Carlos',
            'last_name': 'Santos',
            'student_id': '2024-004',
            'section': 'C'
        },
        {
            'id': 5,
            'first_name': 'Mary Jane',
            'last_name': 'Watson',
            'student_id': '2024-005',
            'section': 'B'
        }
    ]
    
    # Test cases for folder names
    test_cases = [
        # (folder_name, expected_student_id, description)
        ("Garcia", 1, "Last name only"),
        ("Maria", 1, "First name part"),
        ("Elena", 1, "Middle name part"),
        ("Smith", 2, "Last name only"),
        ("John", 2, "First name part"),
        ("Paul", 2, "Middle name part"),
        ("Rodriguez", 3, "Last name only"),
        ("Ana", 3, "First name only"),
        ("Maria", 3, "Last name part (should match first Maria Elena)"),
        ("Santos", 4, "Last name only"),
        ("Carlos", 4, "First name only"),
        ("Watson", 5, "Last name only"),
        ("Mary", 5, "First name part"),
        ("Jane", 5, "Middle name part"),
        ("Unknown", None, "No match expected"),
    ]
    
    print("🧪 Testing Compound Name Matching")
    print("=" * 50)
    
    for folder_name, expected_id, description in test_cases:
        result = find_student_by_folder_name(folder_name, students)
        
        if result:
            actual_id = result['id']
            full_name = f"{result['first_name']} {result['last_name']}"
            status = "✅ PASS" if actual_id == expected_id else "❌ FAIL"
            print(f"{status} | Folder: '{folder_name}' -> {full_name} (ID: {actual_id}) | {description}")
        else:
            status = "✅ PASS" if expected_id is None else "❌ FAIL"
            print(f"{status} | Folder: '{folder_name}' -> No match | {description}")
    
    print("\n📋 Folder Naming Recommendations:")
    print("=" * 40)
    print("For best results, use these folder naming strategies:")
    print("1. Last name only: 'Garcia', 'Smith', 'Rodriguez'")
    print("2. First name only: 'Maria', 'John', 'Ana'")
    print("3. Any part of the name: 'Elena', 'Paul', 'Jane'")
    print("4. Full last name for compound surnames: 'Maria Rodriguez'")
    print("\nThe system will automatically match these to the correct student!")

if __name__ == "__main__":
    test_compound_name_matching()

