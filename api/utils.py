import ast
from typing import List


def convert_literal(test_cases: str="[{'id': 1, 'input': '[2, 7, 11, 15], 9', 'expected': '[0, 1]'}, {'id': 2, 'input': '[3, 2, 4], 6', 'expected': '[1, 2]'}]"):
    """convert a string representation of List/Tuple into a list[objects].

    Args:
        test_cases: [str]: string representation of objects to get converted
    Returns:
        list: list of converted datatypes
        False: if any errors occurred during conversion
    """
    obj =  ast.literal_eval(test_cases)
    if not isinstance(obj, tuple):
        obj = [obj]

    obj = obj[0]
    # obj will look like this: [{'id': 1, 'input': '[2, 7, 11, 15], 9', 'expected': '[0, 1]'},
    #                           {'id': 2, 'input': '[3, 2, 4], 6', 'expected': '[1, 2]'}]
    # as you see here the input/expected are in string format and we dont want that 
    # down below we are converting those:
    testcases = []
    for testcase in obj:
        new_testcase = testcase.copy()
        for key in testcase:
            if key == "input" or key == "expected" and isinstance(testcase[key], str):
                # print("testcase[key]: ", testcase[key], type(testcase[key]))
                new_testcase[key] = ast.literal_eval(testcase[key])
        testcases.append(new_testcase)
    return testcases
convert_literal()
def check_test_case_pass(test_cases: List, test_result: List) -> List:
    """
    Compares the expected output of test cases with the actual output from the code runner
    
    Args:
        test_cases (List): a list of test cases where each test case is a dictionary
            containing the keys 'id', 'input', 'expected'
        test_result (List): a list of test results where each result is a dictionary
            containing the keys 'id', 'output', 'error', 'error_message'
    
    Returns:
        List: list of passed test cases
        bool: True if all test cases passed
    """
    print(f"test_cases: {test_cases}")
    print(f"test_result: {test_result}")

    passed_count = 0
    compared_list = []
    if not test_result or not test_result:
        compared_list.append({
            "test_case": test_cases,
            "test_result": test_result,
            "passed": False
        })
    for testcase, result in zip(test_cases, test_result):
        if testcase.get('expected') == result.get('output'):
            passed_count += 1
            compared_list.append({
                "test_case": testcase,
                "your_result": result,
                "passed": True
            })
        else:
            compared_list.append({
                "test_case": testcase,
                "your_result": result,
                "passed": False
            })
            break

    return compared_list, passed_count == len(test_cases)


# {'execution_id': '123', 'test_result': [{'id': 1, 'output': 3, 'error': None, 'error_message': None}, {'id': 2, 'output': 5, 'error': None, 'error_message': None}]}
