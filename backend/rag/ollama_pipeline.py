from langchain.document_loaders import CSVLoader
from langchain.embeddings.sentence_transformer import SentenceTransformerEmbeddings
from langchain.vectorstores import Chroma
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_ollama.llms import OllamaLLM
from langchain.text_splitter import RecursiveCharacterTextSplitter


class OllamaPipeline:

    def __init__(self, model_name,localhost,port,embedding_function_type,context_path):
        self.model_name = model_name
        self.localhost = localhost
        self.port = port
        self.embedding_function_type = embedding_function_type
        self.context_path = context_path
        self.embeddings = SentenceTransformerEmbeddings(model_name=self.embedding_function_type)
        self.loader = CSVLoader(file_path=self.context_path)
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=1024, chunk_overlap=100)

    def create_vectorstore(self):
        documents = self.loader.load()
        self.db = Chroma.from_documents(documents, self.embeddings)


    def setup_query(self):
        self.create_vectorstore()
        template = """Only Answer what disease the patient has based on the data given below about disease and symptoms (and please do
        not mention about documents while giving answer):
        {context}

        Question: {question}
        """
        self.prompt = ChatPromptTemplate.from_template(template)
        self.model = OllamaLLM(model=self.model_name,host=self.localhost,port=self.port)
        self.chain = (
            {"context": self.db.as_retriever(), "question": RunnablePassthrough()}
            | self.prompt
            | self.model
            | StrOutputParser()
        )
        
    def query(self,question):
        return self.chain.invoke(question)

if __name__ == "__main__":
    context_path = "/mnt/sda/hophacks/backend/symptom-disease-dataset.csv"
    pipeline = OllamaPipeline(model_name="llama3.1",localhost="localhost",port=11434,
                embedding_function_type="all-MiniLM-L6-v2",context_path=context_path)

    pipeline.setup_query()
    out  = pipeline.query("I'm feeling headache, dizzness and cough")
    print(out)