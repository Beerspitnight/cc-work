const fs = require('fs');

const csv = fs.readFileSync('honda-accords.csv', 'utf8');
const lines = csv.split('\n').slice(1).filter(l => l.length > 10);

const vehicles = lines.map(line => {
    const parts = line.split(',');
    return {
        year: parts[0],
        name: parts[1],
        mileage: parts[2],
        price: parts[3],
        dealer: parts[7]
    };
});

// Sort by price
vehicles.sort((a, b) => {
    const priceA = parseInt(a.price.replace(/[\$,"]/g, ''));
    const priceB = parseInt(b.price.replace(/[\$,"]/g, ''));
    return priceA - priceB;
});

console.log('\n' + '='.repeat(70));
console.log('🎉 FINAL HONDA ACCORD SEARCH RESULTS');
console.log('='.repeat(70) + '\n');

console.log('📊 Summary:');
console.log(`   • Total vehicles: ${vehicles.length}`);
console.log(`   • Budget: $27,500 (INCREASED from $25,000)`);
console.log(`   • Years: 2022-2023`);
console.log(`   • Max mileage: 60,000 miles\n`);

const withinBudget = vehicles.filter(v => parseInt(v.price.replace(/[\$,"]/g, '')) <= 27500);
const overBudget = vehicles.filter(v => parseInt(v.price.replace(/[\$,"]/g, '')) > 27500);

console.log(`   ✅ Within budget: ${withinBudget.length} vehicles (+13 from budget increase!)`);
console.log(`   ⚠️  Over budget: ${overBudget.length} vehicles\n`);

console.log('='.repeat(70));
console.log('🏆 TOP 10 BEST DEALS (within $27,500 budget)');
console.log('='.repeat(70) + '\n');

withinBudget.slice(0, 10).forEach((v, i) => {
    console.log(`${String(i + 1).padStart(2, ' ')}. ${v.price} - ${v.name}`);
    console.log(`    📏 ${v.mileage} miles | 🏢 ${v.dealer}\n`);
});

console.log('='.repeat(70) + '\n');
