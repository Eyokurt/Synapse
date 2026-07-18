import os
from synapse.tools.builtin.file_system import read_file, write_file, list_directory

def test_write_and_read_file(tmp_path):
    filepath = tmp_path / "test.txt"
    content = "Hello, world!"
    
    # Test write
    result = write_file(str(filepath), content)
    assert "Successfully wrote" in result
    assert os.path.exists(filepath)
    
    # Test read
    read_content = read_file(str(filepath))
    assert read_content == content

def test_list_directory(tmp_path):
    (tmp_path / "file1.txt").touch()
    (tmp_path / "file2.txt").touch()
    (tmp_path / "dir1").mkdir()
    
    items = list_directory(str(tmp_path))
    assert len(items) == 3
    assert "file1.txt" in items
    assert "file2.txt" in items
    assert "dir1" in items
