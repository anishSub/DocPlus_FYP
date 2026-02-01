// WebRTC Video Call Implementation
// This is a basic implementation using SimpleWebRTC concept
// For production, you'd use a signaling server (Django Channels WebSocket)

let localStream = null;
let remoteStream = null;
let peerConnection = null;
let isMuted = false;
let isVideoOff = false;
let callStartTime = null;
let timerInterval = null;

// Get DOM elements
const localVideo = document.getElementById('local-video');
const remoteVideo = document.getElementById('remote-video');
const toggleMicBtn = document.getElementById('toggle-mic');
const toggleVideoBtn = document.getElementById('toggle-video');
const toggleChatBtn = document.getElementById('toggle-chat');
const endCallBtn = document.getElementById('end-call');
const chatSidebar = document.getElementById('chat-sidebar');
const closeChatBtn = document.getElementById('close-chat');
const callStatus = document.querySelector('.call-status');

// Initialize on page load
document.addEventListener('DOMContentLoaded', init);

async function init() {
    try {
        // Request camera and microphone access
        localStream = await navigator.mediaDevices.getUserMedia({
            video: true,
            audio: true
        });

        // Display local video
        localVideo.srcObject = localStream;

        // Update status
        callStatus.textContent = 'Ready to call';
        callStatus.style.color = '#10b981';

        // Start call timer
        startTimer();

        // Setup event listeners
        setupEventListeners();

        // For demo: Auto-mirror local video to remote
        // In production, this would connect to the other party via WebRTC
        simulateRemoteVideo();

    } catch (error) {
        console.error('Error accessing media devices:', error);
        callStatus.textContent = 'Camera/Mic access denied';
        callStatus.style.color = '#ef4444';
        alert('Please allow camera and microphone access to join the video call.');
    }
}

function setupEventListeners() {
    toggleMicBtn.addEventListener('click', toggleMicrophone);
    toggleVideoBtn.addEventListener('click', toggleVideo);
    toggleChatBtn.addEventListener('click', () => chatSidebar.classList.toggle('active'));
    closeChatBtn.addEventListener('click', () => chatSidebar.classList.remove('active'));
    endCallBtn.addEventListener('click', endCall);
}

function toggleMicrophone() {
    if (localStream) {
        const audioTrack = localStream.getAudioTracks()[0];
        if (audioTrack) {
            audioTrack.enabled = !audioTrack.enabled;
            isMuted = !audioTrack.enabled;

            toggleMicBtn.classList.toggle('muted', isMuted);
            toggleMicBtn.querySelector('i').className = isMuted ?
                'fas fa-microphone-slash' : 'fas fa-microphone';
        }
    }
}

function toggleVideo() {
    if (localStream) {
        const videoTrack = localStream.getVideoTracks()[0];
        if (videoTrack) {
            videoTrack.enabled = !videoTrack.enabled;
            isVideoOff = !videoTrack.enabled;

            toggleVideoBtn.classList.toggle('muted', isVideoOff);
            toggleVideoBtn.querySelector('i').className = isVideoOff ?
                'fas fa-video-slash' : 'fas fa-video';
        }
    }
}

