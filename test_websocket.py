
"""
WebSocket Test Client
Tests the WebSocket functionality of the VoxAura application
"""
import socketio
import time
import json

# Create a Socket.IO client
sio = socketio.Client()

@sio.event
def connect():
    print('✅ Connected to VoxAura WebSocket server')

@sio.event
def disconnect():
    print('❌ Disconnected from VoxAura WebSocket server')

@sio.event
def status(data):
    print(f'📊 Server Status: {data}')

@sio.event
def echo_response(data):
    print(f'🔄 Echo Response: {json.dumps(data, indent=2)}')

@sio.event
def chat_response(data):
    print(f'💬 Chat Response: {json.dumps(data, indent=2)}')

@sio.event
def audio_processed(data):
    print(f'🎵 Audio Processed: {json.dumps(data, indent=2)}')

def test_websocket():
    try:
        # Connect to the server
        print('🔗 Connecting to WebSocket server...')
        sio.connect('http://127.0.0.1:5000')
        
        # Wait a moment for connection
        time.sleep(1)
        
        # Test 1: Send a simple message
        print('\n📤 Test 1: Sending simple message...')
        sio.emit('message', 'Hello from test client!')
        time.sleep(2)
        
        # Test 2: Send a chat message
        print('\n📤 Test 2: Sending chat message...')
        sio.emit('chat_message', {
            'message': 'How are you today?',
            'session_id': 'test_session_123'
        })
        time.sleep(2)
        
        # Test 3: Send audio stream event
        print('\n📤 Test 3: Sending audio stream event...')
        sio.emit('audio_stream', {
            'audio_data': 'fake_audio_data_for_testing',
            'format': 'webm'
        })
        time.sleep(2)
        
        print('\n✅ All tests completed successfully!')
        
    except Exception as e:
        print(f'❌ Error during testing: {e}')
    
    finally:
        # Disconnect
        print('\n🔌 Disconnecting...')
        sio.disconnect()

if __name__ == '__main__':
    print('🧪 VoxAura WebSocket Test Client')
    print('=' * 40)
    print('Make sure the VoxAura server is running on localhost:5000')
    print('Starting tests in 3 seconds...\n')
    
    time.sleep(3)
    test_websocket()
    
    time.sleep(3)
    test_websocket()
