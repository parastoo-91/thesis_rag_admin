from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from pypdf import PdfReader
import logging
from docling.document_converter import DocumentConverter
from docling.datamodel.base_models import InputFormat
from docling.document_converter import (
    DocumentConverter,
    PdfFormatOption,
    WordFormatOption,
)
from docling.pipeline.simple_pipeline import SimplePipeline
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.backend.pypdfium2_backend import PyPdfiumDocumentBackend
from pptx import Presentation
from docx import Document as wdoc


class chunker:
    def __init__(self, ChunkSize, ChunkOverlap):
       """
       Initializes the chunker with specified chunk size and overlap.

       Args:
           ChunkSize (int): The size of each chunk when splitting the text.
           ChunkOverlap (int): The number of overlapping characters between chunks.
       """
       self.ChunkSize = ChunkSize
       self.ChunkOverlap = ChunkOverlap
       self.ch_logger = logging.getLogger(__name__)
       self.ch_logger.setLevel(level=logging.INFO)
       
    def __merge_dicts(self, dict1,*args)->dict:
        """
        Merges multiple dictionaries into one.

        Args:
            dict1 (dict): The first dictionary to merge.
            *args (dict): Additional constants to merge into the dics.

        Returns:
            dict: A single dictionary containing all key-value pairs.
        """
        fin_dict = dict1
        for i in args:
           fin_dict.update(i)
        return fin_dict
     
    def extract_pdf_metadata(self,file_path:str,file_name:str)->dict:
       """
       Extracts metadata from a PDF file.

       Args:
           file_path (str): The file path of the PDF document.
           file_name (str): The name of the PDF file.

       Returns:
           dict: A dictionary containing extracted metadata fields.
       """
       self.ch_logger.info(f"Extracting metadata of {file_path}")
       f= open(file_path,"rb")
       pdf_reader = PdfReader(f)
       metadata = {
        "Author": pdf_reader.metadata.author,
        "Title": pdf_reader.metadata.title,
        #"Subject": pdf_reader.metadata.subject,
        #"Producer":pdf_reader.metadata.producer
        #"CreationDate": pdf_reader.metadata.creation_date.strftime("%m/%d/%Y, %H:%M:%S"),
        #"ModDate": pdf_reader.metadata.modification_date.strftime("%m/%d/%Y, %H:%M:%S")
       "File Extension": 'pdf',
       "File Name": file_name
        }
       f.close()
       return metadata
    
    def extract_docx_metadata(self,file_path:str,file_name:str)->dict:
       """
       Extracts metadata from a DOCX file.

       Args:
           file_path (str): The file path of the DOCX document.
           file_name (str): The name of the DOCX file.

       Returns:
           dict: A dictionary containing extracted metadata fields.
       """
       self.ch_logger.info(f"Extracting metadata of {file_path}")
       f = open(file_path,"rb")
       word_file = wdoc(f)
       metadata = {
       "Title":    word_file.core_properties.title,
       "Author":   word_file.core_properties.author,
       "Created":  str(word_file.core_properties.created),
       #"Subject":  word_file.core_properties.subject,
       #"Category": word_file.core_properties.category,
       #"Comments": word_file.core_properties.comments,
       #"Status":   word_file.core_properties.content_status,
       #"Keywords": word_file.core_properties.keywords,
       "File Extension": 'docx',
       "File Name": file_name
       }           
       f.close()
       return metadata
    
    def extract_pptx_metadata(self,file_path:str,file_name:str)->dict:
       """
       Extracts metadata from a PPTX file.

       Args:
           file_path (str): The file path of the PPTX document.
           file_name (str): The name of the PPTX file.

       Returns:
           dict: A dictionary containing extracted metadata fields.
       """

       self.ch_logger.info(f"Extracting metadata of {file_path}")
       f = open(file_path,"rb")
       pptx_file = Presentation(f)
       metadata = {
       "Title":    pptx_file.core_properties.title,
       "Author":   pptx_file.core_properties.author,
       "Created":  str(pptx_file.core_properties.created),
       #"Subject":  pptx_file.core_properties.subject,
       #"Category": pptx_file.core_properties.category,
       #"Comments": pptx_file.core_properties.comments,
       #"Status":   pptx_file.core_properties.content_status,
       #"Keywords": pptx_file.core_properties.keywords,
       "File Extension": 'pptx',
       "File Name": file_name
       }           
       f.close()
       return metadata
    
    def document_converter_to_text(self,file_path:str,enable_ocr:bool)->str:
       """
       Converts a document to text using a document converter. The doc_converter contains the settings that are used for the document extraction. For example allowed document types.

       Args:
           file_path (str): The file path of the document to convert.
           enable_ocr (bool): Whether to enable OCR for text extraction from images.

       Returns:
           str: The extracted text from the document.
       """

       pipeline_options = PdfPipelineOptions()
       pipeline_options.do_ocr = enable_ocr
       pipeline_options.do_table_structure = True
       #...
       
       ## Custom options are now defined per format.
       doc_converter = (
           DocumentConverter(  # all of the below is optional, has internal defaults.
               allowed_formats=[
                   InputFormat.PDF,
                   InputFormat.IMAGE,
                   InputFormat.DOCX,
                   InputFormat.PPTX,
               ],  # whitelist formats, non-matching files are ignored.
               format_options={
                   InputFormat.PDF: PdfFormatOption(
                       pipeline_options=pipeline_options, # pipeline options go here.
                       backend=PyPdfiumDocumentBackend # optional: pick an alternative backend
                   ),
                   InputFormat.DOCX: WordFormatOption(
                       pipeline_cls=SimplePipeline # default for office formats and HTML
                   ),
               },
           )
       )
       
       self.ch_logger.info(f"Converting file {file_path} to text")
       con_file = doc_converter.convert(file_path)
       con_file_text = con_file.document.export_to_text()
     
       return con_file_text
    
    

    def metadata_checker(self,metadata:dict)->dict:
       """
       Validates the metadata fields and checks for their completeness.

       Args:
           metadata (dict): The metadata dictionary to validate.

       Returns:
           dict: A dictionary containing the validation status and results.
       """
       status_list = []
       for key, value in metadata.items():
          if value is not None and len(str(value)) > 0 :
             status_list =  status_list + [{"Field":key,"Status":"Success","Description":f":white_check_mark: - Successfully validated {key} with the value '{value}'"}]
          else: 
             status_list = status_list + [{"Field":key,"Status":"Failed","Description":f":exclamation: - Validation Failed for {key} -> None supplied"}] 
       overall_status = ""
       validation_results = []
       for s in status_list:
          if s["Status"] == "Success":
             if overall_status == "Failed":
                pass
             else: 
                overall_status = "Success"
                overall_status_description = ":face_with_monocle: Successful Metadata Validation :white_check_mark:"
             validation_results = validation_results + [s["Description"]]
          else: 
             overall_status = "Failed"
             overall_status_description = ":exclamation: Metadata Validation failed :exclamation:"
             validation_results = validation_results + [s["Description"]]
       return {"status":overall_status, "status_description":overall_status_description,"validation_results":validation_results,"status_list":status_list}
         
    def document_load(self,text:str,metadata:dict,**kwargs)->list: 
       """
       Loads the document text into chunks and attaches metadata.

       Args:
           text (str): The textual content of the document.
           metadata (dict): The metadata to attach to each chunk.
           **kwargs: Additional metadata to be added to each chunk.
       
       Returns:
           list: A list of Document objects containing chunked content and metadata.
       """

       text_splitter = RecursiveCharacterTextSplitter(
       chunk_size=self.ChunkSize, chunk_overlap=self.ChunkOverlap, keep_separator=False)
       pdf_chunks = text_splitter.split_text(text=text)
       update_dict = {}
       self.ch_logger.info("Loading File")
       for key,value in kwargs.items():
          update_dict[key] = value
       doc_list =  list(map(lambda doc: Document(page_content= doc , metadata= self.__merge_dicts(metadata, update_dict)),pdf_chunks))
       
       return doc_list

