import argparse
import ast
import unicodedata
import re
from collections import defaultdict
from pathlib import Path
from typing import Optional
from fuzzy import nysiis
from metaphone import doublemetaphone
import pandas as pd


class FileProcesser:

    def _name_encoding(self, name1: str) -> str:
        name1_unicode = self._normalize_unicode_to_ascii(name1)
        name_list = self._name_to_list(name1_unicode)
        clean_name = " ".join(name_list)
        return doublemetaphone(clean_name)[0] + doublemetaphone(clean_name)[1] + nysiis(clean_name)

    def _processing(self, data: pd.DataFrame) -> dict:
        authors_df = self._clean_data(data)
        unique_authors_dict = defaultdict(list)
        for idx, row in authors_df.iterrows():
            name_encoded = self._name_encoding(row['authors'])
            unique_authors_dict[name_encoded].append(row['authors'])
        return unique_authors_dict

    @staticmethod
    def _name_to_list(name1: str) -> list:
        name_list = name1.split(' ')
        name_list.sort()
        return name_list

    @staticmethod
    def _normalize_unicode_to_ascii(word_data: str) -> str:
        normal = unicodedata.normalize('NFKD', word_data).encode('ASCII', 'ignore')
        word = normal.decode("utf-8")
        word = word.lower()
        re.sub('[^A-Za-z0-9 ]+', '', word)
        re.sub(' +', ' ', word)
        return word

    @staticmethod
    def _clean_data(df: pd.DataFrame, prune_column_name: str = 'authors') -> pd.DataFrame:
        authors_df = df.loc[:, [prune_column_name]]
        authors_df = authors_df.loc[~authors_df[prune_column_name].isnull()]
        authors_df[prune_column_name] = authors_df[prune_column_name].apply(lambda x: ast.literal_eval(x))
        authors_df = authors_df.explode(prune_column_name)
        authors_df = authors_df.drop_duplicates()
        return authors_df

    @staticmethod
    def _writer(name_file: str, unique_dict: dict, header: Optional[str] = None):
        with open(name_file, 'w') as file:
            if header:
                file.write(f'{header}\n')
            for encode in unique_dict:
                final_name = max(unique_dict[encode], key=len)
                final_name_list = final_name.split(" ")
                firstname, lastname = " ".join(final_name_list[:len(final_name_list) - 1]), final_name_list[
                    len(final_name_list) - 1]
                file.write(f"{firstname},{lastname}\n")

    def run(self, input_filename: str = "publications_min.csv.gz",
            output_filename: str = "unique_people.csv",
            header: str = "firstname,lastname"):
        data = pd.read_csv(f'{Path(__file__).parents[1]}/{input_filename}',
                           compression='gzip',
                           error_bad_lines=False)
        unique_authors_dict = self._processing(data)
        self._writer(output_filename, unique_authors_dict, header)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--input', dest='input_filename', help='Input File Name', default="publications_min.csv.gz",
                        required=False)
    parser.add_argument('--output', dest='output_filename', help='Output File Name', default="unique_people.csv",
                        required=False)
    parser.add_argument('--header', dest='header', help='Headers', default="firstname,lastname", required=False)
    args = parser.parse_args()
    file_processer = FileProcesser()
    file_processer.run(args.input_filename, args.output_filename, args.header)
    print("FINISHED!!")
