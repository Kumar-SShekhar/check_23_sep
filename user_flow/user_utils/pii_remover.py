import boto3
import os
from dotenv import load_dotenv
load_dotenv()

comprehend = boto3.client(
        'comprehend',
        region_name=os.getenv("AWS_DEFAULT_REGION"),
        aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        aws_session_token = os.getenv("AWS_SESSION_TOKEN")
)

def detect_and_mask_pii(text, language_code='en'):
    response = comprehend.detect_pii_entities(
        Text=text,
        LanguageCode=language_code
    )
    pii_entities = response.get('Entities', [])
    
    masked_text = list(text)
    pii_removed = "N"  # Default to "N" (no PII removed)
    
    for entity in pii_entities:
        if entity['Type'] == "ADDRESS" or entity['Type'] == "DATE_TIME":
            continue
        else:
            begin_offset = entity['BeginOffset']
            end_offset = entity['EndOffset']
            
            # Mark PII removal flag as "Y"
            pii_removed = "Y"
            
            # Mask the text
            for i in range(begin_offset, end_offset):
                masked_text[i] = '#'
    
    masked_text = ''.join(masked_text)
    
    return {
        "masked_text": masked_text,
        "pii_removed": pii_removed
    }

# # Example usage:
# if __name__ == "__main__":
#     # Input text containing PII
#     text = "What is the primary goal of the Climate Change (Emissions Reduction Targets) (Scotland) Act 2019, and how does it affect the carbon footprint of businesses like GreenTech Solutions, located in Aberdeen?"
    
#     # Detect and mask PII in the text
#     masked_text = detect_and_mask_pii(text)
    
#     # Print the masked text
#     print("Original Text:", text)
#     print("Masked Text:", masked_text)