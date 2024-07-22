import json
import jsonlines
from datetime import datetime
import os

def convert_json_to_jsonl_audio_qa(input_json, output_jsonl):
    # Get the base name of the input file to use as the file_name
    file_name = os.path.basename(input_json)
    
    with open(input_json, 'r') as json_file:
        data = json.load(json_file)
    
    with jsonlines.open(output_jsonl, mode='w') as writer:
        for result in data['results']:
            # Extract primary transcript and metadata
            primary_alternative = result['alternatives'][0] if result['alternatives'] else {}
            transcript = primary_alternative.get('transcript', '')
            language_code = result.get('languageCode', '')
            result_end_time = result.get('resultEndTime', '')
            
            # Extract word details
            words = primary_alternative.get('words', [])
            word_count = len(words)
            
            # Calculate duration
            if words:
                start_time = float(words[0]['startTime'].rstrip('s'))
                end_time = float(words[-1]['endTime'].rstrip('s'))
                duration = end_time - start_time
            else:
                duration = 0
            
            # Create structured metadata
            metadata = {
                "language": language_code,
                "duration_seconds": round(duration, 2),
                "word_count": word_count,
                "timestamp": datetime.utcnow().isoformat(),
                "file_name": file_name  # Now using the dynamic file name
            }
            
            # Create the entry
            entry = {
                "metadata": metadata,
                "transcript": transcript,
                "word_details": [
                    {
                        "word": word['word'],
                        "start_time": word['startTime'],
                        "end_time": word['endTime'],
                        "confidence": word['confidence']
                    } for word in words
                ],
                "raw_data": data  # Include the full raw data for the entire file
            }
            
            writer.write(entry)

# Usage
input_json = 'input.json'
output_jsonl = 'output_audio_qa.jsonl'
convert_json_to_jsonl_audio_qa(input_json, output_jsonl)