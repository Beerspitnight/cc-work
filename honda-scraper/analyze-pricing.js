const fs = require('fs');

// Read the data
const listings = JSON.parse(fs.readFileSync('marketcheck-listings.json', 'utf8'));

// Filter and analyze 2021 Honda Accords
const accords = listings.filter(l =>
  l.build &&
  l.build.year === 2021 &&
  l.build.make === 'Honda' &&
  l.build.model === 'Accord' &&
  l.price && l.miles
);

// Sort by mileage
accords.sort((a, b) => a.miles - b.miles);

console.log('\n=== 2021 HONDA ACCORD PRICING ANALYSIS ===\n');

// Group by trim
const byTrim = {};
accords.forEach(car => {
  const trim = car.build.trim || 'Unknown';
  if (!byTrim[trim]) byTrim[trim] = [];
  byTrim[trim].push(car);
});

// Calculate price per mile depreciation
console.log('VEHICLES CLOSEST TO 85,000 MILES:\n');
const target = 85000;
const closest = accords
  .map(car => ({
    ...car,
    diff: Math.abs(car.miles - target)
  }))
  .sort((a, b) => a.diff - b.diff)
  .slice(0, 10);

closest.forEach((car, i) => {
  const pricePerMile = (car.price / car.miles).toFixed(2);
  console.log(`${i + 1}. ${car.build.trim} - ${car.miles.toLocaleString()} miles - $${car.price.toLocaleString()}`);
  console.log(`   Price/Mile: $${pricePerMile} | Location: ${car.dealer.city}, ${car.dealer.state}`);
  console.log(`   Dealer: ${car.dealer.name}`);
  console.log('');
});

// Calculate statistics for vehicles 70k-100k miles
console.log('\n=== VEHICLES WITH 70,000 - 100,000 MILES ===\n');
const similar = accords.filter(car => car.miles >= 70000 && car.miles <= 100000);

if (similar.length > 0) {
  const prices = similar.map(c => c.price);
  const avg = prices.reduce((a, b) => a + b, 0) / prices.length;
  const min = Math.min(...prices);
  const max = Math.max(...prices);
  const median = prices.sort((a, b) => a - b)[Math.floor(prices.length / 2)];

  console.log(`Sample Size: ${similar.length} vehicles`);
  console.log(`Average Price: $${avg.toFixed(0).toLocaleString()}`);
  console.log(`Median Price: $${median.toLocaleString()}`);
  console.log(`Price Range: $${min.toLocaleString()} - $${max.toLocaleString()}`);
  console.log('');

  // Break down by trim
  console.log('BY TRIM LEVEL:');
  const trimStats = {};
  similar.forEach(car => {
    const trim = car.build.trim;
    if (!trimStats[trim]) trimStats[trim] = [];
    trimStats[trim].push(car.price);
  });

  Object.entries(trimStats).forEach(([trim, prices]) => {
    const avg = prices.reduce((a, b) => a + b, 0) / prices.length;
    const min = Math.min(...prices);
    const max = Math.max(...prices);
    console.log(`  ${trim}: $${avg.toFixed(0).toLocaleString()} avg (${prices.length} vehicles) [$${min.toLocaleString()} - $${max.toLocaleString()}]`);
  });
}

// Estimate for 85,000 miles
console.log('\n=== PRICING ESTIMATE FOR 85,000 MILES ===\n');

// Calculate depreciation rate
const sortedByMiles = accords.filter(c => c.miles >= 40000).sort((a, b) => a.miles - b.miles);
if (sortedByMiles.length >= 2) {
  const low = sortedByMiles[0];
  const high = sortedByMiles[sortedByMiles.length - 1];
  const depreciationPerMile = (high.price - low.price) / (high.miles - low.miles);

  console.log(`Depreciation analysis:`);
  console.log(`  ${low.miles.toLocaleString()} miles: $${low.price.toLocaleString()}`);
  console.log(`  ${high.miles.toLocaleString()} miles: $${high.price.toLocaleString()}`);
  console.log(`  Rate: $${Math.abs(depreciationPerMile).toFixed(2)} per mile`);
  console.log('');
}

// Recommended pricing
if (similar.length > 0) {
  const prices = similar.map(c => c.price);
  const median = prices.sort((a, b) => a - b)[Math.floor(prices.length / 2)];
  const low = median * 0.90;
  const high = median * 1.05;

  console.log('RECOMMENDED NEGOTIATION RANGE:');
  console.log(`  Target Price: $${(median * 0.95).toFixed(0).toLocaleString()} (5% below median)`);
  console.log(`  Acceptable Range: $${low.toFixed(0).toLocaleString()} - $${high.toFixed(0).toLocaleString()}`);
  console.log(`  Walk-Away Price: $${high.toFixed(0).toLocaleString()}`);
  console.log('');
  console.log('NEGOTIATION STRATEGY:');
  console.log(`  Opening Offer: $${(median * 0.88).toFixed(0).toLocaleString()} (12% below median)`);
  console.log(`  Counter Offer: $${(median * 0.92).toFixed(0).toLocaleString()} (8% below median)`);
  console.log(`  Final Offer: $${(median * 0.95).toFixed(0).toLocaleString()} (5% below median)`);
}

console.log('\n');
