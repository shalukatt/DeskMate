const sprite = document.getElementById('sprite');
const bubble = document.getElementById('speech-bubble');

// Map each emotion to a sprite file. Add more as you add more sprites later.
const EMOTION_SPRITES = {
  happy: '../assets/happy.png',
  excited: '../assets/excited.png',
  scolding: '../assets/approve.png', // placeholder until you add a proper "scolding" sprite
  sleepy: '../assets/idle.png',      // placeholder until you add a proper "sleepy" sprite
  neutral: '../assets/idle.png',
  curious: '../assets/happy.png',    // placeholder - LLM sometimes invents emotions outside our list
};

let bubbleTimeout = null;

function showReply(reply) {
  if (!reply || reply.skipped || !reply.text) {
    return; // cooldown-skipped events have no text, nothing to show
  }

  // Update sprite (fall back to idle if the emotion isn't mapped)
  sprite.src = EMOTION_SPRITES[reply.emotion] || '../assets/idle.png';

  // Show the speech bubble
  bubble.textContent = reply.text;
  bubble.style.display = 'block';

  // Hide it again after a few seconds, and return to idle sprite
  if (bubbleTimeout) clearTimeout(bubbleTimeout);
  bubbleTimeout = setTimeout(() => {
    bubble.style.display = 'none';
    sprite.src = '../assets/idle.png';
  }, 6000);
}

function connect() {
  const ws = new WebSocket('ws://127.0.0.1:8000/ws');

  ws.onopen = () => {
    console.log('[WS] Connected to server');
  };

  ws.onmessage = (event) => {
    try {
      const reply = JSON.parse(event.data);
      console.log('[WS] Received:', reply);
      showReply(reply);
    } catch (e) {
      console.error('[WS] Failed to parse message', e);
    }
  };

  ws.onclose = () => {
    console.log('[WS] Disconnected, retrying in 3s...');
    setTimeout(connect, 3000);
  };

  ws.onerror = (err) => {
    console.error('[WS] Error', err);
    ws.close();
  };
}

connect();