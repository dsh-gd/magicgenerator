import json
import random
import unittest
from argparse import Namespace
from unittest import mock

from app.cli import check_arguments
from magicgenerator.generate import generate_dict

random.seed(42)


class TestCheckArguments(unittest.TestCase):
    def setUp(self):
        self.args = Namespace(
            path_to_save_files="./data",
            files_count=0,
            file_name="output",
            file_prefix="count",
            data_schema='{"number": "int:rand"}',
            data_lines=1000,
            clear_path=False,
        )

    def test_all_args_are_valid(self):
        self.assertEqual(check_arguments(self.args), True)

    def test_path_to_save_files(self):
        self.args.path_to_save_files = "./generated_data"
        self.assertEqual(check_arguments(self.args), False)

        self.args.path_to_save_files = "./README.md"
        self.assertEqual(check_arguments(self.args), False)

    def test_files_count(self):
        self.args.files_count = 1
        self.assertEqual(check_arguments(self.args), True)

        self.args.files_count = -1
        self.assertEqual(check_arguments(self.args), False)

    def test_file_name(self):
        self.args.file_name = ""
        self.assertEqual(check_arguments(self.args), False)

    def test_file_prefix(self):
        self.args.file_prefix = "count"
        self.assertEqual(check_arguments(self.args), True)

        self.args.file_prefix = "random"
        self.assertEqual(check_arguments(self.args), True)

        self.args.file_prefix = "uuid"
        self.assertEqual(check_arguments(self.args), True)

        self.args.file_prefix = "other"
        self.assertEqual(check_arguments(self.args), False)

    def test_data_schema(self):
        self.args.data_schema = '{"name": "str:rand"}'
        self.assertEqual(check_arguments(self.args), True)

        self.args.data_schema = '{"date":"timestamp:", "name": "str:rand", "type":"str:[\'client\', \'partner\', \'government\']", "age": "int:rand(1, 90)"}'
        self.assertEqual(check_arguments(self.args), True)

        self.args.data_schema = '{number: "int:rand"}'
        self.assertEqual(check_arguments(self.args), False)

        self.args.data_schema = '{date: "timestamp:rand"}'
        self.assertEqual(check_arguments(self.args), False)

        self.args.data_schema = '(number: "int:rand")'
        self.assertEqual(check_arguments(self.args), False)

        self.args.data_schema = "./README.md"
        self.assertEqual(check_arguments(self.args), False)

    def test_data_lines(self):
        self.args.data_lines = 0
        self.assertEqual(check_arguments(self.args), False)


class TestGenerateData(unittest.TestCase):
    @mock.patch("time.time", mock.MagicMock(return_value=12345))
    @mock.patch("uuid.uuid4", mock.MagicMock(return_value="f0b8be8f-ef67-47fe-83a5-f205403ac3f0"))
    def test_generate_dict(self):
        s = '{"number": "int:rand"}'
        data_schema = json.loads(s)
        d = {"number": 1824}
        self.assertEqual(generate_dict(data_schema), d)

        s = '{"date":"timestamp:", "name": "str:rand", "type":"str:[\'client\', \'partner\', \'government\']", "age": "int:rand(1, 90)"}'
        data_schema = json.loads(s)
        d = {"age": 36, "date": 12345, "name": "f0b8be8f-ef67-47fe-83a5-f205403ac3f0", "type": "client"}
        self.assertEqual(generate_dict(data_schema), d)

        s = '{"date": "timestamp:rand"}'
        data_schema = json.loads(s)
        d = {}
        self.assertEqual(generate_dict(data_schema), d)

        s = '{"digit": "int:[0, 1, 2, 3, 4, 5, 6, 7, 8, 9]"}'
        data_schema = json.loads(s)
        d = {"digit": 3}
        self.assertEqual(generate_dict(data_schema), d)

        s = '{"number": "int:rand(1, 1000)"}'
        data_schema = json.loads(s)
        d = {"number": 229}
        self.assertEqual(generate_dict(data_schema), d)

        s = '{"name": "str:cat"}'
        data_schema = json.loads(s)
        d = {"name": "cat"}
        self.assertEqual(generate_dict(data_schema), d)

        s = '{"number": "int:100"}'
        data_schema = json.loads(s)
        d = {"number": 100}
        self.assertEqual(generate_dict(data_schema), d)

        s = '{"empty_int": "int:", "empty_str": "str:"}'
        data_schema = json.loads(s)
        d = {"empty_int": None, "empty_str": ""}
        self.assertEqual(generate_dict(data_schema), d)

        with self.assertRaises(SystemExit):
            s = '{"number": "int"}'
            data_schema = json.loads(s)
            generate_dict(data_schema)

        with self.assertRaises(SystemExit):
            s = '{"number": "float:rand"}'
            data_schema = json.loads(s)
            generate_dict(data_schema)

        with self.assertRaises(SystemExit):
            s = '{"number": "int:[1, 2, 3.5]"}'
            data_schema = json.loads(s)
            generate_dict(data_schema)

        with self.assertRaises(SystemExit):
            s = '{"number": "int:rand(100)"}'
            data_schema = json.loads(s)
            generate_dict(data_schema)

        with self.assertRaises(SystemExit):
            s = '{"number": "int:rand(100, 0)"}'
            data_schema = json.loads(s)
            generate_dict(data_schema)


if __name__ == "__main__":
    unittest.main()
