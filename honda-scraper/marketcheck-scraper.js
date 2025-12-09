const https = require('https');
const fs = require('fs');

const API_KEY = 'INSERT_KEY';
const BASE_URL = 'https://api.marketcheck.com/v2';

// Helper function to make API requests
function makeRequest(url) {
  return new Promise((resolve, reject) => {
    https.get(url, (res) => {
      let data = '';
      res.on('data', (chunk) => { data += chunk; });
      res.on('end', () => {
        try {
          resolve(JSON.parse(data));
        } catch (e) {
          reject(e);
        }
      });
    }).on('error', reject);
  });
}

// Fetch recent listings for a specific make/model/year/state
async function fetchRecentListings(make, model, year, state, limit = 100) {
  const url = `${BASE_URL}/search/car/recents?api_key=${API_KEY}&make=${make}&model=${model}&year=${year}&state=${state}&limit=${limit}`;
  console.log(`Fetching recent listings for ${year} ${make} ${model} in ${state}...`);
  return await makeRequest(url);
}

// Fetch VIN history for a specific vehicle
async function fetchVINHistory(vin) {
  const url = `${BASE_URL}/history/car/${vin}?api_key=${API_KEY}`;
  console.log(`Fetching history for VIN ${vin}...`);
  await new Promise(resolve => setTimeout(resolve, 200)); // Rate limiting
  return await makeRequest(url);
}

// Main function
async function main() {
  const searchParams = {
    make: 'Honda',
    model: 'Accord',
    year: 2021,
    states: ['NJ', 'PA']
  };

  let allListings = [];
  let allHistory = [];

  // Fetch listings from each state
  for (const state of searchParams.states) {
    try {
      const data = await fetchRecentListings(
        searchParams.make,
        searchParams.model,
        searchParams.year,
        state
      );

      console.log(`Found ${data.num_found} listings in ${state}`);

      if (data.listings && data.listings.length > 0) {
        allListings = allListings.concat(data.listings);
      }
    } catch (error) {
      console.error(`Error fetching listings for ${state}:`, error.message);
    }
  }

  console.log(`\nTotal listings found: ${allListings.length}`);

  // Save listings
  fs.writeFileSync(
    'marketcheck-listings.json',
    JSON.stringify(allListings, null, 2)
  );
  console.log('Saved listings to marketcheck-listings.json');

  // Fetch history for each VIN
  const uniqueVINs = [...new Set(allListings.map(l => l.vin))];
  console.log(`\nFetching history for ${uniqueVINs.length} unique VINs...`);

  let processed = 0;
  for (const vin of uniqueVINs) {
    try {
      const history = await fetchVINHistory(vin);
      if (history && history.length > 0) {
        allHistory.push({
          vin: vin,
          history: history
        });
      }
      processed++;
      if (processed % 10 === 0) {
        console.log(`Processed ${processed}/${uniqueVINs.length} VINs`);
      }
    } catch (error) {
      console.error(`Error fetching history for VIN ${vin}:`, error.message);
    }
  }

  // Save history
  fs.writeFileSync(
    'marketcheck-history.json',
    JSON.stringify(allHistory, null, 2)
  );
  console.log(`\nSaved history for ${allHistory.length} vehicles to marketcheck-history.json`);

  // Generate CSV summary
  const csvRows = [];
  csvRows.push('VIN,Make,Model,Year,Trim,Current_Price,Current_Miles,First_Seen,Last_Seen,Price_History_Count,Lowest_Price,Highest_Price');

  for (const vehicle of allHistory) {
    const currentListing = allListings.find(l => l.vin === vehicle.vin);
    if (!currentListing) continue;

    const prices = vehicle.history.map(h => h.price).filter(p => p > 0);
    const lowestPrice = prices.length > 0 ? Math.min(...prices) : 'N/A';
    const highestPrice = prices.length > 0 ? Math.max(...prices) : 'N/A';

    const firstSeen = vehicle.history.length > 0
      ? new Date(vehicle.history[vehicle.history.length - 1].first_seen_at * 1000).toISOString().split('T')[0]
      : 'N/A';

    const lastSeen = vehicle.history.length > 0
      ? new Date(vehicle.history[0].last_seen_at * 1000).toISOString().split('T')[0]
      : 'N/A';

    csvRows.push([
      vehicle.vin,
      currentListing.build?.make || 'N/A',
      currentListing.build?.model || 'N/A',
      currentListing.build?.year || 'N/A',
      currentListing.build?.trim || 'N/A',
      currentListing.price || 'N/A',
      currentListing.miles || 'N/A',
      firstSeen,
      lastSeen,
      vehicle.history.length,
      lowestPrice,
      highestPrice
    ].join(','));
  }

  fs.writeFileSync('marketcheck-summary.csv', csvRows.join('\n'));
  console.log('Saved summary to marketcheck-summary.csv');
}

main().catch(console.error);
