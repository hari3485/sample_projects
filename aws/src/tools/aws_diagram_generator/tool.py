import os
import re
import sys
import uuid
import contextlib
from io import StringIO
from src.engine.gateway import GatewayEngine
from dotenv import load_dotenv
load_dotenv()



def generate_random_filename():
    """Generates a random filename for the diagram."""
    return f"aws_diagram_{uuid.uuid4().hex[:8]}"


class AWS_Diagram_Generator_Tool:
    require_llm_engine = True

    def __init__(self, model_string="gpt-4o-mini"):
        self.model_string = model_string
        self.llm_engine = GatewayEngine(model_string=model_string)


    @staticmethod
    def preprocess_code(code):
        """
        Extracts Python code from a generated response.
        """
        match = re.search(r"```python(.*?)```", code, re.DOTALL)
        if match:
            return match.group(1).strip()
        return code.strip()

    @contextlib.contextmanager
    def capture_output(self):
        """
        Context manager to capture the standard output.
        """
        new_out = StringIO()
        old_out = sys.stdout
        sys.stdout = new_out
        try:
            yield sys.stdout
        finally:
            sys.stdout = old_out

    def execute_code_snippet(self, code):
        """
        Executes the given Python code snippet safely.
        """
        dangerous_functions = ['exit', 'quit', 'sys.exit']
        for func in dangerous_functions:
            code = re.sub(rf'{func}\s*\([^)]*\)', '', code)

        try:
            # Generate a random filename
            random_filename = generate_random_filename()
            code = code.replace("\"temp\"", f"\"{random_filename}\"")

            print(code)
            execution_code = self.preprocess_code(code)
            local_vars = {}

            with self.capture_output() as output:
                exec(execution_code, {}, local_vars)

            printed_output = output.getvalue().strip()

            # Check if the file was created and return its full path
            image_path = f"{random_filename}.png"
            if os.path.exists(image_path):
                return {"image": os.path.abspath(image_path)}
            else:
                return {"error": "No image file was generated."}

        except Exception as e:
            print(e, e)
            return {"error": str(e)}

    def execute(self, image, prompt):
        print(f"\nGenerating AWS Diagram for: {prompt}")

        system_prompt = (
            """
            **You are an expert in AWS architecture diagrams**, specializing in converting system architecture images into AWS-based diagrams using the diagrams library in Python.
            
            Your goal is to **map generic components** in the image to **AWS services** while preserving the structure, hierarchy, and theme of the input diagram.

            If **no AWS equivalent is found**, default to **general components** from the original image while ensuring that each service is labeled with both:
             1. **The functionality name as provided in original diagram** (e.g., "Object Storage" for Amazon S3)**
             2. **The corresponding AWS icon name (e.g., S3)**
            ### **Key Requirements:**
                **Image as the Primary Reference**
            - Use the **architecture image** as the **main input** to generate the AWS-based diagram.
            - Replace **generic components** with their **AWS equivalents**, ensuring both the **service name and icon name** are displayed.
            - If a **direct AWS mapping is unavailable**, use **general elements** (e.g., General, User, Users) while preserving structure.

                **AWS Service Replacement Rules:**
            - Replace all **compute, storage, database, networking, security, analytics, ML, integration, and migration components** with AWS services.
            - Use **only the AWS services listed below (strict validation required)**.
            - Maintain **correct imports** (e.g., EMR from `diagrams.aws.analytics`, StepFunctions from `diagrams.aws.integration`).
            - Do **not** include non-existent  or incorrect imports.
            - Each AWS component must be labeled with:
	            -	**Functionality name (top row)**
	            -	**AWS icon name (bottom row, from the diagrams library)** (e.g., S3)
            - Format:
                ```code <Functionality Name>\n<AWS Icon Name>```"

                **Logical Flow & Structure:**
            - Ensure **logical data flow** is **preserved** (e.g., ingestion → storage → processing → querying).
            - Maintain **hierarchy and relationships** between components.
            - Label each AWS service with both:
                - **Functionality name (descriptive)**
                - **The AWS icon name (technical)**
                ** Handling Missing AWS Services**
            - If no relevant AWS service is found for a component, fall back to general elements:
                - General (for unknown or unsupported components).
                - User / Users (for user-related elements).
                - Ensure both **labels (AWS service name & icon name)** follow the same format for consistency.

                **Output Formatting:**
            - Generate Python code that creates the diagram and saves it to a file.
            - Use the following code structure:
                ```python
                from diagrams import Diagram
                from diagrams.aws.ml import Sagemaker
                from diagrams.aws.storage import S3
                from diagrams.aws.general import General
                from diagrams.aws.management import Cloudwatch

                # Create diagram with a temporary filename
                with Diagram("AWS Architecture", show=False, outformat="png", filename="temp") as diag:
                    # Your diagram components here
                    pass
                ```
            - IMPORTANT: The diagram should be generated only ONCE in the code.
            - Do NOT include any additional diagram generation or display code.
            - Do NOT include any file handling or cleanup code.
            - The script **must run without errors**. If any issue arises, **adjust and retry**.
            ---

            ### **Allowed AWS Services (Strictly Mapping):**
            ** Mobile:**
            - APIGateway: diagrams.aws.mobile.APIGateway
            ** Analytics:**
            - AmazonOpensearchService: diagrams.aws.analytics.AmazonOpensearchService
            - Athena: diagrams.aws.analytics.Athena
            - Elasticsearch: diagrams.aws.analytics.ElasticsearchService, ES
            - EMRCluster: diagrams.aws.analytics.EMRCluster
            - EMR: diagrams.aws.analytics.EMR
            - Glue: diagrams.aws.analytics.Glue
            - Kinesis: diagrams.aws.analytics.Kinesis
            - Redshift: diagrams.aws.analytics.Redshift
            ** AR:**
            - Sumerian: diagrams.aws.ar.Sumerian
            - ArVr: diagrams.aws.ar.ArVr
            **Compute:**
            - EC2: diagrams.aws.compute.EC2
            - Lambda: diagrams.aws.compute.Lambda
            - ECS: diagrams.aws.compute.ElasticContainerService
            - EKS: diagrams.aws.compute.ElasticKubernetesService
            - Fargate: diagrams.aws.compute.Fargate

            **Storage:**
            - S3: diagrams.aws.storage.S3
            - EBS: diagrams.aws.storage.ElasticBlockStoreEBS
            - EFS: diagrams.aws.storage.ElasticFileSystemEFS

            **Database:**
            - RDS: diagrams.aws.database.RDS
            - Dynamodb: diagrams.aws.database.Dynamodb

            - DB: diagrams.aws.database.Database, DB
            - Redshift: diagrams.aws.database.Redshift
            - Neptune: diagrams.aws.database.Neptune
            - TimeStream: diagrams.aws.database.Timestream

            **Networking:**
            - VPC: diagrams.aws.network.VPC
            - Route53: diagrams.aws.network.Route53
            - ELB: diagrams.aws.network.ElasticLoadBalancing
            - InternetGateway: diagrams.aws.network.InternetGateway
            - NATGateway: diagrams.aws.network.NATGateway
            - TransitGateway: diagrams.aws.network.TransitGateway

            **Security:**
            - IAM: diagrams.aws.security.IdentityAndAccessManagementIam
            - WAF: diagrams.aws.security.WAF
            - SecurityHub: diagrams.aws.security.SecurityHub
            - KMS: diagrams.aws.security.KeyManagementService

            **Analytics:**
            - Glue: diagrams.aws.analytics.Glue
            - EMR: diagrams.aws.analytics.EMR
            - Athena: diagrams.aws.analytics.Athena
            - Kinesis: diagrams.aws.analytics.Kinesis

            **Machine Learning:**
            - Sagemaker: diagrams.aws.ml.Sagemaker


            **Integration:**
            - StepFunctions: diagrams.aws.integration.StepFunctions
            - SQS: diagrams.aws.integration.SimpleQueueServiceSqs
            - SNS: diagrams.aws.integration.SimpleNotificationServiceSns

            **Migration:**
            - DMS: diagrams.aws.migration.DatabaseMigrationService
            - Snowball: diagrams.aws.migration.Snowball
            - Snowmobile: diagrams.aws.migration.Snowmobile
            - TransferForSFTP: diagrams.aws.migration.TransferForSftp
            - CloudEndureMigration: diagrams.aws.migration.CloudendureMigration
            - MigrationHub: diagrams.aws.migration.MigrationHub

            **General (Fallback Services):**
            - General: diagrams.aws.general.General
            - User: diagrams.aws.general.User
            - Users: diagrams.aws.general.Users
            """
        )
        full_prompt = f"{system_prompt}\n\nArchitecture description: {prompt}"
        input_data = [full_prompt]
        if image and os.path.isfile(image):
            try:
                with open(image, 'rb') as file:
                    image_bytes = file.read()
                input_data.append(image_bytes)
            except Exception as e:
                return f"Error reading image file: {str(e)}"
        else:
            return "Error: Invalid image file path."

        try:
            metadata,generated_code = self.llm_engine(input_data)
            result_or_error = self.execute_code_snippet(generated_code)
            return metadata,result_or_error
        except Exception as e:
            print(e, e)
            return {"error": str(e)}
        
