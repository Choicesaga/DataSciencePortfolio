from docling.document_converter import DocumentConverter
from pathlib import Path

def batch_convert_pdfs_to_markdown(input_dir: str, output_dir: str) -> str:
    
    input_path = Path(input_dir)
    output_path = Path(output_dir)

    # 1. Validation and Setup
    if not input_path.is_dir():
        return f"Error: Input path '{input_dir}' is not a valid directory or does not exist."

    # Create the output directory if it doesn't exist
    try:
        output_path.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        return f"Error: Could not create output directory '{output_dir}'. Details: {e}"

    try:
        converter = DocumentConverter()
    except Exception as e:
        return f"Error: Failed to initialize DocumentConverter. Check 'docling' installation. Details: {e}"

    converted_count = 0
    errors = []

    print(f"\n--- Starting Batch Conversion from {input_dir} to {output_dir} ---")

    # 2. Iterate through PDF files in the input directory
    for pdf_file in input_path.glob("*.pdf"):
        try:
            # 3. Perform Conversion
            # Using str(pdf_file) for compatibility with external libraries
            pdf_path_str = str(pdf_file)
            result = converter.convert(pdf_path_str).document
            markdown_text = result.export_to_markdown()

            # 4. Determine output file path (keep name, change extension)
            md_filename = pdf_file.stem + ".md"
            output_filepath = output_path / md_filename

            # 5. Export Markdown
            with open(output_filepath, 'w', encoding='utf-8') as f:
                f.write(markdown_text)

            print(f"  [SUCCESS] Converted {pdf_file.name} to {md_filename}")
            converted_count += 1

        except Exception as e:
            error_message = f"Error converting {pdf_file.name}: {e}"
            print(f"  [ERROR] {error_message}")
            errors.append(error_message)

    # 6. Summary and Return
    summary = f"\nBatch conversion complete. Successfully converted {converted_count} PDF file(s) into Markdown."
    if errors:
        summary += f"\n--- Warnings: {len(errors)} file(s) failed to convert. ---"
        for i, err in enumerate(errors, 1):
            summary += f"\n  {i}. {err}"

    return summary

def get_input_path():
    input_path = " "

    try:
        input_path = input("Please enter the input path for the pdf documents: ")

    except Exception as e:
        error_message = f"Error taking in {input_path}: {e}"
        print(error_message)

    return input_path

def get_output_path():
    output_path = " "

    try:
        output_path = input("Please enter the output path for the markdown documents: ")

    except Exception as e:
        error_message = f"Error taking in {output_path}: {e}"
        print(error_message)

    return output_path

if __name__ == '__main__':

    INPUT_FOLDER = get_input_path()
    OUTPUT_FOLDER = get_output_path()
    
    # Run the batch conversion
    result_summary = batch_convert_pdfs_to_markdown(INPUT_FOLDER, OUTPUT_FOLDER)
    print("\n" + "="*40)
    print(result_summary)
    print("="*40)