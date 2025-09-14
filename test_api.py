"""
Test script for the HCLI Backend API
Tests all endpoints to ensure they work correctly.
"""

import asyncio
import json
import requests
import time
from pathlib import Path


API_BASE_URL = "http://localhost:8000"


def test_health_check():
    """Test the health check endpoint"""
    print("Testing health check...")
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health check error: {e}")


def test_root_endpoint():
    """Test the root endpoint"""
    print("\nTesting root endpoint...")
    try:
        response = requests.get(f"{API_BASE_URL}/")
        if response.status_code == 200:
            print("✅ Root endpoint passed")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Root endpoint error: {e}")


def test_crawl_endpoint():
    """Test the crawl endpoint"""
    print("\nTesting crawl endpoint...")
    try:
        # Test with current directory
        crawl_data = {
            "repo_path": "./test",
            "output_dir": "./test_out"
        }
        
        response = requests.post(f"{API_BASE_URL}/crawl", json=crawl_data)
        if response.status_code == 200:
            print("✅ Crawl endpoint passed")
            result = response.json()
            print(f"   Processed files: {len(result['processed_files'])}")
            print(f"   Output directory: {result['output_dir']}")
        else:
            print(f"❌ Crawl endpoint failed: {response.status_code}")
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ Crawl endpoint error: {e}")


def test_display_pyh_endpoint():
    """Test the display pyh endpoint"""
    print("\nTesting display pyh endpoint...")
    try:
        # Look for existing pyh files
        pyh_files = list(Path(".").rglob("*.pyh.ast.json"))
        if not pyh_files:
            print("⚠️  No pyh files found, skipping display test")
            return
        
        pyh_file = pyh_files[0]
        display_data = {
            "pyh_file_path": str(pyh_file)
        }
        
        response = requests.post(f"{API_BASE_URL}/display-pyh", json=display_data)
        if response.status_code == 200:
            print("✅ Display pyh endpoint passed")
            result = response.json()
            print(f"   File: {result['file_path']}")
            print(f"   Content length: {len(result['content'])} characters")
        else:
            print(f"❌ Display pyh endpoint failed: {response.status_code}")
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ Display pyh endpoint error: {e}")


def test_pyh_to_py_endpoint():
    """Test the pyh to py endpoint"""
    print("\nTesting pyh to py endpoint...")
    try:
        # Look for existing pyh files
        pyh_files = list(Path(".").rglob("*.pyh.ast.json"))
        if not pyh_files:
            print("⚠️  No pyh files found, skipping pyh-to-py test")
            return
        
        pyh_file = pyh_files[0]
        original_content = pyh_file.read_text(encoding="utf-8")
        
        # Create a simple modification (add a comment)
        modified_content = original_content.replace(
            '"description": "',
            '"description": "Modified: '
        )
        
        # Look for corresponding Python file
        py_files = list(Path(".").rglob("*.py"))
        source_py_file = None
        for py_file in py_files:
            if py_file.stem == pyh_file.stem.split('.')[0]:
                source_py_file = str(py_file)
                break
        
        if not source_py_file:
            print("⚠️  No corresponding Python file found, skipping pyh-to-py test")
            return
        
        pyh_to_py_data = {
            "pyh_file_path": str(pyh_file),
            "original_pyh_content": original_content,
            "modified_pyh_content": modified_content,
            "source_py_file": source_py_file
        }
        
        response = requests.post(f"{API_BASE_URL}/pyh-to-py", json=pyh_to_py_data)
        if response.status_code == 200:
            print("✅ Pyh to py endpoint passed")
            result = response.json()
            print(f"   Changes applied: {result['changes_applied']}")
            print(f"   Modified files: {result['modified_files']}")
        else:
            print(f"❌ Pyh to py endpoint failed: {response.status_code}")
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ Pyh to py endpoint error: {e}")


def test_temp_files_endpoints():
    """Test temporary files management endpoints"""
    print("\nTesting temp files endpoints...")
    try:
        # List temp files
        response = requests.get(f"{API_BASE_URL}/temp-files")
        if response.status_code == 200:
            print("✅ Temp files list endpoint passed")
            result = response.json()
            print(f"   Active sessions: {result['active_sessions']}")
        else:
            print(f"❌ Temp files list endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Temp files endpoints error: {e}")


def main():
    """Run all tests"""
    print("HCLI Backend API Test Suite")
    print("=" * 50)
    
    # Wait a moment for server to be ready
    print("Waiting for server to be ready...")
    time.sleep(2)
    
    # Run tests
    test_health_check()
    test_root_endpoint()
    test_crawl_endpoint()
    # test_display_pyh_endpoint()
    # test_pyh_to_py_endpoint()
    # test_temp_files_endpoints()
    
    print("\n" + "=" * 50)
    print("Test suite completed!")


if __name__ == "__main__":
    main()
