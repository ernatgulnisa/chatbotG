#!/bin/bash
# Initialize bot templates on Render with automatic test data creation

cd /opt/render/project/src/backend

echo "============================================================"
echo "  Render.com Bot Templates Initialization"
echo "============================================================"
echo ""

# Set default environment variables if not set
export WHATSAPP_PHONE_NUMBER="${WHATSAPP_PHONE_NUMBER:-+1234567890}"
export WHATSAPP_PHONE_NUMBER_ID="${WHATSAPP_PHONE_NUMBER_ID:-demo_phone_id}"

echo "🔧 Configuration:"
echo "   WhatsApp Phone: $WHATSAPP_PHONE_NUMBER"
echo "   Phone Number ID: $WHATSAPP_PHONE_NUMBER_ID"
echo ""

echo "🤖 Initializing bot templates..."
python3 init_bot_templates.py

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Bot templates initialized successfully!"
    echo ""
    echo "📋 Test credentials:"
    echo "   Email: admin@chatbot.com"
    echo "   Password: admin123"
    echo ""
else
    echo ""
    echo "❌ Failed to initialize bot templates"
    exit 1
fi
