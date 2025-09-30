#!/bin/bash

# Create a test submission
curl -X POST http://localhost:8002/api/v1/sessions/test_session/submit \
  -H "Content-Type: application/json" \
  -d '{
    "responses": [
      {"item_id": "1", "response": 5},
      {"item_id": "2", "response": 3},
      {"item_id": "3", "response": 4},
      {"item_id": "4", "response": 2},
      {"item_id": "5", "response": 5},
      {"item_id": "6", "response": 3},
      {"item_id": "7", "response": 4},
      {"item_id": "8", "response": 2},
      {"item_id": "9", "response": 5},
      {"item_id": "10", "response": 3},
      {"item_id": "11", "response": 4},
      {"item_id": "12", "response": 2},
      {"item_id": "13", "response": 5},
      {"item_id": "14", "response": 3},
      {"item_id": "15", "response": 4},
      {"item_id": "16", "response": 2},
      {"item_id": "17", "response": 5},
      {"item_id": "18", "response": 3},
      {"item_id": "19", "response": 4},
      {"item_id": "20", "response": 2}
    ],
    "completion_time": 120
  }' | python3 -m json.tool
