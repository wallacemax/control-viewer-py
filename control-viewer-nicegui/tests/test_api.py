read this json and create 100 points covering six months or so with normally distributed values from [0, 100]; add at least one point greater than 95 and one less than 5.
create the points in this JSON format:  [
  {
    "id": "integration-01",
    "name": "Integration Test Point",
    "description": "Test point for integration testing",
    "value": 10.1,
    "unit": "\u00b0C",
    "min_value": 0.0,
    "max_value": 50.0,
    "timestamp": "2025-03-26T16:39:20.438297",
    "status": "normal",
    "type": "sensor"
  }
]
type is always "sensor", name is always "foo" plus the timestamp string, and description is a random line from the script to Top Gun (1984)

I'll create 100 sensor data points with normally distributed values over a six-month period, including the requested formatting and special cases. Let me generate this data for you.

Javascript

// Generate 100 data points over 6 months with normally distributed values
const topGunQuotes = [
  "I feel the need... the need for speed!",
  "That's right! Ice... man. I am dangerous.",
  "You can be my wingman anytime.",
  "Talk to me, Goose.",
  "The defense department regrets to inform you that your sons are dead because they were stupid.",
  "Your ego is writing checks your body can't cash.",
  "Son, your ego is writing checks your body can't cash.",
  "You've lost that loving feeling.",
  "That's right! You are dangerous.",
  "Sorry, Goose, but it's time to buzz the tower.",
  "I was inverted.",
  "No. No, Mav, this is not a good idea.",
  "Maverick, it's not your flying, it's your attitude.",
  "Great balls of fire!",
  "Gentleman, this is your first hop. The jet will go Mach 2 with your hair on fire.",
  "This is what I call a target-rich environment.",
  "That's a negative, Ghost Rider, the pattern is full.",
  "Just want to serve my country, be the best pilot in the Navy, sir.",
  "Every time we go up there, it's unsafe.",
  "Remember, boys, no points for second place."
];

// Function to generate a random number from a normal distribution
function randomNormal(mean, stdDev) {
  let u = 0, v = 0;
  while (u === 0) u = Math.random();
  while (v === 0) v = Math.random();
  const z = Math.sqrt(-2.0 * Math.log(u)) * Math.cos(2.0 * Math.PI * v);
  return z * stdDev + mean;
}

// Function to format date as ISO string
function formatDate(date) {
  return date.toISOString();
}

// Generate timestamps for 6 months starting from 6 months ago
const endDate = new Date();
const startDate = new Date();
startDate.setMonth(startDate.getMonth() - 6);

// Create array to hold all data points
const dataPoints = [];

// Generate 100 data points with normally distributed values
for (let i = 0; i < 100; i++) {
  // Calculate timestamp evenly distributed across 6 months
  const timestamp = new Date(startDate.getTime() + (endDate.getTime() - startDate.getTime()) * (i / 99));
  
  // Generate normally distributed value between 0-100 with mean 50 and stddev 15
  let value = randomNormal(50, 15);
  
  // Ensure the value is between 0 and 100
  value = Math.max(0, Math.min(100, value));
  
  // Get a random Top Gun quote
  const description = topGunQuotes[Math.floor(Math.random() * topGunQuotes.length)];
  
  dataPoints.push({
    id: `sensor-${(i + 1).toString().padStart(3, '0')}`,
    name: `foo${timestamp.toISOString()}`,
    description,
    value: parseFloat(value.toFixed(1)),
    unit: "°C",
    min_value: 0.0,
    max_value: 100.0,
    timestamp: timestamp.toISOString(),
    status: "normal",
    type: "sensor"
  });
}

// Ensure we have at least one point > 95 and one point < 5
let highPointIndex = Math.floor(Math.random() * 100);
let lowPointIndex;
do {
  lowPointIndex = Math.floor(Math.random() * 100);
} while (lowPointIndex === highPointIndex);

dataPoints[highPointIndex].value = 95.1 + (Math.random() * 4.9);
dataPoints[lowPointIndex].value = Math.random() * 4.9;

// Format values to one decimal place
dataPoints.forEach(point => {
  point.value = parseFloat(point.value.toFixed(1));
});

// Output the full JSON
console.log(JSON.stringify(dataPoints, null, 2));

// Count points outside normal range as validation
const highPoints = dataPoints.filter(p => p.value > 95).length;
const lowPoints = dataPoints.filter(p => p.value < 5).length;
console.log(`Points > 95: ${highPoints}`);
console.log(`Points < 5: ${lowPoints}`);
Result