function startTimer() {
    callStartTime = Date.now();
    const timerElement = document.getElementById('call-timer');

    timerInterval = setInterval(() => {
        const elapsed = Math.floor((Date.now() - callStartTime) / 1000);
        const minutes = Math.floor(elapsed / 60);
        const seconds = elapsed % 60;
        timerElement.textContent =
            `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
    }, 1000);
}

function endCall() {
    // Stop all tracks
    if (localStream) {
        localStream.getTracks().forEach(track => track.stop());
    }

    // Clear timer
    if (timerInterval) {
        clearInterval(timerInterval);
    }

    // Redirect back
    if (confirm('Are you sure you want to end the call?')) {
        window.location.href = '/';
    }
}

// Demo function: Simulate remote video by mirroring local
// In production, this would be replaced with actual WebRTC peer connection
function simulateRemoteVideo() {
    // For demo purposes, we'll show the local stream in the remote video too
    // This simulates what a real 2-person call would look like
    remoteVideo.srcObject = localStream;
    callStatus.textContent = 'Connected';
}

// Production WebRTC Functions (for future implementation with Django Channels)
/*
function createPeerConnection() {
    const configuration = {
        iceServers: [
            { urls: 'stun:stun.l.google.com:19302' }
        ]
    };
    
    peerConnection = new RTCPeerConnection(configuration);
    
    // Add local stream tracks
    localStream.getTracks().forEach(track => {
        peerConnection.addTrack(track, localStream);
    });
    
    // Handle remote stream
    peerConnection.ontrack = (event) => {
        remoteStream = event.streams[0];
        remoteVideo.srcObject = remoteStream;
        callStatus.textContent = 'Connected';
    };
    
    // Handle ICE candidates
    peerConnection.onicecandidate = (event) => {
        if (event.candidate) {
            // Send to signaling server (WebSocket)
            sendToSignalingServer({
                type: 'ice-candidate',
                candidate: event.candidate
            });
        }
    };
}

function sendToSignalingServer(data) {
    // WebSocket implementation
    // ws.send(JSON.stringify(data));
}
*/


// ============================================================================
// REAL-TIME CHAT FUNCTIONALITY WITH WEBSOCKET
// ============================================================================

let chatSocket = null;
let appointmentId = null;
let userRole = null;
let userName = null;

// Initialize chat when page loads
document.addEventListener('DOMContentLoaded', function () {
    initializeChat();
});

function initializeChat() {
    // Get call data from hidden div
    const callData = document.getElementById('call-data');
    appointmentId = callData.dataset.appointmentId;
    userRole = callData.dataset.userRole;
    userName = callData.dataset.userName;

    // Establish WebSocket connection
    connectChatWebSocket();

    // Setup chat UI event listeners
    setupChatListeners();
}

function connectChatWebSocket() {
    // Determine WebSocket protocol (ws or wss)
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/chat/${appointmentId}/`;

    console.log('Connecting to chat WebSocket:', wsUrl);

    chatSocket = new WebSocket(wsUrl);

    chatSocket.onopen = function (e) {
        console.log('✅ Chat WebSocket connected');
        updateChatStatus('Connected', 'success');
    };

    chatSocket.onmessage = function (e) {
        const data = JSON.parse(e.data);
        handleChatMessage(data);
    };

    chatSocket.onerror = function (e) {
        console.error('❌ Chat WebSocket error:', e);
        updateChatStatus('Connection error', 'error');
    };

    chatSocket.onclose = function (e) {
        console.log('🔌 Chat WebSocket closed. Attempting to reconnect...');
        updateChatStatus('Disconnected', 'warning');

        // Attempt to reconnect after 3 seconds
        setTimeout(() => {
            connectChatWebSocket();
        }, 3000);
    };
}

function handleChatMessage(data) {
    if (data.type === 'chat_history') {
        // Load previous messages
        data.messages.forEach(msg => {
            displayChatMessage(msg.message, msg.sender_type, msg.sender_name, msg.timestamp);
        });
        scrollChatToBottom();
    } else if (data.type === 'new_message') {
        // Display new real-time message
        displayChatMessage(data.message, data.sender_type, data.sender_name, data.timestamp);
        scrollChatToBottom();
    }
}

function displayChatMessage(message, senderType, senderName, timestamp) {
    const chatMessages = document.getElementById('chat-messages');
    const messageDiv = document.createElement('div');

    // Determine if this message is from the current user
    const isOwnMessage = senderType === userRole;

    messageDiv.className = `chat-message ${isOwnMessage ? 'own-message' : 'other-message'}`;

    messageDiv.innerHTML = `
        <div class="message-header">
            <span class="sender-name">${isOwnMessage ? 'You' : senderName}</span>
            <span class="message-time">${formatTime(timestamp)}</span>
        </div>
        <div class="message-content">${escapeHtml(message)}</div>
    `;

    chatMessages.appendChild(messageDiv);
}

function setupChatListeners() {
    const chatInput = document.getElementById('chat-input');
    const sendBtn = document.getElementById('send-btn');

    // Send message on button click
    sendBtn.addEventListener('click', sendChatMessage);

    // Send message on Enter key
    chatInput.addEventListener('keypress', function (e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendChatMessage();
        }
    });
}

function sendChatMessage() {
    const chatInput = document.getElementById('chat-input');
    const message = chatInput.value.trim();

    if (message && chatSocket && chatSocket.readyState === WebSocket.OPEN) {
        // Send via WebSocket
        chatSocket.send(JSON.stringify({
            'message': message,
            'sender_type': userRole,
            'sender_name': userName
        }));

        // Clear input
        chatInput.value = '';
        chatInput.focus();
    } else if (!chatSocket || chatSocket.readyState !== WebSocket.OPEN) {
        alert('Chat is not connected. Please wait...');
    }
}

function scrollChatToBottom() {
    const chatMessages = document.getElementById('chat-messages');
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function updateChatStatus(status, type) {
    // You can add a status indicator in the chat header if needed
    console.log(`Chat status: ${status} (${type})`);
}

function formatTime(timestamp) {
    const date = new Date(timestamp);
    const hours = date.getHours();
    const minutes = date.getMinutes();
    const ampm = hours >= 12 ? 'PM' : 'AM';
    const displayHours = hours % 12 || 12;

    return `${displayHours}:${minutes.toString().padStart(2, '0')} ${ampm}`;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Clean up WebSocket when page unloads
window.addEventListener('beforeunload', function () {
    if (chatSocket) {
        chatSocket.close();
    }
});
