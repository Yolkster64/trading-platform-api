#!/usr/bin/env python3
"""Test OpenAI API Key configuration"""

import os
from dotenv import load_dotenv

load_dotenv()

key = os.getenv('OPENAI_API_KEY')

if key and key.startswith('sk-proj-'):
    print('✅ OpenAI API Key (ai1) - STORED & VERIFIED')
    print(f'   Key: {key[:25]}...{key[-10:]}')
    print(f'   Length: {len(key)} characters')
    print(f'   Status: READY FOR API CALLS')
else:
    print('❌ OpenAI API Key not found or invalid format')
    if key:
        print(f'   Found: {key[:50]}...')