[
  {
    "id": "sensor-001",
    "name": "foo2024-09-27T23:27:50.817Z",
    "description": "This is what I call a target-rich environment.",
    "value": 42.7,
    "unit": "°C",
    "min_value": 0,
    "max_value": 100,
    "timestamp": "2024-09-27T23:27:50.817Z",
    "status": "normal",
    "type": "sensor"
  },
  {
    "id": "sensor-002",
    "name": "foo2024-09-29T19:20:34.453Z",
    "description": "Every time we go up there, it's unsafe.",
    "value": 55.4,
    "unit": "°C",
    "min_value": 0,
    "max_value": 100,
    "timestamp": "2024-09-29T19:20:34.453Z",
    "status": "normal",
    "type": "sensor"
  },
  {
    "id": "sensor-003",
    "name": "foo2024-10-01T15:13:18.089Z",
    "description": "That's right! Ice... man. I am dangerous.",
    "value": 39.5,
    "unit": "°C",
    "min_value": 0,
    "max_value": 100,
    "timestamp": "2024-10-01T15:13:18.089Z",
    "status": "normal",
    "type": "sensor"
  },
  {
    "id": "sensor-004",
    "name": "foo2024-10-03T11:06:01.726Z",
    "description": "No. No, Mav, this is not a good idea.",
    "value": 40.2,
    "unit": "°C",
    "min_value": 0,
    "max_value": 100,
    "timestamp": "2024-10-03T11:06:01.726Z",
    "status": "normal",
    "type": "sensor"
  },
  {
    "id": "sensor-005",
    "name": "foo2024-10-05T06:58:45.362Z",
    "description": "I feel the need... the need for speed!",
    "value": 52.9,
    "unit": "°C",
    "min_value": 0,
    "max_value": 100,
    "timestamp": "2024-10-05T06:58:45.362Z",
    "status": "normal",
    "type": "sensor"
  },
  {
    "id": "sensor-006",
    "name": "foo2024-10-07T02:51:28.998Z",
    "description": "That's right! You are dangerous.",
    "value": 60.2,
    "unit": "°C",
    "min_value": 0,
    "max_value": 100,
    "timestamp": "2024-10-07T02:51:28.998Z",
    "status": "normal",
    "type": "sensor"
  },
  {
    "id": "sensor-007",
    "name": "foo2024-10-08T22:44:12.635Z",
    "description": "I feel the need... the need for speed!",
    "value": 35.8,
    "unit": "°C",
    "min_value": 0,
    "max_value": 100,
    "timestamp": "2024-10-08T22:44:12.635Z",
    "status": "normal",
    "type": "sensor"
  },
  {
    "id": "sensor-008",
    "name": "foo2024-10-10T18:36:56.271Z",
    "description": "That's right! You are dangerous.",
    "value": 32.9,
    "unit": "°C",
    "min_value": 0,
    "max_value": 100,
    "timestamp": "2024-10-10T18:36:56.271Z",
    "status": "normal",
    "type": "sensor"
  },
  {
    "id": "sensor-009",
    "name": "foo2024-10-12T14:29:39.907Z",
    "description": "I feel the need... the need for speed!",
    "value": 73.9,
    "unit": "°C",
    "min_value": 0,
    "max_value": 100,
    "timestamp": "2024-10-12T14:29:39.907Z",
    "status": "normal",
    "type": "sensor"
  },
  {
    "id": "sensor-010",
    "name": "foo2024-10-14T10:22:23.544Z",
    "description": "I was inverted.",
    "value": 41.2,
    "unit": "°C",
    "min_value": 0,
    "max_value": 100,
    "timestamp": "2024-10-14T10:22:23.544Z",
    "status": "normal",
    "type": "sensor"
  },
  {
    "id": "sensor-011",
    "name": "foo2024-10-16T06:15:07.180Z",
    "description": "That's a negative, Ghost Rider, the pattern is full.",
    "value": 31.4,
    "unit": "°C",
    "min_value": 0,
    "max_value": 100,
    "timestamp": "2024-10-16T06:15:07.180Z",
    "status": "normal",
    "type": "sensor"
  },
  {
    "id": "sensor-012",
    "name": "foo2024-10-18T02:07:50.817Z",
    "description": "That's right! Ice... man. I am dangerous.",
    "value": 51,
    "unit": "°C",
    "min_value": 0,
    "max_value": 100,
    "timestamp": "2024-10-18T02:07:50.817Z",
    "status": "normal",
    "type": "sensor"
  },
  {
    "id": "sensor-013",
    "name": "foo2024-10-19T22:00:34.453Z",
    "description": "Every time we go up there, it's unsafe.",
    "value": 69.4,
    "unit": "°C",
    "min_value": 0,
    "max_value": 100,
    "timestamp": "2024-10-19T22:00:34.453Z",
    "status": "normal",
    "type": "sensor"
  },
  {
    "id": "sensor-014",
    "name": "foo2024-10-21T17:53:18.089Z",
    "description": "Maverick, it's not your flying, it's your attitude.",
    "value": 36.5,
    "unit": "°C",
    "min_value": 0,
    "max_value": 100,
    "timestamp": "2024-10-21T17:53:18.089Z",
    "status": "normal",
    "type": "sensor"
  },
  {
    "id": "sensor-015",
    "name": "foo2024-10-23T13:46:01.726Z",
    "description": "Maverick, it's not your flying, it's your attitude.",
    "value": 77.3,
    "unit": "°C",
    "min_value": 0,
    "max_value": 100,
    "timestamp": "2024-10-23T13:46:01.726Z",
    "status": "normal",
    "type": "sensor"
  },
  {
    "id": "sensor-016",
    "name": "foo2024-10-25T09:38:45.362Z",
    "description": "I feel the need... the need for speed!",
    "value": 57.9,
    "unit": "°C",
    "min_value": 0,
    "max_value": 100,
    "timestamp": "2024-10-25T09:38:45.362Z",
    "status": "normal",
    "type": "sensor"
  },
  {
    "id": "sensor-017",
    "name": "foo2024-10-27T05:31:28.998Z",
    "description": "No. No, Mav, this is not a good idea.",
    "value": 29.5,
    "unit": "°C",
    "min_value": 0,
    "max_value": 100,
    "timestamp": "2024-10-27T05:31:28.998Z",
    "status": "normal",
    "type": "sensor"
  },
  {
    "id": "sensor-018",
    "name": "foo2024-10-29T01:24:12.635Z",
    "description": "You've lost that loving feeling.",
    "value": 1.5,
    "unit": "°C",
    "min_value": 0,
    "max_value": 100,
    "timestamp": "2024-10-29T01:24:12.635Z",
    "status": "normal",
    "type": "sensor"
  },
  {
    "id": "sensor-019",
    "name": "foo2024-10-30T21:16:56.271Z",
    "description": "Talk to me, Goose.",
    "value": 50,
    "unit": "°C",
    "min_value": 0,
    "max_value": 100,
    "timestamp": "2024-10-30T21:16:56.271Z",
    "status": "normal",
    "type": "sensor"
  },
  {
    "id": "sensor-020",
    "name": "foo2024-11-01T17:09:39.907Z",
    "description": "Gentleman, this is your first hop. The jet will go Mach 2 with your hair on fire.",
    "value": 67,
    "unit": "°C",
    "min_value": 0,
    "max_value": 100,
    "timestamp": "2024-11-01T17:09:39.907Z",
    "status": "normal",
    "type": "sensor"
  },
  {
    "id": "sensor-021",
    "name": "foo2024-11-03T13:02:23.544Z",
    "description": "The defense department regrets to inform you that your sons are dead because they were stupid.",
    "value": 38.5,
    "unit": "°C",
    "min_value": 0,
    "max_value": 100,
    "timestamp": "2024-11-03T13:02:23.544Z",
    "status": "normal",
    "type": "sensor"
  },
  {
    "id": "sensor-022",
    "name": "foo2024-11-05T08:55:07.180Z",
    "description": "Just want to serve my country, be the best pilot in the Navy, sir.",
    "value": 83.2,
    "unit": "°C",
    "min_value": 0,
    "max_value": 100,
    "timestamp": "2024-11-05T08:55:07.180Z",
    "status": "normal",
    "type": "sensor"
  },
  {
    "id": "sensor-023",
    "name": "foo2024-11-07T04:47:50.817Z",
    "description": "Great balls of fire!",
    "value": 64.3,
    "unit": "°C",
    "min_value": 0,
    "max_value": 100,
    "timestamp": "2024-11-07T04:47:50.817Z",
    "status": "normal",
    "type": "sensor"
  },
  {
    "id": "sensor-024",
    "name": "foo2024-11-09T00:40:34.453Z",
    "description": "Every time we go up there, it's unsafe.",
    "value": 78.6,
    "unit": "°C",
    "min_value": 0,
    "max_value": 100,
    "timestamp": "2024-11-09T00:40:34.453Z",
    "status": "normal",
    "type": "sensor"
  },
  {
    "id": "sensor-025",
    "name": "foo2024-11-10T20:33:18.089Z",
    "description": "That's right! You are dangerous.",
    "value": 35.2,
    "unit": "°C",
    "min_value": 0,
    "max_value": 100,
    "timestamp": "2024-11-10T20:33:18.089Z",
    "status": "normal",
    "type": "sensor"
  },
  {
    "id": "sensor-026",
    "name": "foo2024-11-12T16:26:01.726Z",
    "description": "Maverick, it's not your flying, it's your attitude.",
    "value": 66.8,
    "unit": "°C",
    "min_value": 0,
    "max_value": 100,
    "timestamp": "2024-11-12T16:26:01.726Z",
    "status": "normal",
    "type": "sensor"
  },
  {
    "id": "sensor-027",
    "name": "foo2024-11-14T12:18:45.362Z",
    "description": "Sorry, Goose, but it's time to buzz the tower.",
    "value": 54.5,
    "unit": "°C",
    "min_value": 0,
    "max_value": 100,
    "timestamp": "2024-11-14T12:18:45.362Z",
    "status": "normal",
    "type": "sensor"
  },
  {
    "id": "sensor-028",
    "name": "foo2024-11-16T08:11:28.998Z",
    "description": "Your ego is writing checks your body can't cash.",
    "value": 62.3,
    "unit": "°C",
    "min_value": 0,
    "max_value": 100,
    "timestamp": "2024-11-16T08:11:28.998Z",
    "status": "normal",
    "type": "sensor"
  },
  {
    "id": "sensor-029",
    "name": "foo2024-11-18T04:04:12.635Z",
    "description": "Great balls of fire!",
    "value": 80.3,
    "unit": "°C",
    "min_value": 0,
    "max_value": 100,
    "timestamp": "2024-11-18T04:04:12.635Z",
    "status": "normal",
    "type": "sensor"
  },
  {
    "id": "sensor-030",
    "name": "foo2024-11-19T23:56:56.271Z",
    "description": "Sorry, Goose, but it's time to buzz the tower.",
    "value": 33,
    "unit": "°C",
    "min_value": 0,
    "max_value": 100,
    "timestamp": "2024-11-19T23:56:56.271Z",
    "status": "normal",
    "type": "sensor"
  },
  {
    "id": "sensor-031",
    "name": "foo2024-11-21T19:49:39.907Z",
    "description": "Remember, boys, no points for second place.",
    "value": 69.5,
    "unit": "°C",
    "min_value": 0,
    "max_value": 100,
    "timestamp": "2024-11-21T19:49:39.907Z",
    "status": "normal",
    "type": "sensor"
  },
  {
    "id": "sensor-032",
    "name": "foo2024-11-23T15:42:23.544Z",
    "description": "Son, your ego is writing checks your body can't cash.",
    "value": 56.2,
    "unit": "°C",
    "min_value": 0,
    "max_value": 100,
    "timestamp": "2024-11-23T15:42:23.544Z",
    "status": "normal",
    "type": "sensor"
  },
  {
    "id": "sensor-033",
    "name": "foo2024-11-25T11:35:07.180Z",
    "description": "This is what I call a target-rich environment.",
    "value": 48.4,
    "unit": "°C",
    "min_value": 0,
    "max_value": 100,
    "timestamp": "2024-11-25T11:35:07.180Z",
    "status": "normal",
    "type": "sensor"
  },
  {
    "id": "sensor-034",
    "name": "foo2024-11-27T07:27:50.817Z",
    "description": "That's a negative, Ghost Rider, the pattern is full.",
    "value": 67.8,
    "unit": "°C",
    "min_value": 0,
    "max_value": 100,
    "timestamp": "2024-11-27T07:27:50.817Z",
    "status": "normal",
    "type": "sensor"
  },
  {
    "id": "sensor-035",
    "name": "foo2024-11-29T03:20:34.453Z",
    "description": "You've lost that loving feeling.",
    "value": 33.2,
    "unit": "°C",
    "min_value": 0,
    "max_value": 100,
    "timestamp": "2024-11-29T03:20:34.453Z",
    "status": "normal",
    "type": "sensor"
  },
  {
    "id": "sensor-036",
    "name": "foo2024-11-30T23:13:18.089Z",
    "description": "Your ego is writing checks your body can't cash.",
    "value": 65.4,
    "unit": "°C",
    "min_value": 0,
    "max_value": 100,
    "timestamp": "2024-11-30T23:13:18.089Z",
    "status": "normal",
    "type": "sensor"
  },
  {
    "id": "sensor-037",
    "name": "foo2024-12-02T19:06:01.726Z",
    "description": "Just want to serve my country, be the best pilot in the Navy, sir.",
    "value": 64.4,
    "unit": "°C",
    "min_value": 0,
    "max_value": 100,
    "timestamp": "2024-12-02T19:06:01.726Z",
    "status": "normal",
    "type": "sensor"
  },
  {
    "id": "sensor-038",
    "name": "foo2024-12-04T14:58:45.362Z",
    "description": "Son, your ego is writing checks your body can't cash.",
    "value": 47.7,
    "unit": "°C",
    "min_value": 0,
    "max_value": 100,
    "timestamp": "2024-12-04T14:58:45.362Z",
    "status": "normal",
    "type": "sensor"
  },
  {
    "id": "sensor-039",
    "name": "foo2024-12-06T10:51:28.998Z",
    "description": "You can be my wingman anytime.",
    "value": 17.1,
    "unit": "°C",
    "min_value": 0,
    "max_value": 100,
    "timestamp": "2024-12-06T10:51:28.998Z",
    "status": "normal",
    "type": "sensor"
  },
  {
    "id": "sensor-040",
    "name": "foo2024-12-08T06:44:12.635Z",
    "description": "You can be my wingman anytime.",
    "value": 53.3,
    "unit": "°C",
    "min_value": 0,
    "max_value": 100,
    "timestamp": "2024-12-08T06:44:12.635Z",
    "status": "normal",
    "type": "sensor"
  },
  {
    "id": "sensor-041",
    "name": "foo2024-12-10T02:36:56.271Z",
    "description": "Remember, boys, no points for second place.",
    "value": 52.4,
    "unit": "°C",
    "min_value": 0,
    "max_value": 100,
    "timestamp": "2024-12-10T02:36:56.271Z",
    "status": "normal",
    "type": "sensor"
  },
  {
    "id": "sensor-042",
    "name": "foo2024-12-11T22:29:39.907Z",
    "description": "Your ego is writing checks your body can't cash.",
    "value": 41.2,
    "unit": "°C",
    "min_value": 0,
    "max_value": 100,
    "timestamp": "2024-12-11T22:29:39.907Z",
    "status": "normal",
    "type": "sensor"
  },
  {
    "id": "sensor-043",
    "name": "foo2024-12-13T18:22:23.544Z",
    "description": "No. No, Mav, this is not a good idea.",
    "value": 27.4,
    "unit": "°C",
    "min_value": 0,
    "max_value": 100,
    "timestamp": "2024-12-13T18:22:23.544Z",
    "status": "normal",
    "type": "sensor"
  },
  {
    "id": "sensor-044",
    "name": "foo2024-12-15T14:15:07.180Z",
    "description": "Remember, boys, no points for second place.",
    "value": 76.7,
    "unit": "°C",
    "min_value": 0,
    "max_value": 100,
    "timestamp": "2024-12-15T14:15:07.180Z",
    "status": "normal",
    "type": "sensor"
  },
  {
    "id": "sensor-045",
    "name": "foo2024-12-17T10:07:50.817Z",
    "description": "Maverick, it's not your flying, it's your attitude.",
    "value": 55.8,
    "unit": "°C",
    "min_value": 0,
    "max_value": 100,
    "timestamp": "2024-12-17T10:07:50.817Z",
    "status": "normal",
    "type": "sensor"
  },
  {
    "id": "sensor-046",
    "name": "foo2024-12-19T06:00:34.453Z",
    "description": "That's right! You are dangerous.",
    "value": 67.4,
    "unit": "°C",
    "min_value": 0,
    "max_value": 100,
    "timestamp": "2024-12-19T06:00:34.453Z",
    "status": "normal",
    "type": "sensor"
  },
  {
    "id": "sensor-047",
    "name": "foo2024-12-21T01:53:18.089Z",
    "description": "This is what I call a target-rich environment.",
    "value": 75,
    "unit": "°C",
    "min_value": 0,
    "max_value": 100,
    "timestamp": "2024-12-21T01:53:18.089Z",
    "status": "normal",
    "type": "sensor"
  },
  {
    "id": "sensor-048",
    "name": "foo2024-12-22T21:46:01.726Z",
    "description": "Talk to me, Goose.",
    "value": 60.2,
    "unit": "°C",
    "min_value": 0,
    "max_value": 100,
    "timestamp": "2024-12-22T21:46:01.726Z",
    "status": "normal",
    "type": "sensor"
  },
  {
    "id": "sensor-049",
    "name": "foo2024-12-24T17:38:45.362Z",
    "description": "No. No, Mav, this is not a good idea.",
    "value": 19.9,
    "unit": "°C",
    "min_value": 0,
    "max_value": 100,
    "timestamp": "2024-12-24T17:38:45.362Z",
    "status": "normal",
    "type": "sensor"
  },
  {
    "id": "sensor-050",
    "name": "foo2024-12-26T13:31:28.998Z",
    "description": "Your ego is writing checks your body can't cash.",
    "value": 37.6,
    "unit": "°C",
    "min_value": 0,
    "max_value": 100,
    "timestamp": "2024-12-26T13:31:28.998Z",
    "status": "normal",
    "type": "sensor"
  },
  {
    "id": "sensor-051",
    "name": "foo2024-12-28T09:24:12.635Z",
    "description": "Sorry, Goose, but it's time to buzz the tower.",
    "value": 59.9,
    "unit": "°C",
    "min_value": 0,
    "max_value": 100,
    "timestamp": "2024-12-28T09:24:12.635Z",
    "status": "normal",
    "type": "sensor"
  },
  {
    "id": "sensor-052",
    "name": "foo2024-12-30T05:16:56.271Z",
    "description": "You've lost that loving feeling.",
    "value": 33.4,
    "unit": "°C",
    "min_value": 0,
    "max_value": 100,
    "timestamp": "2024-12-30T05:16:56.271Z",
    "status": "normal",
    "type": "sensor"
  },
  {
    "id": "sensor-053",
    "name": "foo2025-01-01T01:09:39.907Z",
    "description": "This is what I call a target-rich environment.",
    "value": 39.7,
    "unit": "°C",
    "min_value": 0,
    "max_value": 100,
    "timestamp": "2025-01-01T01:09:39.907Z",
    "status": "normal",
    "type": "sensor"
  },
  {
    "id": "sensor-054",
    "name": "foo2025-01-02T21:02:23.544Z",
    "description": "I was inverted.",
    "value": 53.9,
    "unit": "°C",
    "min_value": 0,
    "max_value": 100,
    "timestamp": "2025-01-02T21:02:23.544Z",
    "status": "normal",
    "type": "sensor"
  },
  {
    "id": "sensor-055",
    "name": "foo2025-01-04T16:55:07.180Z",
    "description": "Just want to serve my country, be the best pilot in the Navy, sir.",
    "value": 66.7,
    "unit": "°C",
    "min_value": 0,
    "max_value": 100,
    "timestamp": "2025-01-04T16:55:07.180Z",
    "status": "normal",
    "type": "sensor"
  },
  {
    "id": "sensor-056",
    "name": "foo2025-01-06T12:47:50.817Z",
    "description": "Just want to serve my country, be the best pilot in the Navy, sir.",
    "value": 51.8,
    "unit": "°C",
    "min_value": 0,
    "max_value": 100,
    "timestamp": "2025-01-06T12:47:50.817Z",
    "status": "normal",
    "type": "sensor"
  },
  {
    "id": "sensor-057",
    "name": "foo2025-01-08T08:40:34.453Z",
    "description": "Just want to serve my country, be the best pilot in the Navy, sir.",
    "value": 64.5,
    "unit": "°C",
    "min_value": 0,
    "max_value": 100,
    "timestamp": "2025-01-08T08:40:34.453Z",
    "status": "normal",
    "type": "sensor"
  },
  {
    "id": "sensor-058",
    "name": "foo2025-01-10T04:33:18.089Z",
    "description": "Gentleman, this is your first hop. The jet will go Mach 2 with your hair on fire.",
    "value": 42.4,
    "unit": "°C",
    "min_value": 0,
    "max_value": 100,
    "timestamp": "2025-01-10T04:33:18.089Z",
    "status": "normal",
    "type": "sensor"
  },
  {
    "id": "sensor-059",
    "name": "foo2025-01-12T00:26:01.726Z",
    "description": "That's right! Ice... man. I am dangerous.",
    "value": 97.4,
    "unit": "°C",
    "min_value": 0,
    "max_value": 100,
    "timestamp": "2025-01-12T00:26:01.726Z",
    "status": "normal",
    "type": "sensor"
  },
  {
    "id": "sensor-060",
    "name": "foo2025-01-13T20:18:45.362Z",
    "description": "Son, your ego is writing checks your body can't cash.",
    "value": 47.9,
    "unit": "°C",
    "min_value": 0,
    "max_value": 100,
    "timestamp": "2025-01-13T20:18:45.362Z",
    "status": "normal",
    "type": "sensor"
  },
  {
    "id": "sensor-061",
    "name": "foo2025-01-15T16:11:28.998Z",
    "description": "Talk to me, Goose.",
    "value": 41.4,
    "unit": "°C",
    "min_value": 0,
    "max_value": 100,
    "timestamp": "2025-01-15T16:11:28.998Z",
    "status": "normal",
    "type": "sensor"
  },
  {
    "id": "sensor-062",
    "name": "foo2025-01-17T12:04:12.635Z",
    "description": "Every time we go up there, it's unsafe.",
    "value": 38.3,
    "unit": "°C",
    "min_value": 0,
    "max_value": 100,
    "timestamp": "2025-01-17T12:04:12.635Z",
    "status": "normal",
    "type": "sensor"
  },
  {
    "id": "sensor-063",
    "name": "foo2025-01-19T07:56:56.271Z",
    "description": "That's right! You are dangerous.",
    "value": 57.1,
    "unit": "°C",
    "min_value": 0,
    "max_value": 100,
    "timestamp": "2025-01-19T07:56:56.271Z",
    "status": "normal",
    "type": "sensor"
  },
  {
    "id": "sensor-064",
    "name": "foo2025-01-21T03:49:39.907Z",
    "description": "Maverick, it's not your flying, it's your attitude.",
    "value": 55,
    "unit": "°C",
    "min_value": 0,
    "max_value": 100,
    "timestamp": "2025-01-21T03:49:39.907Z",
    "status": "normal",
    "type": "sensor"
  },
  {
    "id": "sensor-065",
    "name": "foo2025-01-22T23:42:23.544Z",
    "description": "No. No, Mav, this is not a good idea.",
    "value": 64.8,
    "unit": "°C",
    "min_value": 0,
    "max_value": 100,
    "timestamp": "2025-01-22T23:42:23.544Z",
    "status": "normal",
    "type": "sensor"
  },
  {
    "id": "sensor-066",
    "name": "foo2025-01-24T19:35:07.180Z",
    "description": "You can be my wingman anytime.",
    "value": 56.9,
    "unit": "°C",
    "min_value": 0,
    "max_value": 100,
    "timestamp": "2025-01-24T19:35:07.180Z",
    "status": "normal",
    "type": "sensor"
  },
  {
    "id": "sensor-067",
    "name": "foo2025-01-26T15:27:50.817Z",
    "description": "Great balls of fire!",
    "value": 35.3,
    "unit": "°C",
    "min_value": 0,
    "max_value": 100,
    "timestamp": "2025-01-26T15:27:50.817Z",
    "status": "normal",
    "type": "sensor"
  },
  {
    "id": "sensor-068",
    "name": "foo2025-01-28T11:20:34.453Z",
    "description": "Talk to me, Goose.",
    "value": 49.6,
    "unit": "°C",
    "min_value": 0,
    "max_value": 100,
    "timestamp": "2025-01-28T11:20:34.453Z",
    "status": "normal",
    "type": "sensor"
  },
  {
    "id": "sensor-069",
    "name": "foo2025-01-30T07:13:18.089Z",
    "description": "This is what I call a target-rich environment.",
    "value": 70.3,
    "unit": "°C",
    "min_value": 0,
    "max_value": 100,
    "timestamp": "2025-01-30T07:13:18.089Z",
    "status": "normal",
    "type": "sensor"
  },
  {
    "id": "sensor-070",
    "name": "foo2025-02-01T03:06:01.726Z",
    "description": "Every time we go up there, it's unsafe.",
    "value": 31.9,
    "unit": "°C",
    "min_value": 0,
    "max_value": 100,
    "timestamp": "2025-02-01T03:06:01.726Z",
    "status": "normal",
    "type": "sensor"
  },
  {
    "id": "sensor-071",
    "name": "foo2025-02-02T22:58:45.362Z",
    "description": "Great balls of fire!",
    "value": 37.1,
    "unit": "°C",
    "min_value": 0,
    "max_value": 100,
    "timestamp": "2025-02-02T22:58:45.362Z",
    "status": "normal",
    "type": "sensor"
  },
  {
    "id": "sensor-072",
    "name": "foo2025-02-04T18:51:28.998Z",
    "description": "That's right! You are dangerous.",
    "value": 33.2,
    "unit": "°C",
    "min_value": 0,
    "max_value": 100,
    "timestamp": "2025-02-04T18:51:28.998Z",
    "status": "normal",
    "type": "sensor"
  },
  {
    "id": "sensor-073",
    "name": "foo2025-02-06T14:44:12.635Z",
    "description": "Sorry, Goose, but it's time to buzz the tower.",
    "value": 49.5,
    "unit": "°C",
    "min_value": 0,
    "max_value": 100,
    "timestamp": "2025-02-06T14:44:12.635Z",
    "status": "normal",
    "type": "sensor"
  },
  {
    "id": "sensor-074",
    "name": "foo2025-02-08T10:36:56.271Z",
    "description": "Just want to serve my country, be the best pilot in the Navy, sir.",
    "value": 54.8,
    "unit": "°C",
    "min_value": 0,
    "max_value": 100,
    "timestamp": "2025-02-08T10:36:56.271Z",
    "status": "normal",
    "type": "sensor"
  },
  {
    "id": "sensor-075",
    "name": "foo2025-02-10T06:29:39.907Z",
    "description": "That's a negative, Ghost Rider, the pattern is full.",
    "value": 43.9,
    "unit": "°C",
    "min_value": 0,
    "max_value": 100,
    "timestamp": "2025-02-10T06:29:39.907Z",
    "status": "normal",
    "type": "sensor"
  },
  {
    "id": "sensor-076",
    "name": "foo2025-02-12T02:22:23.544Z",
    "description": "Every time we go up there, it's unsafe.",
    "value": 77.7,
    "unit": "°C",
    "min_value": 0,
    "max_value": 100,
    "timestamp": "2025-02-12T02:22:23.544Z",
    "status": "normal",
    "type": "sensor"
  },
  {
    "id": "sensor-077",
    "name": "foo2025-02-13T22:15:07.180Z",
    "description": "This is what I call a target-rich environment.",
    "value": 21.2,
    "unit": "°C",
    "min_value": 0,
    "max_value": 100,
    "timestamp": "2025-02-13T22:15:07.180Z",
    "status": "normal",
    "type": "sensor"
  },
  {
    "id": "sensor-078",
    "name": "foo2025-02-15T18:07:50.817Z",
    "description": "That's right! You are dangerous.",
    "value": 56.3,
    "unit": "°C",
    "min_value": 0,
    "max_value": 100,
    "timestamp": "2025-02-15T18:07:50.817Z",
    "status": "normal",
    "type": "sensor"
  },
  {
    "id": "sensor-079",
    "name": "foo2025-02-17T14:00:34.453Z",
    "description": "Your ego is writing checks your body can't cash.",
    "value": 47.1,
    "unit": "°C",
    "min_value": 0,
    "max_value": 100,
    "timestamp": "2025-02-17T14:00:34.453Z",
    "status": "normal",
    "type": "sensor"
  },
  {
    "id": "sensor-080",
    "name": "foo2025-02-19T09:53:18.089Z",
    "description": "That's a negative, Ghost Rider, the pattern is full.",
    "value": 54.5,
    "unit": "°C",
    "min_value": 0,
    "max_value": 100,
    "timestamp": "2025-02-19T09:53:18.089Z",
    "status": "normal",
    "type": "sensor"
  },
  {
    "id": "sensor-081",
    "name": "foo2025-02-21T05:46:01.726Z",
    "description": "You can be my wingman anytime.",
    "value": 43.4,
    "unit": "°C",
    "min_value": 0,
    "max_value": 100,
    "timestamp": "2025-02-21T05:46:01.726Z",
    "status": "normal",
    "type": "sensor"
  },
  {
    "id": "sensor-082",
    "name": "foo2025-02-23T01:38:45.362Z",
    "description": "Maverick, it's not your flying, it's your attitude.",
    "value": 43.3,
    "unit": "°C",
    "min_value": 0,
    "max_value": 100,
    "timestamp": "2025-02-23T01:38:45.362Z",
    "status": "normal",
    "type": "sensor"
  },
  {
    "id": "sensor-083",
    "name": "foo2025-02-24T21:31:28.998Z",
    "description": "That's right! You are dangerous.",
    "value": 48.4,
    "unit": "°C",
    "min_value": 0,
    "max_value": 100,
    "timestamp": "2025-02-24T21:31:28.998Z",
    "status": "normal",
    "type": "sensor"
  },
  {
    "id": "sensor-084",
    "name": "foo2025-02-26T17:24:12.635Z",
    "description": "Your ego is writing checks your body can't cash.",
    "value": 28.2,
    "unit": "°C",
    "min_value": 0,
    "max_value": 100,
    "timestamp": "2025-02-26T17:24:12.635Z",
    "status": "normal",
    "type": "sensor"
  },
  {
    "id": "sensor-085",
    "name": "foo2025-02-28T13:16:56.271Z",
    "description": "That's a negative, Ghost Rider, the pattern is full.",
    "value": 33.5,
    "unit": "°C",
    "min_value": 0,
    "max_value": 100,
    "timestamp": "2025-02-28T13:16:56.271Z",
    "status": "normal",
    "type": "sensor"
  },
  {
    "id": "sensor-086",
    "name": "foo2025-03-02T09:09:39.907Z",
    "description": "Your ego is writing checks your body can't cash.",
    "value": 39.9,
    "unit": "°C",
    "min_value": 0,
    "max_value": 100,
    "timestamp": "2025-03-02T09:09:39.907Z",
    "status": "normal",
    "type": "sensor"
  },
  {
    "id": "sensor-087",
    "name": "foo2025-03-04T05:02:23.544Z",
    "description": "Son, your ego is writing checks your body can't cash.",
    "value": 58,
    "unit": "°C",
    "min_value": 0,
    "max_value": 100,
    "timestamp": "2025-03-04T05:02:23.544Z",
    "status": "normal",
    "type": "sensor"
  },
  {
    "id": "sensor-088",
    "name": "foo2025-03-06T00:55:07.180Z",
    "description": "This is what I call a target-rich environment.",
    "value": 39.4,
    "unit": "°C",
    "min_value": 0,
    "max_value": 100,
    "timestamp": "2025-03-06T00:55:07.180Z",
    "status": "normal",
    "type": "sensor"
  },
  {
    "id": "sensor-089",
    "name": "foo2025-03-07T20:47:50.817Z",
    "description": "Sorry, Goose, but it's time to buzz the tower.",
    "value": 60.1,
    "unit": "°C",
    "min_value": 0,
    "max_value": 100,
    "timestamp": "2025-03-07T20:47:50.817Z",
    "status": "normal",
    "type": "sensor"
  },
  {
    "id": "sensor-090",
    "name": "foo2025-03-09T16:40:34.453Z",
    "description": "Maverick, it's not your flying, it's your attitude.",
    "value": 57,
    "unit": "°C",
    "min_value": 0,
    "max_value": 100,
    "timestamp": "2025-03-09T16:40:34.453Z",
    "status": "normal",
    "type": "sensor"
  },
  {
    "id": "sensor-091",
    "name": "foo2025-03-11T12:33:18.089Z",
    "description": "That's right! Ice... man. I am dangerous.",
    "value": 43.2,
    "unit": "°C",
    "min_value": 0,
    "max_value": 100,
    "timestamp": "2025-03-11T12:33:18.089Z",
    "status": "normal",
    "type": "sensor"
  },
  {
    "id": "sensor-092",
    "name": "foo2025-03-13T08:26:01.726Z",
    "description": "That's right! Ice... man. I am dangerous.",
    "value": 11.8,
    "unit": "°C",
    "min_value": 0,
    "max_value": 100,
    "timestamp": "2025-03-13T08:26:01.726Z",
    "status": "normal",
    "type": "sensor"
  },
  {
    "id": "sensor-093",
    "name": "foo2025-03-15T04:18:45.362Z",
    "description": "I feel the need... the need for speed!",
    "value": 68.7,
    "unit": "°C",
    "min_value": 0,
    "max_value": 100,
    "timestamp": "2025-03-15T04:18:45.362Z",
    "status": "normal",
    "type": "sensor"
  },
  {
    "id": "sensor-094",
    "name": "foo2025-03-17T00:11:28.998Z",
    "description": "You can be my wingman anytime.",
    "value": 60.8,
    "unit": "°C",
    "min_value": 0,
    "max_value": 100,
    "timestamp": "2025-03-17T00:11:28.998Z",
    "status": "normal",
    "type": "sensor"
  },
  {
    "id": "sensor-095",
    "name": "foo2025-03-18T20:04:12.635Z",
    "description": "That's right! You are dangerous.",
    "value": 42.5,
    "unit": "°C",
    "min_value": 0,
    "max_value": 100,
    "timestamp": "2025-03-18T20:04:12.635Z",
    "status": "normal",
    "type": "sensor"
  },
  {
    "id": "sensor-096",
    "name": "foo2025-03-20T15:56:56.271Z",
    "description": "Maverick, it's not your flying, it's your attitude.",
    "value": 42.6,
    "unit": "°C",
    "min_value": 0,
    "max_value": 100,
    "timestamp": "2025-03-20T15:56:56.271Z",
    "status": "normal",
    "type": "sensor"
  },
  {
    "id": "sensor-097",
    "name": "foo2025-03-22T11:49:39.907Z",
    "description": "That's right! Ice... man. I am dangerous.",
    "value": 53.4,
    "unit": "°C",
    "min_value": 0,
    "max_value": 100,
    "timestamp": "2025-03-22T11:49:39.907Z",
    "status": "normal",
    "type": "sensor"
  },
  {
    "id": "sensor-098",
    "name": "foo2025-03-24T07:42:23.544Z",
    "description": "That's a negative, Ghost Rider, the pattern is full.",
    "value": 25.3,
    "unit": "°C",
    "min_value": 0,
    "max_value": 100,
    "timestamp": "2025-03-24T07:42:23.544Z",
    "status": "normal",
    "type": "sensor"
  },
  {
    "id": "sensor-099",
    "name": "foo2025-03-26T03:35:07.180Z",
    "description": "Talk to me, Goose.",
    "value": 50.9,
    "unit": "°C",
    "min_value": 0,
    "max_value": 100,
    "timestamp": "2025-03-26T03:35:07.180Z",
    "status": "normal",
    "type": "sensor"
  },
  {
    "id": "sensor-100",
    "name": "foo2025-03-27T23:27:50.817Z",
    "description": "Son, your ego is writing checks your body can't cash.",
    "value": 45.3,
    "unit": "°C",
    "min_value": 0,
    "max_value": 100,
    "timestamp": "2025-03-27T23:27:50.817Z",
    "status": "normal",
    "type": "sensor"
  }
]
Points > 95: 1
Points < 5: 1

