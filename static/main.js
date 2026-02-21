/* static/main.js */

const video          = document.getElementById('video');
const processedImage = document.getElementById('processed_image');
const endFeedBtn     = document.getElementById('endFeedBtn');
const threatBanner   = document.getElementById('threatBanner');

let intervalId;
let processingEnded = false;

// --- Start webcam ---
navigator.mediaDevices
    .getUserMedia({ video: { width: 480, height: 360 } })
    .then(stream => { video.srcObject = stream; })
    .catch(err => console.error('Camera error:', err));

// --- Send frames to backend ---
function sendFrame() {
    if (video.videoWidth === 0) return; // not ready yet
    const canvas = document.createElement('canvas');
    canvas.width  = video.videoWidth;
    canvas.height = video.videoHeight;
    canvas.getContext('2d').drawImage(video, 0, 0);

    fetch('/upload', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ image: canvas.toDataURL('image/jpeg', 0.6) })
    })
    .then(r => r.json())
    .then(data => {
        if (processingEnded) return;
        processedImage.src = data.image;

        // Update threat banner
        if (data.threat && data.threat.loitering_detected) {
            threatBanner.classList.remove('hidden');
        } else {
            threatBanner.classList.add('hidden');
        }
    })
    .catch(err => console.warn('Upload error:', err));
}

intervalId = setInterval(sendFrame, 250);

// --- End feed ---
endFeedBtn.addEventListener('click', () => {
    processingEnded = true;
    clearInterval(intervalId);
    video.srcObject?.getTracks().forEach(t => t.stop());
    threatBanner.classList.add('hidden');

    endFeedBtn.style.display = 'none';
    document.getElementById('cameraBox').style.display = 'none';
    document.getElementById('processedBox').querySelector('h2').innerText = 'Final Motion Heatmap';

    fetch('/end_feed', { method: 'POST' })
        .then(r => r.json())
        .then(data => { processedImage.src = data.heatmap_image; })
        .catch(err => console.error('End feed error:', err));
});

// Blur effect on hover
endFeedBtn.addEventListener('mouseover', () => document.body.classList.add('is-blurred'));
endFeedBtn.addEventListener('mouseout',  () => document.body.classList.remove('is-blurred'));
