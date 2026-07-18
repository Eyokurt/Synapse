from synapse.tools.builtin.system import get_current_time, execute_python

def test_get_current_time():
    # Test valid timezone
    time_utc = get_current_time("UTC")
    assert "UTC" in time_utc
    
    # Test invalid timezone
    time_err = get_current_time("Invalid/Timezone")
    assert "Error: Invalid timezone" in time_err

def test_execute_python():
    # Test simple print
    code = "print('Hello, world!')"
    output = execute_python(code)
    assert output.strip() == "Hello, world!"
    
    # Test exception
    code_with_error = "1 / 0"
    output_err = execute_python(code_with_error)
    assert "division by zero" in output_err
    
    # Test variable assignment and print
    code_with_vars = "a = 2\nb = 3\nprint(a + b)"
    output_vars = execute_python(code_with_vars)
    assert output_vars.strip() == "5"
