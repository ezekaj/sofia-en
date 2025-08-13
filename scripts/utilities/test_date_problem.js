// Test für das Datumsproblem

console.log("=== Test Datumsproblem ===");
console.log("Heute:", new Date());

// Teste verschiedene Datumsformate
const tomorrow = new Date();
tomorrow.setDate(tomorrow.getDate() + 1);
console.log("Morgen (korrekt):", tomorrow);

// Teste ISO-Format
const tomorrowISO = tomorrow.toISOString().split('T')[0];
console.log("Morgen ISO:", tomorrowISO);

// Teste die formatDate Funktion aus server.js
function formatDate(dateString) {
  const date = new Date(dateString);
  const options = { 
    weekday: 'long', 
    year: 'numeric', 
    month: 'long', 
    day: 'numeric' 
  };
  return date.toLocaleDateString('de-DE', options);
}

console.log("\n=== Test formatDate ===");
console.log("formatDate(tomorrowISO):", formatDate(tomorrowISO));
console.log("formatDate mit new Date(tomorrowISO):", new Date(tomorrowISO));

// Teste problematische Formate
console.log("\n=== Teste verschiedene Datumsformate ===");
const testDates = [
    "2025-08-05",  // ISO
    "2025-05-08",  // Könnte als 8. Mai interpretiert werden
    "05-08-2025",  // US-Format
    "08-05-2025",  // EU-Format?
];

testDates.forEach(dateStr => {
    console.log(`\nInput: "${dateStr}"`);
    console.log("new Date():", new Date(dateStr));
    console.log("formatDate():", formatDate(dateStr));
});

// Teste Zeitzonenprobleme
console.log("\n=== Zeitzonentest ===");
console.log("Zeitzone:", Intl.DateTimeFormat().resolvedOptions().timeZone);
console.log("UTC Offset:", new Date().getTimezoneOffset());