from unique_people_etl.reader import FileProcesser
import pandas as pd
from unittest import TestCase


class BaseTest(TestCase):

    file_processer = FileProcesser()

    def test_normalize_unicode_to_ascii(self):
        input_string = "Mickæël"
        expected = 'mickel'

        real = self.file_processer._normalize_unicode_to_ascii(input_string)
        assert real == expected

    def test_name_encoding(self):
        input_string = "Mickæël"
        expected = 'MKLMACAL'
        real = self.file_processer._name_encoding(input_string)
        assert real == expected

    def test_clean_data(self):
        prune_column = "column_test_name"
        input_data = {prune_column: ["['Yann Sommer', 'Granit Xaka', 'Xherdan Shaqiri']",
                                     "['Granit Xhaka', 'Yan Somer', 'Xerdan Shaquiri']"],
                      'Number': [32, 28]}

        input_df = pd.DataFrame(input_data)
        expected_df = pd.DataFrame([('Yann Sommer'),
                                    ('Granit Xaka'),
                                    ('Xherdan Shaqiri'),
                                    ('Granit Xhaka'),
                                    ('Yan Somer'),
                                    ('Xerdan Shaquiri')],
                                   index=[0, 0, 0, 1, 1, 1],
                                   columns=[prune_column])
        real = self.file_processer._clean_data(input_df, prune_column)
        assert real["column_test_name"].equals(expected_df["column_test_name"])


