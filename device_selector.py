import streamlit.components.v1 as components

def device_selector():
    """
    Create a device selector component
    """
    device_selector_html = """
    <div style="margin: 10px 0; padding: 15px; border: 1px solid #ddd; border-radius: 8px; background: #f9f9f9;">
        <h4>🎙️ Microphone Selection</h4>
        <button onclick="loadMicrophones()" style="background: #4CAF50; color: white; padding: 8px 16px; border: none; border-radius: 4px; cursor: pointer; margin-bottom: 10px;">
            🔄 Load Available Microphones
        </button>
        <select id="micSelect" style="width: 100%; padding: 8px; margin: 5px 0; border: 1px solid #ccc; border-radius: 4px;" disabled>
            <option value="">Click "Load Available Microphones" first</option>
        </select>
        <div id="deviceInfo" style="margin-top: 10px; font-size: 14px;"></div>
    </div>

    <script>
        let availableMicrophones = [];
        let selectedDeviceInfo = null;

        // Load available microphones
        async function loadMicrophones() {
            const deviceInfo = document.getElementById('deviceInfo');
            const micSelect = document.getElementById('micSelect');
            
            try {
                deviceInfo.innerHTML = '<div style="color: #0066cc;">Loading microphones...</div>';
                
                // Request permission first to get device labels
                const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                stream.getTracks().forEach(track => track.stop()); // Stop immediately
                
                // Get all devices
                const devices = await navigator.mediaDevices.enumerateDevices();
                
                // Filter for audio input devices
                availableMicrophones = devices.filter(device => device.kind === 'audioinput');
                
                if (availableMicrophones.length === 0) {
                    deviceInfo.innerHTML = '<div style="color: #cc0000;">No microphones found!</div>';
                    return;
                }
                
                // Populate dropdown
                micSelect.innerHTML = '<option value="">Select a microphone...</option>';
                
                availableMicrophones.forEach((device, index) => {
                    const option = document.createElement('option');
                    option.value = device.deviceId;
                    option.textContent = device.label || `Microphone ${index + 1}`;
                    micSelect.appendChild(option);
                });
                
                micSelect.disabled = false;
                micSelect.addEventListener('change', onMicrophoneSelect);
                
                deviceInfo.innerHTML = `<div style="color: #006600;">✅ Found ${availableMicrophones.length} microphone(s). Select one above.</div>`;
                
            } catch (error) {
                console.error('Error loading microphones:', error);
                deviceInfo.innerHTML = `<div style="color: #cc0000;">Error: ${error.message}</div>`;
            }
        }

        // Handle microphone selection
        function onMicrophoneSelect() {
            const micSelect = document.getElementById('micSelect');
            const deviceInfo = document.getElementById('deviceInfo');
            const selectedDeviceId = micSelect.value;
            
            if (selectedDeviceId) {
                const selectedDevice = availableMicrophones.find(device => device.deviceId === selectedDeviceId);
                const selectedLabel = micSelect.options[micSelect.selectedIndex].text;
                
                selectedDeviceInfo = {
                    deviceId: selectedDeviceId,
                    label: selectedLabel
                };
                
                deviceInfo.innerHTML = `<div style="color: #006600;">🎤 Selected: <strong>${selectedLabel}</strong></div>`;
                
                // Store in session storage for the audio recorder to potentially use
                sessionStorage.setItem('selectedMicrophoneId', selectedDeviceId);
                sessionStorage.setItem('selectedMicrophoneLabel', selectedLabel);
                
            } else {
                deviceInfo.innerHTML = '<div style="color: #666666;">Please select a microphone.</div>';
                sessionStorage.removeItem('selectedMicrophoneId');
                sessionStorage.removeItem('selectedMicrophoneLabel');
            }
        }

        // Listen for device changes
        navigator.mediaDevices?.addEventListener('devicechange', () => {
            const deviceInfo = document.getElementById('deviceInfo');
            if (deviceInfo.innerHTML.includes('Found')) {
                deviceInfo.innerHTML += '<br><div style="color: #0066cc;">💡 Audio devices changed. Consider reloading.</div>';
            }
        });
    </script>
    """
    components.html(device_selector_html, height=250)