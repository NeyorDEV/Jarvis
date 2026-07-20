// ── Référence partagée vers la socket WebSocket active ──────────────────────
// main.ts la réassigne à chaque (re)connexion. Les modules extraits l'utilisent
// via wsRef.current pour toujours viser la socket courante.
export const wsRef: { current: WebSocket | null } = { current: null };
