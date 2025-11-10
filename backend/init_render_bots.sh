#!/bin/bash
# Initialize bot templates on Render

cd /opt/render/project/src/backend

echo "Initializing bot templates..."
python init_bot_templates.py

echo "Done!"
