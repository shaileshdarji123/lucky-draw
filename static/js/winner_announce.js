// Winner Announcement Animation Script (Lottie Edition)
// Requires: Lottie-web (CDN loaded in dashboard.html)

function animateWinnerReveal(winnerName, department) {
    // Remove any existing overlay
    const old = document.getElementById('winner-overlay');
    if (old) old.remove();

    const overlay = document.createElement('div');
    overlay.id = 'winner-overlay';
    overlay.innerHTML = `
      <div class="winner-lottie-center">
        <div id="lottie-winner-animation" style="width:420px; height:420px; margin:auto;"></div>
        <div class="winner-lottie-labels">
          <div id="winner-label" class="winner-label">${winnerName}</div>
          <div id="winner-dept-label" class="winner-dept-label">${department}</div>
        </div>
      </div>
      <audio id="winner-audio" src="https://cdn.pixabay.com/audio/2022/07/26/audio_124bfae5e2.mp3" preload="auto"></audio>
    `;
    document.body.appendChild(overlay);

    // Play sound
    setTimeout(() => {
      const audio = document.getElementById('winner-audio');
      if (audio) audio.play().catch(()=>{});
    }, 400);

    // Load Lottie animation
    lottie.loadAnimation({
      container: document.getElementById('lottie-winner-animation'),
      renderer: 'svg',
      loop: false,
      autoplay: true,
      path: '/static/lottie/win_result_1.json' // Place your Lottie JSON here
    });

    // Animate winner name and department fade in
    setTimeout(() => {
      const label = document.getElementById('winner-label');
      const dept = document.getElementById('winner-dept-label');
      label.style.opacity = 0;
      dept.style.opacity = 0;
      label.style.transform = 'translateY(40px) scale(0.8)';
      dept.style.transform = 'translateY(40px) scale(0.8)';
      setTimeout(() => {
        label.style.transition = 'all 0.7s cubic-bezier(.68,-0.55,.27,1.55)';
        dept.style.transition = 'all 0.7s cubic-bezier(.68,-0.55,.27,1.55)';
        label.style.opacity = 1;
        dept.style.opacity = 1;
        label.style.transform = 'translateY(0) scale(1)';
        dept.style.transform = 'translateY(0) scale(1)';
      }, 200);
    }, 1200);

    // Remove overlay on click or after 8s
    overlay.addEventListener('click', function() {
      overlay.remove();
    });
    setTimeout(() => { overlay.remove(); }, 8000);
}

// Lottie Winner Animation CSS
(function(){
  if(document.getElementById('winner-announce-style')) return;
  const style = document.createElement('style');
  style.id = 'winner-announce-style';
  style.innerHTML = `
  #winner-overlay {
    position: fixed; top:0; left:0; width:100vw; height:100vh;
    background: linear-gradient(120deg, #181c2a 0%, #232946 50%, #181c2a 100%);
    background-size: 200% 200%;
    animation: winner-bg-move 14s ease-in-out infinite;
    backdrop-filter: blur(4px);
    z-index: 9999; display: flex; align-items: center; justify-content: center;
    overflow: hidden; cursor: pointer;
    transition: background 0.5s;
  }
  @keyframes winner-bg-move {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
  }
  .winner-lottie-center {
    position: relative; z-index: 2; display: flex; flex-direction: column; align-items: center;
  }
  .winner-lottie-labels {
    position: absolute; left: 0; top: 0; width: 420px; height: 420px; display: flex; flex-direction: column; align-items: center; justify-content: center; pointer-events: none;
  }
  .winner-label {
    font-size: 2.8rem;
    color: #f7f3e9;
    font-family: 'Pacifico', 'Brush Script MT', cursive, Arial, sans-serif;
    font-weight: 400;
    letter-spacing: 0.04em;
    background: none;
    text-shadow: 0 2px 6px #b8860b;
    filter: none;
    margin-bottom: 0.5rem;
    opacity: 0;
    border-radius: 0;
    padding: 0.2em 0.6em;
    transition: color 0.5s;
  }
  .winner-dept-label {
    font-size: 1.2rem;
    color: #fffbe6;
    font-family: 'Pacifico', 'Brush Script MT', cursive, Arial, sans-serif;
    font-weight: 400;
    letter-spacing: 0.03em;
    background: none;
    text-shadow: 0 0 4px #b8860b;
    opacity: 0;
    border-radius: 0;
    padding: 0.1em 0.4em;
    transition: color 0.5s;
  }
  @media (max-width: 600px) {
    .winner-lottie-center #lottie-winner-animation { width: 220px !important; height: 220px !important; }
    .winner-lottie-labels { width: 220px !important; height: 220px !important; }
  }
  `;
  document.head.appendChild(style);
})();