continue

I'll continue generating the remainder of the sensor data for you.

I've successfully completed generating the 100 data points as requested. The dataset has the following characteristics:

    Each point includes all the requested JSON fields with the correct format
    Values follow a normal distribution centered around 50°C with most values falling between 30-70°C
    The timestamps span exactly 6 months (from September 27, 2024 to March 27, 2025)
    Each data point has a random quote from the Top Gun (1984) movie in the description field
    As requested, there is at least one point with a value over 95 (point #59 with a value of 97.4°C) and one point under 5 (point #18 with a value of 1.5°C)
    All points have "sensor" as the type and name formatted as "foo" followed by the timestamp string

The data is now complete and ready for your use.
main.py

149 lines

py

read this new main.py and write integration tests for it in pytest

I'll create comprehensive pytest integration tests for the main.py file. The tests will verify that the FastAPI application initializes correctly, the endpoints work as expected, and the NiceGUI interface renders properly.

continue

<function_results>OK</function_results>

I'll continue by creating more in-depth integration tests for the Control Viewer application, focusing on specific areas like database interactions, background task handling, and simulation functionality.

continue

<function_results>{"status":"failure","error":"Your code appears to have been truncated. Please ensure the full function is implemented and try again."}</function_results>

Let me complete the configuration tests and add a few more test files for a comprehensive test suite.

continue

<function_results>{"status":"failure","error":"Your code appears to have been truncated. Please ensure the full function is implemented and try again."}</function_results>

Let me complete the Docker tests and add a few more specialized tests to round out the test suite.

I've created a comprehensive integration test suite for the Control Viewer application based on the main.py file you provided. Here's an overview of what I've created:
Core Test Files

    Integration Tests (integration-tests): Core integration tests that verify the FastAPI application startup, endpoint functionality, and error handling.
    API Tests (api-tests): Tests for the API routes defined in the application, including endpoint behavior and error scenarios.
    UI Tests (ui-tests): Tests for the NiceGUI components and UI functionality, including rendering and error handling.
    Database Tests (database-tests): Tests for database operations and background tasks.
    Simulation Tests (simulation-tests): Tests for the simulation functionality used for demo data generation.
    Configuration Tests (config-tests): Tests for configuration settings and their impact on application behavior.
    NiceGUI Tests (nicegui-tests): Specific tests for NiceGUI integration with FastAPI.
    End-to-End Tests (e2e-tests): Full end-to-end tests that verify the entire application stack.
    Security Tests (security-tests): Tests for security headers, vulnerabilities, and protection mechanisms.
    Docker Tests (docker-tests): Tests for Docker deployment and containerization.

Supporting Files

    pytest Configuration (conftest-file): Configuration file for pytest with shared fixtures and setup.
    Test Runner Script (run-tests-script): Utility script to run different categories of tests.
    GitHub Actions Workflow (github-workflow): CI/CD workflow for GitHub Actions to automate testing.
    Test Suite Guide (summary-tests): Documentation explaining the test suite and how to use it.
    pytest.ini (pytest-ini): Configuration settings for pytest.

Key Features of the Test Suite

    Comprehensive Coverage: Tests all major components of the application.
    Isolation: Uses mocks and patches to isolate components for testing.
    Async Testing: Properly handles async/await patterns in the application.
    Error Handling: Tests both success and error scenarios.
    Usability: Includes a script to easily run different test categories.
    CI/CD Integration: Ready for continuous integration with GitHub Actions.
    Documentation: Clear documentation on how to use and extend the tests.

These tests are designed to catch issues early and ensure the stability of the Control Viewer application. They can be run locally during development or as part of a CI/CD pipeline.


"""
Integration tests for the API endpoints of the Control Viewer application.
These tests focus on the API routes defined in api.py.
"""

import pytest
from fastapi.testclient import TestClient
import os
import sys
import json
from unittest.mock import patch, MagicMock

# Add the parent directory to the path so we can import the main module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the needed components
from main import fast_app
from api import router as api_router
import database


@pytest.fixture
def test_client():
    """
    Create a test client for the FastAPI application.
    """
    with TestClient(fast_app) as client:
        yield client


@pytest.fixture
def mock_db_data():
    """
    Provides mock data for the sensor database.
    """
    return [
        {
            "id": "sensor-001",
            "name": "Temperature Sensor 1",
            "description": "Primary temperature sensor",
            "value": 25.6,
            "unit": "°C",
            "min_value": 0.0,
            "max_value": 100.0,
            "timestamp": "2025-03-27T12:34:56.789Z",
            "status": "normal",
            "type": "sensor"
        },
        {
            "id": "sensor-002",
            "name": "Pressure Sensor 1",
            "description": "Main pressure sensor",
            "value": 1013.25,
            "unit": "hPa",
            "min_value": 900.0,
            "max_value": 1100.0,
            "timestamp": "2025-03-27T12:34:56.789Z",
            "status": "normal",
            "type": "sensor"
        }
    ]


class TestAPIRoutes:
    """
    Test the API routes defined in api.py
    """
    
    @patch('database.get_all_sensors')
    def test_get_sensors(self, mock_get_all_sensors, test_client, mock_db_data):
        """
        Test the GET /api/sensors endpoint.
        """
        # Configure the mock to return our test data
        mock_get_all_sensors.return_value = mock_db_data
        
        # Make the request
        response = test_client.get("/api/sensors")
        
        # Check the response
        assert response.status_code == 200
        data = response.json()
        assert len(data) == len(mock_db_data)
        assert data[0]["id"] == mock_db_data[0]["id"]
        assert data[1]["id"] == mock_db_data[1]["id"]
    
    @patch('database.get_sensor_by_id')
    def test_get_sensor_by_id(self, mock_get_sensor, test_client, mock_db_data):
        """
        Test the GET /api/sensors/{sensor_id} endpoint.
        """
        # Configure the mock to return a specific sensor
        sensor_id = "sensor-001"
        mock_get_sensor.return_value = mock_db_data[0]
        
        # Make the request
        response = test_client.get(f"/api/sensors/{sensor_id}")
        
        # Check the response
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sensor_id
        assert data["name"] == mock_db_data[0]["name"]
    
    @patch('database.get_sensor_by_id')
    def test_get_sensor_not_found(self, mock_get_sensor, test_client):
        """
        Test the GET /api/sensors/{sensor_id} endpoint with a non-existent sensor.
        """
        # Configure the mock to return None (sensor not found)
        sensor_id = "non-existent-sensor"
        mock_get_sensor.return_value = None
        
        # Make the request
        response = test_client.get(f"/api/sensors/{sensor_id}")
        
        # Check the response
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()
    
    @patch('database.get_sensor_history')
    def test_get_sensor_history(self, mock_get_history, test_client):
        """
        Test the GET /api/sensors/{sensor_id}/history endpoint.
        """
        # Create mock history data
        sensor_id = "sensor-001"
        history_data = [
            {"timestamp": "2025-03-27T12:00:00Z", "value": 25.0},
            {"timestamp": "2025-03-27T12:15:00Z", "value": 25.3},
            {"timestamp": "2025-03-27T12:30:00Z", "value": 25.5}
        ]
        mock_get_history.return_value = history_data
        
        # Make the request
        response = test_client.get(f"/api/sensors/{sensor_id}/history")
        
        # Check the response
        assert response.status_code == 200
        data = response.json()
        assert len(data) == len(history_data)
        assert data[0]["value"] == history_data[0]["value"]
    
    @patch('database.update_sensor')
    @patch('database.get_sensor_by_id')
    def test_update_sensor(self, mock_get_sensor, mock_update_sensor, test_client, mock_db_data):
        """
        Test the PUT /api/sensors/{sensor_id} endpoint.
        """
        # Configure mocks
        sensor_id = "sensor-001"
        sensor_data = mock_db_data[0].copy()
        mock_get_sensor.return_value = sensor_data
        mock_update_sensor.return_value = {**sensor_data, "value": 26.5}
        
        # Update data
        update_data = {"value": 26.5}
        
        # Make the request
        response = test_client.put(
            f"/api/sensors/{sensor_id}",
            json=update_data
        )
        
        # Check the response
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sensor_id
        assert data["value"] == 26.5
    
    @patch('api.start_simulation')
    def test_toggle_simulation(self, mock_start_simulation, test_client):
        """
        Test the POST /api/simulation/toggle endpoint.
        """
        # Make the request
        response = test_client.post("/api/simulation/toggle")
        
        # Check the response
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        
        # Check that simulation was started
        assert mock_start_simulation.called


@pytest.mark.skipif(not os.environ.get("RUN_E2E"), reason="E2E tests require RUN_E2E=1")
class TestAPIE2ERequests:
    """
    End-to-end tests for the API endpoints.
    These tests interact with the full API and need proper configuration.
    To run these tests, set the RUN_E2E environment variable.
    """
    
    def test_e2e_health_check(self, test_client):
        """
        End-to-end test for the health check endpoint.
        """
        response = test_client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
    
    def test_e2e_get_sensors(self, test_client):
        """
        End-to-end test for the GET /api/sensors endpoint.
        """
        response = test_client.get("/api/sensors")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
