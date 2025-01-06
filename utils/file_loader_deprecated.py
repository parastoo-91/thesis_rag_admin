from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from pypdf import PdfReader
import logging
from io import BytesIO

class chunker:
    def __init__(self, ChunkSize, ChunkOverlap):
       self.ChunkSize = ChunkSize
       self.ChunkOverlap = ChunkOverlap
       self.ch_logger = logging.getLogger("__name__")
       self.ch_logger.setLevel(level=logging.INFO)
       


    def __merge_dicts(self, dict1,*args):
        """
        can be used to merge multiple dicts
        """
        fin_dict = dict1
        for i in args:
           fin_dict.update(i)
        return fin_dict
     
    def __extract_pdf_metadata(self,pdf)->dict:
       """
       Extracts metadata from the PDF file.
       """
       pdf_reader = pdf
       metadata = {
        "Author": pdf_reader.metadata.author,
        "Title": pdf_reader.metadata.title,
        "Subject": pdf_reader.metadata.subject
        #"Producer":pdf_reader.metadata.producer
        #"CreationDate": pdf_reader.metadata.creation_date.strftime("%m/%d/%Y, %H:%M:%S"),
        #"ModDate": pdf_reader.metadata.modification_date.strftime("%m/%d/%Y, %H:%M:%S")
        }
       return metadata
    
    def __extract_pdf_text(self,pdf)->str:
       pdf_reader = pdf
       text = ''
       for page_num in range(0,len(pdf_reader.pages)):
          page = pdf_reader.pages[page_num]
          text += page.extract_text()
       return text
    

    def pdf_read(self,uploaded_file):
       bytes_pdf = BytesIO(uploaded_file.read())
       pdf =  PdfReader(bytes_pdf)
       return pdf
       
    def pdf_metadata_checker(self,pdf)->dict:
       pdf_metadata = self.__extract_pdf_metadata(pdf)
       status_list = []
       
       for key, value in pdf_metadata.items():
          if value is not None:
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
       return {"status":overall_status, "status_description":overall_status_description,"validation_results":validation_results}
         

    def pdf_load(self,pdf,**kwargs):
       """
       FilePath = Path to the PDF File
       ChunkSize = Size of the Chunks
       ChunkOverlap = Overlap of the Chunks
       *kwargs = further metadata to be added
       """
       pdf_metadata = self.__extract_pdf_metadata(pdf)
       pdf_text = self.__extract_pdf_text(pdf)
       text_splitter = RecursiveCharacterTextSplitter(
       chunk_size=self.ChunkSize, chunk_overlap=self.ChunkOverlap, keep_separator=False)
       pdf_chunks = text_splitter.split_text(pdf_text)
       update_dict = {}
       self.ch_logger.info("Working on file")
       for key,value in kwargs.items():
          update_dict[key] = value
       doc_list =  list(map(lambda doc: Document(page_content= doc , metadata= self.__merge_dicts(pdf_metadata, update_dict))  ,pdf_chunks))
       
       return doc_list

