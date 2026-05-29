let socket = null;

function connect() {
  socket = new WebSocket("ws://localhost:8765");

  socket.onopen = () => {
    console.log("[JARVIS EXTENSION] Connecté au serveur local ws://localhost:8765");
  };

  socket.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      // Si on reçoit une action DOM de JARVIS
      if (data.type === "dom_action" || data.action === "dom_sequence") {
        // Envoyer la commande à tous les onglets actifs (pour éviter les problèmes de focus de fenêtre)
        chrome.tabs.query({ active: true }, (tabs) => {
          tabs.forEach(tab => {
            chrome.tabs.sendMessage(tab.id, data);
          });
        });
      }
    } catch (e) {
      // Ignorer les messages non-JSON
    }
  };

  socket.onclose = () => {
    console.log("[JARVIS EXTENSION] Déconnecté. Tentative de reconnexion dans 3s...");
    setTimeout(connect, 3000);
  };

  socket.onerror = (err) => {
    socket.close();
  };
}

// Lancer la connexion au démarrage de l'extension
connect();
