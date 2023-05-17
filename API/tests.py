import gaming_copy
import unittest

def test_set_value_if():
    # Test case 1: When value is None, return result
    assert gaming_copy.set_value_if(None, "==", 10, "true") == "true"

    # Test case 2: When op is "<" and value < test_value, return result
    assert gaming_copy.set_value_if(5, "<", 10, "false") == "false"

    # Test case 3: When op is ">=" and value >= test_value, return value
    assert gaming_copy.set_value_if(15, ">=", 10, "true") == 15

    # Test case 4: When op is invalid, return value
    assert gaming_copy.set_value_if(20, "invalid", 10, "true") == 20


def test_test_value():
    # Test case 1: When value is None, return True
    assert gaming_copy.test_value(None, "==", 10) == True

    # Test case 2: When op is "<" and value < test_value, return True
    assert gaming_copy.test_value(5, "<", 10) == True

    # Test case 3: When op is ">=" and value >= test_value, return False
    assert gaming_copy.test_value(5, ">=", 10) == False

    # Test case 4: When op is invalid, return False
    assert gaming_copy.test_value(20, "invalid", 10) == False

class TestUpdate(unittest.TestCase):
    def test_update_single_condition(self):
        # Test updating a list with a single condition
        lst = [1, 2, 3]
        filters = [(0, '==', 1, 5)]
        result = gaming_copy.update(lst, filters)
        self.assertEqual(result, [5, 2, 3])

    def test_update_double_condition(self):
        # Test updating a list with a double condition
        lst = [1, 2, 3, 4]
        filters = [(0, '==', 1, 5, 3, '>=', 6, 6, False)]
        result = gaming_copy.update(lst, filters)
        self.assertEqual(result, [5, 2, 3, 4])

    def test_update_no_conditions(self):
        # Test updating a list with no conditions
        lst = [1, 2, 3]
        filters = []
        result = gaming_copy.update(lst, filters)
        self.assertEqual(result, [1, 2, 3])

if __name__ == '__main__':
    unittest.main()
