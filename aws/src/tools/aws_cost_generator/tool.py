import os
from octotools.tools.base import BaseTool
from src.engine.gateway import GatewayEngine
from dotenv import load_dotenv
load_dotenv()



class AWS_Cost_Generator_Tool(BaseTool):
    require_llm_engine = True

    def __init__(self, model_string="gpt-4o-mini"):
        super().__init__(
            tool_name="AWS_Cost_Generator_Tool",
            tool_description="A tool that calculates the average, minimum, and maximum cost for AWS services used in an architecture diagram.",
            tool_version="1.0.0",
            input_types={"image": "str - The path to the image file.",
                         "prompt": "str - A text description of the AWS architecture.",},
            output_type = "str - Text output of cost analysis.",
            demo_commands = [
                {
                    "command": 'execution = tool.execute(image="path/to/image.png", '
                            'prompt="AWS architecture with Lambda, S3, and RDS")',
                    "description": "Calculates average, minimum, and maximum cost for AWS services used in the architecture.",
                }
            ],
        )
        self.model_string=model_string



    def execute(self, image, prompt):
        print(f"\nCalculating AWS Costs for: {prompt}")


        system_prompt = (
            """

                **You are an expert in AWS cost analysis**, specializing in estimating costs for AWS services based on an architecture diagram.

                Your goal is to **extract AWS services from the given input** and provide cost estimates including:

                - **Average Cost**
                - **Minimum Cost**
                - **Maximum Cost**
                - **Assumptions used per cost tier (Min, Avg, Max)**

                ---

                ## 🔍 Key Requirements:

                ### AWS Services Identification
                - Extract AWS services from the **architecture description**.
                - List the services used and their **corresponding pricing models**.
                - Assume all AWS services are running in the **us-east-1** region.

                ---

                ## 📊 Assumptions for Cost Calculation:

                Each pricing tier has its own assumptions, and these will be outlined separately **after** the cost table.

                ---

                ## 📋 Output Format:

                ### Cost Table:

                | Service Name | Min Cost (USD) | Avg Cost (USD) | Max Cost (USD) | Pricing Model |
                |--------------|----------------|----------------|----------------|----------------|

                - Use pay-as-you-go pricing unless the description implies reserved or spot instances.
                - Reflect free-tier impact when applicable.
                - Use standard service pricing in `us-east-1`.

                ---

                ### 💰 Total Estimated Monthly Cost:

                - **Total Min Cost**: \$XXX.XX
                - **Total Avg Cost**: \$XXX.XX
                - **Total Max Cost**: \$XXX.XX

                ---

                ## 📌 Assumptions Used:

                ### For Min Cost:
                - **Compute**: 10,000 Lambda invocations or 50 EC2 instance hours/month
                - **Storage**: 100 GB (e.g., S3, EBS)
                - **Database**: 20 GB + 50,000 requests/month
                - **Data Transfer**: 1 TB/month
                - **Analytics/ML**:
                - **AWS Glue**: 10 ETL jobs processing 10 GB each
                - **Amazon Athena**: 10 queries scanning 100 GB each
                - **Amazon EMR**: 10 hours on a 3-node (m5.xlarge) cluster
                - **Amazon SageMaker**: 10 training hours on ml.m5.large

                ### For Avg Cost:
                - **Compute**: 100,000 Lambda invocations or 200 EC2 instance hours/month
                - **Storage**: 500 GB
                - **Database**: 100 GB + 500,000 requests/month
                - **Data Transfer**: 10 TB/month
                - **Analytics/ML**:
                - **AWS Glue**: 50 ETL jobs processing 10 GB each
                - **Amazon Athena**: 50 queries scanning 100 GB each
                - **Amazon EMR**: 50 hours on a 3-node (m5.xlarge) cluster
                - **Amazon SageMaker**: 50 training hours on ml.m5.large

                ### For Max Cost:
                - **Compute**: 500,000 Lambda invocations or 750 EC2 instance hours/month
                - **Storage**: 2 TB
                - **Database**: 500 GB + 2 million requests/month
                - **Data Transfer**: 30 TB/month
                - **Analytics/ML**:
                - **AWS Glue**: 200 ETL jobs processing 10 GB each
                - **Amazon Athena**: 200 queries scanning 100 GB each
                - **Amazon EMR**: 200 hours on a 3-node (m5.xlarge) cluster
                - **Amazon SageMaker**: 200 training hours on ml.m5.large


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
            llm_engine=GatewayEngine(model_string=self.model_string)
            metadata,generated_text = llm_engine(input_data)
            return metadata,generated_text
        except Exception as e:
            print(e, e)
            return {"error": str(e)}
        