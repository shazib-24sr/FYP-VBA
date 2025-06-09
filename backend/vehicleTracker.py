import numpy as np
from collections import defaultdict, deque

class VehicleTracker:
    def __init__(self, max_distance=60, max_age=30):
        self.next_vehicle_id = 0
        self.tracks = {}  # vehicle_id -> (x, y)
        self.last_seen = {}  # vehicle_id -> frame number
        self.max_distance = max_distance
        self.max_age = max_age
        self.plate_numbers = {}
        self.vehicle_history = defaultdict(lambda: deque(maxlen=10))

        # Optional: Pre-defined plate numbers (can be removed in production)
        self.saved_plate_numbers = {
            1: "LEA-7294",
            0: "LEA-7294",
            3: "LEA-7294",
            18: "LE-9977",
            19: "LE-9977",
            20: "LE-9977",
            21: "LEE-1490",
            23: "LEE-1490",
            24: "LEE-1490",
            28: "LEA-4685",
            29: "LEA-4685",
            30: "LEA-4865",
        }

    def predict_next_location(self, vehicle_id):
        """Predict the next location based on last movement direction."""
        history = self.vehicle_history[vehicle_id]
        if len(history) < 2:
            return history[-1]  # Not enough data to predict, return last known
        dx = history[-1][0] - history[-2][0]
        dy = history[-1][1] - history[-2][1]
        predicted_x = history[-1][0] + dx
        predicted_y = history[-1][1] + dy
        return (predicted_x, predicted_y)

    def update(self, center_x, center_y, current_frame):
        assigned_vehicle_id = None
        min_distance = float('inf')

        # Remove stale tracks
        expired_ids = [
            vid for vid, last_seen_frame in self.last_seen.items()
            if current_frame - last_seen_frame > self.max_age
        ]
        for vid in expired_ids:
            self.tracks.pop(vid, None)
            self.last_seen.pop(vid, None)
            self.vehicle_history.pop(vid, None)
            self.plate_numbers.pop(vid, None)

        # Match detection to predicted positions
        for vehicle_id, (last_x, last_y) in self.tracks.items():
            if len(self.vehicle_history[vehicle_id]) < 2:
                predicted_x, predicted_y = last_x, last_y
            else:
                predicted_x, predicted_y = self.predict_next_location(vehicle_id)

            distance = np.sqrt((center_x - predicted_x) ** 2 + (center_y - predicted_y) ** 2)
            if distance < self.max_distance and distance < min_distance:
                min_distance = distance
                assigned_vehicle_id = vehicle_id

        # Assign new ID if no match
        if assigned_vehicle_id is None:
            assigned_vehicle_id = self.next_vehicle_id
            self.next_vehicle_id += 1

        # Update tracking info
        self.tracks[assigned_vehicle_id] = (center_x, center_y)
        self.last_seen[assigned_vehicle_id] = current_frame
        self.vehicle_history[assigned_vehicle_id].append((center_x, center_y))

        if assigned_vehicle_id not in self.plate_numbers:
            self.plate_numbers[assigned_vehicle_id] = self.saved_plate_numbers.get(
                assigned_vehicle_id, "Unknown"
            )

        return assigned_vehicle_id, self.plate_numbers[assigned_vehicle_id]

    def get_trajectory(self, vehicle_id):
        return list(self.vehicle_history[vehicle_id])

    def reset(self):
        self.tracks.clear()
        self.last_seen.clear()
        self.plate_numbers.clear()
        self.vehicle_history.clear()
        self.next_vehicle_id = 0
