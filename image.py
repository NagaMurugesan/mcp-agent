from InlineAgent.agent import InlineAgent
from InlineAgent.action_group import ActionGroup
import boto3
import base64
import json
import os
import random

import asyncio

# Step 1: Define tools with Docstring
def get_current_weather(location: str, state: str, unit: str = "fahrenheit") -> dict:
    """
    Get the current weather in a given location.

    Parameters:
        location: The city, e.g., San Francisco
        state: The state eg CA
        unit: The unit to use, e.g., fahrenheit or celsius. Defaults to "fahrenheit"
    """
    return "Weather is 70 fahrenheit"

# Image Generation
def generate_image(prompt: str, width: int = 512, height: int = 512) -> str:
    """
    Generates an image from a text prompt using a Bedrock multimodal model.

    Parameters:
        prompt (str): The text prompt describing the image to generate.
        width (int, optional): The width of the generated image in pixels. Default is 512.
        height (int, optional): The height of the generated image in pixels. Default is 512.

    Returns:
        str: Base64 encoded string of the generated image.
    """
    seed = random.randint(0, 858993460)

    native_request = {
        "taskType": "TEXT_IMAGE",
        "textToImageParams": {"text": prompt},
        "imageGenerationConfig": {
            "seed": seed,
            "quality": "standard",
            "height": 1024,
            "width": 1024,
            "numberOfImages": 1,
            "cfgScale":9.5,
        },
    }

    request = json.dumps(native_request)

    REGION = "us-east-1"
    bedrock = boto3.client(service_name='bedrock-runtime', region_name=REGION)

    response = bedrock.invoke_model(modelId="amazon.titan-image-generator-v2:0", body=request)


    # Decode the response body.
    model_response = json.loads(response["body"].read())

    # Extract the image data.
    base64_image_data = model_response["images"][0]
    image_data = base64.b64decode(base64_image_data)

    image_path = os.path.join("/home/ec2-user/img/", "nova_canvas.png")
    with open(image_path, "wb") as file:
        file.write(image_data)

    return image_path



# # Step 2: Logically group tools together
# weather_action_group = ActionGroup(
#     name="WeatherActionGroup",
#     description="This is action group to get weather",
#     tools=[get_current_weather],
# )

# # Step 3: Define agent 
# agent = InlineAgent(
#     foundation_model="amazon.nova-canvas-v1:0",
#     instruction="You are a friendly assistant that is responsible for getting the current weather.",
#     action_groups=[weather_action_group],
#     agent_name="MockAgent",
# )
input_text="Create a professional bar chart titled \"Top Customers by Revenue - Q3 2025\" showing two bars for customer revenue in Q3 2025. The bars should show Charlie Davis with $36,114 and Alice Johnson with $24,162. Use distinct colors for each bar with the customer name clearly labeled below each bar and the revenue amount displayed above each bar. Include a y-axis with dollar amounts and grid lines for better readability. Use a clean business visualization style."

# seed = random.randint(0, 858993460)

# native_request = {
#     "taskType": "TEXT_IMAGE",
#     "textToImageParams": {"text": input_text},
#     "imageGenerationConfig": {
#         "seed": seed,
#         "quality": "standard",
#         "height": 512,
#         "width": 512,
#         "numberOfImages": 1,
#     },
# }

# request = json.dumps(native_request)

# REGION = "us-east-1"
# bedrock = boto3.client(service_name='bedrock-runtime', region_name=REGION)

# response = bedrock.invoke_model(modelId="amazon.nova-canvas-v1:0", body=request)
# print(response)

# # Decode the response body.
# model_response = json.loads(response["body"].read())

# # Extract the image data.
# base64_image_data = model_response["images"][0]

# print(base64_image_data)

img=generate_image(input_text,600,600)
print(img)


