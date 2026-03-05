#!/bin/bash

echo "Testing AI Q&A Platform..."

# Test backend health
echo -e "\n1. Testing backend connectivity..."
curl -s http://localhost:8080/docs > /dev/null
if [ $? -eq 0 ]; then
    echo "✓ Backend is running"
else
    echo "✗ Backend is not accessible"
    exit 1
fi

# Test Q&A endpoint
echo -e "\n2. Testing Q&A endpoint..."
response=$(curl -s -X POST http://localhost:8080/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is 2+2?"}')

if [ $? -eq 0 ]; then
    echo "✓ Q&A endpoint responded"
    echo "Response: $response"
else
    echo "✗ Q&A endpoint failed"
    exit 1
fi

echo -e "\n✓ All tests passed!"
