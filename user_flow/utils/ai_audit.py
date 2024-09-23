import os
from datetime import datetime
import csv

def append_token_usage(project_name, prompt_token, completion_token, total_token, model_name="Claude 3 Sonnet"):
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    project_name = project_name
    model_name = model_name
    prompt_token_cost = (prompt_token / 1000) * 0.003
    completion_token_cost = (completion_token / 1000) * 0.015
    total_token_cost = prompt_token_cost + completion_token_cost
    
    new_data = [current_time, project_name, model_name, prompt_token, completion_token, total_token,
                prompt_token_cost, completion_token_cost, total_token_cost]
    
    file_path = './token_usage.csv'
    file_exists = os.path.isfile(file_path)

    with open(file_path, 'a', newline='') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(['Date and Time', 'Project Name', 'LLM Model', 'Prompt Token', 'Completion Token',
                             'Total Token Usage', 'Prompt Token Cost (in USD)', 'Completion Token Cost (in USD)', 'Total Token Cost (in USD)'])
        writer.writerow(new_data)