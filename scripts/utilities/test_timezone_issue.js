// Test für Zeitzonenprobleme mit toISOString()

console.log("=== Zeitzonentest für Sofia-Datumsproblem ===\n");

// Aktuelles Datum in lokaler Zeit
const now = new Date();
console.log("Lokale Zeit:", now);
console.log("ISO String:", now.toISOString());
console.log("ISO Date:", now.toISOString().split('T')[0]);

// Morgen in lokaler Zeit
const tomorrow = new Date();
tomorrow.setDate(tomorrow.getDate() + 1);
console.log("\nMorgen lokal:", tomorrow);
console.log("Morgen ISO:", tomorrow.toISOString());
console.log("Morgen ISO Date:", tomorrow.toISOString().split('T')[0]);

// Das Problem: toISOString() gibt UTC zurück!
console.log("\n=== Problem Demonstration ===");
const problemDate = new Date(2025, 7, 5); // 5. August 2025 (Monat ist 0-basiert, also 7 = August)
console.log("Lokales Datum (5. August):", problemDate);
console.log("ISO String:", problemDate.toISOString());
console.log("ISO Date Teil:", problemDate.toISOString().split('T')[0]);

// Wenn es kurz vor Mitternacht ist
const lateEvening = new Date(2025, 7, 4, 23, 30); // 4. August 23:30
console.log("\n4. August 23:30 lokal:", lateEvening);
console.log("ISO String (UTC):", lateEvening.toISOString());
console.log("ISO Date Teil:", lateEvening.toISOString().split('T')[0], "← Zeigt 5. August!");

// Lösung: Lokales Datum formatieren
function getLocalDateString(date) {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
}

console.log("\n=== Lösung: Lokale Formatierung ===");
console.log("Lokales Datum Format:", getLocalDateString(tomorrow));
console.log("Vergleich:");
console.log("- toISOString():", tomorrow.toISOString().split('T')[0]);
console.log("- Lokal formatiert:", getLocalDateString(tomorrow));