from pyhtml2pdf import converter
from pypdf import PdfWriter
from tqdm import tqdm

import os
import pandas as pd


DB_FILE_NAME = 'All That Lies in Between 8179e5d842d142459bb30a712bcb8df7'
NOTION_EXPORT_DIR_PATH = ''


acceptable_status_list = [
    '📗 Published',
    '📑 Ready',
    '📄 Finished Draft',
]

def convert_html_to_pdf(book_name, file_name):
    output_dir_path = f"{NOTION_EXPORT_DIR_PATH}/pdf/{book_name}"
    os.makedirs(output_dir_path, exist_ok=True)
    output_file_path = f"{output_dir_path}/{file_name.replace('.html', '.pdf')}"

    if not os.path.isfile(output_file_path):    
        converter.convert(
            f'file:///{NOTION_EXPORT_DIR_PATH}/{DB_FILE_NAME}/{file_name}',
            output_file_path,
            compress=True, power=4,
            print_options={
                "scale": 1.5,
                "marginTop": 0.1,
                "marginLeft": 0.1,
                "marginRight": 0.1,
                "marginBottom": 0.1,
            }
        )

def merge_pdfs(book_name, file_names):
    merger = PdfWriter()

    for file_name in file_names:
        pdf = f"{NOTION_EXPORT_DIR_PATH}/pdf/{book_name}/{file_name.replace('.html', '.pdf')}"
        merger.append(pdf)

    merger.write(f"{NOTION_EXPORT_DIR_PATH}/{book_name}.pdf")
    merger.close()

def main():
    df = pd.read_csv(f'{NOTION_EXPORT_DIR_PATH}/{DB_FILE_NAME}.csv')
    df = df[(df['Status'].isin(acceptable_status_list)) & (df['No.'] != '')]
    df = df.dropna(subset=['No.'])
    file_names = sorted(os.listdir(f'{NOTION_EXPORT_DIR_PATH}/{DB_FILE_NAME}'))
    
    print(f"Total chapters: {len(df)}")
    print(f"Total books: {len(df['Book'].unique())}")

    for book in df['Book'].unique():
        book_df = df[df['Book'] == book]
        clean_book_name = book.replace(":", " -")

        print(f"\t- {book}: {len(book_df)}")

        i = 0
        chapter_file_names = []
        for chapter_title in tqdm(book_df['Chapter Title']):
            chapter_title = chapter_title.replace(".", " ").replace(":", "")
            while i < len(file_names):
                if file_names[i].endswith(".html") and file_names[i].startswith(chapter_title):
                    chapter_file_names.append(file_names[i])
                    convert_html_to_pdf(clean_book_name, chapter_file_names[-1])
                    i += 1
                    break
                else:
                    i += 1
        merge_pdfs(clean_book_name, chapter_file_names)
        
if __name__ == '__main__':
    main()