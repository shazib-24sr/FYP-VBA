const mockData = {
    totalVehicles: 77,
    totalViolations: 19,
    mostViolatedVehicle: "ARM-720",
    mostViolationCount: 9,
    mostViolationsType: "Over Speeding",
    violations: 13,
    capturedSpots: [1, 2, 3, 4],
    specificViolations: {
      spot1: 2,
      spot2: 4,
      spot3: 8,
      spot4: 6,
    },
    pieChartData: [
      { label: "Over Speeding", value: 25 },
      { label: "Wrong Way", value: 8 },
      { label: "Lane Change", value: 12 },
    ],
    totalViolationsGraph: [
      { spot: 1, value: 6 },
      { spot: 2, value: 9 },
      { spot: 3, value: 17 },
      { spot: 4, value: 11 },
    ],
  };
  
  export default mockData;
  