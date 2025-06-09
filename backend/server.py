import os
from flask import Flask, request, jsonify, send_from_directory, make_response, abort
from flask_cors import CORS
from vehicleDetector import VehicleDetector
import pandas as pd
from glob import glob
import subprocess
import numpy as np
from collections import defaultdict 
import re
from datetime import datetime
from pymongo import MongoClient
from bson.binary import Binary
from datetime import datetime
import base64
import shutil

app = Flask(__name__)
CORS(app)


UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
VIOLATION_FOLDER = 'violations'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

SUMMARY_FILE = os.path.join(OUTPUT_FOLDER, 'summary.csv')

client = MongoClient('mongodb://localhost:27017/')
db = client['vehicle_db']

vehicles_col = db['vehicles']
users_collection = db['users']

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'success': False, 'message': 'Missing credentials'}), 400

    user = users_collection.find_one({'email': email})

    if user and user.get('password') == password:
        return jsonify({'success': True}), 200
    else:
        return jsonify({'success': False, 'message': 'Invalid credentials'}), 401

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')

    if not name or not email or not password:
        return jsonify({'error': 'All fields are required'}), 400

    if users_collection.find_one({'email': email}):
        return jsonify({'error': 'Email already exists'}), 400

    user_data = {
        'name': name,
        'email': email,
        'password': password  # In real apps, hash the password!
    }
    users_collection.insert_one(user_data)
    return jsonify({'message': 'User registered successfully'}), 200



def get_image_bytes(frame_path):
    with open(frame_path, 'rb') as f:
        return Binary(f.read())

def update_vehicle_history_from_summary(summary_df, video_processed_time=None):
    if video_processed_time is None:
        video_processed_time = datetime.utcnow()

    for _, row in summary_df.iterrows():
        plate = row['plate_number']
        if plate == 'Unknown' or pd.isna(plate):
            continue

        vehicle = vehicles_col.find_one({"plate_number": plate})

        if not vehicle:
            vehicle_doc = {
                "plate_number": plate,
                "total_violations": 0,
                "last_updated": video_processed_time,
                "violations_details": []
            }
            vehicle_id = vehicles_col.insert_one(vehicle_doc).inserted_id
        else:
            vehicle_id = vehicle['_id']

        violation_str = row.get('violations')
        violation_count = int(row.get('violation_count', 0))

        if pd.notna(violation_str) and violation_count > 0:
            violation_types = [v.strip() for v in violation_str.split(',')]

            for violation_type in violation_types:
                frame_folder = f"violations/{violation_type}/"
                frame_filename = f"{row['vehicle_id']}_"
                
                # Match the first image starting with vehicle_id_
                matches = [f for f in os.listdir(frame_folder) if f.startswith(frame_filename)]
                if not matches:
                    continue
                
                frame_path = os.path.join(frame_folder, matches[0])
                image_data = get_image_bytes(frame_path)

                violation_detail = {
                    "type": violation_type,
                    "image_data": image_data,
                    "timestamp": video_processed_time
                }

                # Avoid duplicate insertions
                if vehicle and "violations_details" in vehicle:
                    existing = [
                        v for v in vehicle["violations_details"]
                        if v["type"] == violation_type and v["timestamp"] == video_processed_time
                    ]
                    if existing:
                        continue

                # Push this violation detail and increment total_violations
                vehicles_col.update_one(
                    {"_id": vehicle_id},
                    {
                        "$inc": {"total_violations": 1},
                        "$set": {"last_updated": video_processed_time},
                        "$push": {"violations_details": violation_detail}
                    }
                )

@app.route('/vehicles', methods=['GET'])
def list_vehicles():
    search = request.args.get('search', '').strip()
    query = {}
    if search:
        query = {"plate_number": {"$regex": search, "$options": "i"}}

    vehicles = vehicles_col.find(query)
    result = []
    for v in vehicles:
        result.append({
            "id": str(v["_id"]),
            "plate_number": v["plate_number"],
            "total_violations": v.get("total_violations", 0),
            "last_updated": v.get("last_updated", "").isoformat() if v.get("last_updated") else ""
        })
    return jsonify(result)


@app.route('/vehicles/<plate_number>', methods=['GET'])
def get_vehicle_details(plate_number):
    vehicle = vehicles_col.find_one({"plate_number": plate_number})
    if not vehicle:
        return jsonify({"error": "Vehicle not found"}), 404

    violations = vehicle.get("violations_details", [])
    violation_list = []
    for v in violations:
        violation_list.append({
            "violation_type": v["type"],
            "video_datetime": v["timestamp"].isoformat(),
            "image_data": base64.b64encode(v["image_data"]).decode('utf-8')
        })

    return jsonify({
        "plate_number": vehicle["plate_number"],
        "total_violations": vehicle.get("total_violations", 0),
        "last_updated": vehicle.get("last_updated", "").isoformat() if vehicle.get("last_updated") else "",
        "violations": violation_list
    })

@app.route('/violations', methods=['GET'])
def get_violations():
    vehicle_id_query = request.args.get('vehicleId', '').strip().lower()

    if not vehicle_id_query:
        return jsonify({'error': 'Missing vehicle ID'}), 400

    if not os.path.exists(SUMMARY_FILE):
        return jsonify({'error': 'Summary file not found'}), 500

    try:
        # Read CSV and clean data
        df = pd.read_csv(SUMMARY_FILE, quotechar='"', skipinitialspace=True)

        # Normalize fields for comparison
        df['vehicle_id'] = df['vehicle_id'].astype(str).str.strip().str.lower()
        df['plate_number'] = df['plate_number'].astype(str).str.strip().str.lower()

        matched = df[
            (df['vehicle_id'] == vehicle_id_query) |
            (df['plate_number'] == vehicle_id_query)
        ]

        if matched.empty:
            return jsonify({
                "summary": {},
                "violations": [],
                "capturedSpots": [],
                "pieChartData": []
            })

        row = matched.iloc[0]

        summary = {
    "total_distance": float(row.get('distance', 0))+300,
    "avg_speed": float(row.get('average_speed', 0)),
    "total_violations": int(row.get('violation_count', 0))
}

        # Parse violations into list
        violations_raw = str(row.get('violations', '')).strip()
        violations_list = [v.strip() for v in violations_raw.split(',')] if violations_raw else []

        violations = [{
            "violationType": v
        } for v in violations_list if v]

        # Pie chart data for frontend
        pie_chart_data = []
        if violations_list:
            from collections import Counter
            counts = Counter(violations_list)
            pie_chart_data = [{"type": v_type, "count": count} for v_type, count in counts.items()]

        return jsonify({
            "summary": summary,
            "violations": violations,
            "capturedSpots": [],
            "pieChartData": pie_chart_data
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


def aggregate_vehicle_data(df):
    def mode_or_unknown(series):
        # Return most common value or 'Unknown' if empty
        if series.empty:
            return 'Unknown'
        else:
            return series.mode().iloc[0] if not series.mode().empty else 'Unknown'
    
    # Create a grouping key: if plate_number != 'Unknown', use plate_number else use vehicle_id as string
    df['group_key'] = df.apply(lambda row: row['plate_number'] if row['plate_number'] != 'Unknown' else f"id_{row['vehicle_id']}", axis=1)
    
    agg_rows = []
    
    for group, group_df in df.groupby('group_key'):
        # Calculate total distance and total time ignoring zeros for speed calculation
        valid_speed_rows = group_df[(group_df['distance_meters'] > 0) & (group_df['time_seconds'] > 0)]
        total_distance = valid_speed_rows['distance_meters'].sum()
        total_time = valid_speed_rows['time_seconds'].sum()
        avg_speed = total_distance / total_time if total_time > 0 else 0
        
        # Aggregate other columns
        vehicle_id = group_df['vehicle_id'].mode().iloc[0]
        plate_number = group_df['plate_number'].mode().iloc[0]
        vehicle_class = mode_or_unknown(group_df['class'])
        confidence = group_df['confidence'].mean()
        lane_status = mode_or_unknown(group_df['lane_status'])
        direction = mode_or_unknown(group_df['direction'])
        
        # Bounding box coords - you can take median or mean for approximate location
        x1 = int(group_df['x1'].median())
        y1 = int(group_df['y1'].median())
        x2 = int(group_df['x2'].median())
        y2 = int(group_df['y2'].median())
        
        agg_rows.append({
            'vehicle_id': vehicle_id,
            'plate_number': plate_number,
            'class': vehicle_class,
            'confidence': confidence,
            'x1': x1,
            'y1': y1,
            'x2': x2,
            'y2': y2,
            'speed_kmph': avg_speed,
            'total_distance_m': total_distance,
            'total_time_s': total_time,
            'direction': direction,
            'lane_status': lane_status,
        })
    
    return pd.DataFrame(agg_rows)

def clear_folder(folder_path):
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)  # delete file or symbolic link
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)  # delete folder and its contents
        except Exception as e:
            print(f'Failed to delete {file_path}. Reason: {e}')


@app.route('/upload', methods=['POST'])
def upload_videos():
    clear_folder(UPLOAD_FOLDER)
    clear_folder(OUTPUT_FOLDER)
    clear_folder(VIOLATION_FOLDER)
    print("Clearing folders...")
    uploaded_files = request.files
    responses = []

    for key in uploaded_files:
        file = uploaded_files[key]
        if file:
            filename = file.filename
            input_path = os.path.join(UPLOAD_FOLDER, filename)
            output_filename = f"output_{filename}"
            output_path = os.path.join(OUTPUT_FOLDER, output_filename)
            csv_filename = f"detections_{filename}.csv"
            csv_path = os.path.join(OUTPUT_FOLDER, csv_filename)

            file.save(input_path)

            # Define custom box and lines for video 2
            if "2" in filename.lower():  # You can check any identifier in the filename
               
                box_points = np.array([(614, 435), (701, 812),(1851, 602) ,(972, 415)], dtype=np.int32)
                detector = VehicleDetector(
                    model_path="yolov8n.pt",
                    plate_model_path="",
                    video_path=input_path,
                    output_path=output_path,
                    csv_path=csv_path,
                    resolution=(640, 480),
                    frame_skip=1,
                    line1=[(708, 442), (1081, 783)],
                    line2=[(972, 415), (1851, 602)],
                   
                    box_points=box_points
                )
            else:
                detector = VehicleDetector(
                    model_path="yolov8n.pt",
                    plate_model_path="",
                    video_path=input_path,
                    output_path=output_path,
                    csv_path=csv_path,
                    resolution=(640, 480),
                    frame_skip=1
                )

            detector.process_video(output_path)

            if os.path.exists(csv_path):
                df = pd.read_csv(csv_path)
                aggregated_df = aggregate_vehicle_data(df)
                aggregated_csv_filename = f"aggregated_{filename}.csv"
                aggregated_csv_path = os.path.join(OUTPUT_FOLDER, aggregated_csv_filename)
                aggregated_df.to_csv(aggregated_csv_path, index=False)
            else:
                aggregated_csv_filename = None

            responses.append({
                "filename": filename,
                "output_video": output_filename,
                "csv_data_path": csv_filename,
                "aggregated_csv_path": aggregated_csv_filename
            })

    combine_aggregated_data()
    summary_df = pd.read_csv(SUMMARY_FILE)
   
    video_processed_time = datetime.utcnow()  # <== Add this line
    update_vehicle_history_from_summary(summary_df, video_processed_time)

    update_vehicle_history_from_summary(summary_df)
    return jsonify({
        "status": "success",
        "message": "Videos processed and aggregated successfully",
        "results": responses
    })

@app.route('/dashboard-data', methods=['GET'])
def get_dashboard_data():
    aggregated_files = [f for f in os.listdir(OUTPUT_FOLDER) if f.startswith('aggregated_') and f.endswith('.csv')]
    if not aggregated_files:
        return jsonify({"error": "No aggregated CSV data available"}), 404

    all_rows = []
    for idx, filename in enumerate(aggregated_files, start=1):
        df = pd.read_csv(os.path.join(OUTPUT_FOLDER, filename))

        
        df['group_key'] = df.apply(
            lambda row: row['plate_number'] if row['plate_number'] != 'Unknown' and pd.notna(row['plate_number'])
            else f"id_{row['vehicle_id']}", axis=1
        )

        df['captured_spot'] = f"GT Road Wazirabad-{idx}"

        
        df['overspeeding'] = df['speed_kmph'] > 50
        df['wrong_way'] = df['direction'].str.lower().eq('wrong way')
        df['lane_violation'] = df['lane_status'].str.lower().isin(['abrupt lane change', 'illegal lane change'])

        all_rows.append(df)

    
    combined_df = pd.concat(all_rows, ignore_index=True)
    

   
    violation_columns = ['overspeeding', 'wrong_way', 'lane_violation']
    combined_df[violation_columns] = combined_df[violation_columns].astype(int)
    combined_df['violations_count'] = combined_df[violation_columns].sum(axis=1)

    unique_vehicles = combined_df['group_key'].nunique()
    total_violations = combined_df['violations_count'].sum()
    overspeeding_count = combined_df['overspeeding'].sum()
    wrong_way_count = combined_df['wrong_way'].sum()
    lane_violation_count = combined_df['lane_violation'].sum()

   
    vehicle_violation_summary = combined_df.groupby('vehicle_id')['violations_count'].sum()
    most_violated_count = int(vehicle_violation_summary.max())
    tied_vehicle_ids = vehicle_violation_summary[vehicle_violation_summary == most_violated_count].index.tolist()

    # Filter combined_df for tied vehicles
    tied_rows = combined_df[combined_df['vehicle_id'].isin(tied_vehicle_ids)]

    # Prefer a known plate_number if available
    known_plate_rows = tied_rows[tied_rows['plate_number'].ne('Unknown') & pd.notna(tied_rows['plate_number'])]
   

    if not known_plate_rows.empty:
        most_violated_plate = known_plate_rows.iloc[0]['plate_number']
    else:
        most_violated_plate = f"id_{tied_rows.iloc[0]['vehicle_id']}"

    # Most common violation type
    violation_type_counts = {
        "Over Speeding": int(overspeeding_count),
        "Wrong Way": int(wrong_way_count),
        "Lane Violation": int(lane_violation_count),
    }
    most_violations_type = max(violation_type_counts.items(), key=lambda x: x[1])[0]

    # Per-spot violation count
    specific_violations = {
        f"GT Road Wazirabad Location {idx + 1}": int(df[violation_columns].sum().sum())
        for idx, df in enumerate(all_rows)
    }

    # Build response
    dashboard_data = {
        "totalVehicles": int(unique_vehicles),
        "totalViolations": int(total_violations),
        "mostViolatedVehicle": most_violated_plate,
        "mostViolationCount": most_violated_count,
        "mostViolationsType": most_violations_type,
        "capturedSpots": list(specific_violations.keys()),
        "specificViolations": specific_violations,
        "pieChartData": [
            {"label": "Over Speeding", "value": int(overspeeding_count)},
            {"label": "Wrong Way", "value": int(wrong_way_count)},
            {"label": "Lane Violation", "value": int(lane_violation_count)},
        ],
        "totalViolationsGraph": [
            {
                "GT Road Wazirabad Location": f"GT Road Wazirabad Location{idx + 1}",
                "value": int(df[violation_columns].sum().sum())
            }
            for idx, df in enumerate(all_rows)
        ]
    }

    return jsonify(dashboard_data)


def combine_aggregated_data():
    # Only get CSVs starting with 'aggregated'
    csv_files = glob(os.path.join(OUTPUT_FOLDER, "aggregated*.csv"))
    print(f"[INFO] Found {len(csv_files)} aggregated CSV files.")

    all_dfs = []

    for file in csv_files:
        try:
            df = pd.read_csv(file)
            if not df.empty:
                # Ensure 'speed_kmph' is numeric
                df['speed_kmph'] = pd.to_numeric(df['speed_kmph'], errors='coerce')
                all_dfs.append(df)
            else:
                print(f"[WARNING] Skipped empty file: {file}")
        except Exception as e:
            print(f"[ERROR] Failed to read {file}: {e}")

    if not all_dfs:
        print("[ERROR] No valid CSV files to combine.")
        return None

    # Combine all valid DataFrames
    combined_df = pd.concat(all_dfs, ignore_index=True)

    # Drop rows with missing 'speed_kmph'
    combined_df.dropna(subset=['speed_kmph'], inplace=True)

    # Group and summarize data
    def detect_violations(group):
        violations = set()
        max_speed = group['speed_kmph'].max()

        if max_speed > 50:
            violations.add("overspeeding")

        if 'direction' in group and (group['direction'] == "wrong way").any():
            violations.add("wrongway")

        if 'lane_status' in group and (group['lane_status'] == "abrupt lane change").any():
            violations.add("abruptLaneChange")

        return list(violations)

    summary = combined_df.groupby(['vehicle_id', 'plate_number']).apply(
        lambda group: pd.Series({
            'distance': group.get('total_distance_m', pd.Series([0])).sum(),
            'average_speed': group['speed_kmph'].mean(),
            'max_speed': group['speed_kmph'].max(),
            'violations': ', '.join(detect_violations(group)),
            'violation_count': len(detect_violations(group))
        })
    ).reset_index()

    # Reorder columns to include max_speed
    summary = summary[['vehicle_id', 'plate_number', 'distance', 'average_speed', 'max_speed', 'violations', 'violation_count']]

    # Save to CSV
    output_path = os.path.join(OUTPUT_FOLDER, "summary.csv")
    summary.to_csv(output_path, index=False)

    print(f"[SUCCESS] Aggregated summary saved to: {output_path}")
    return summary



@app.route('/video/<filename>')
def serve_video(filename):
    input_path = os.path.join('outputs', filename)

    if not os.path.exists(input_path):
        return abort(404, description="Video not found")

    # Generate output filename with _fixed suffix
    name, ext = os.path.splitext(filename)
    fixed_filename = f"{name}_fixed{ext}"
    fixed_path = os.path.join('outputs', fixed_filename)

    # Convert only if not already done
    if not os.path.exists(fixed_path):
        try:
            subprocess.run([
                'ffmpeg',
                '-y',  # overwrite if needed
                '-i', input_path,
                '-vcodec', 'libx264',
                '-an',  # remove audio
                fixed_path
            ], check=True)
        except subprocess.CalledProcessError as e:
            return abort(500, description=f"Video conversion failed: {str(e)}")

    return send_from_directory('outputs', fixed_filename)



@app.route('/violation-frame/<violation_type>/<filename>', methods=['GET'])
def serve_violation_frame(violation_type, filename):
    folder_path = os.path.join('violations', violation_type)
    return send_from_directory(folder_path, filename)

@app.route('/viewViolatedFrame/<violation_type>', methods=['GET'])
def view_violated_frames(violation_type):
    # Load CSV and filter vehicles with the specific violation
    
    if not os.path.exists(SUMMARY_FILE):
        return jsonify({'error': 'summary.csv not found'}), 404

    df = pd.read_csv(SUMMARY_FILE)

    # Ensure required columns exist
    if 'vehicle_id' not in df.columns or 'violations' not in df.columns:
        return jsonify({'error': 'Required columns not found in CSV'}), 400

    # Filter vehicle IDs with the given violation
    matching_vehicles = df[df['violations'].str.contains(violation_type, case=False, na=False)]
    valid_vehicle_ids = set(matching_vehicles['vehicle_id'])

    if not valid_vehicle_ids:
        return jsonify([])  # No violations of this type

    # Load violation images
    folder_path = os.path.join('violations', violation_type)
    if not os.path.exists(folder_path):
        return jsonify([])  # No folder for that violation

    vehicle_images = defaultdict(list)
    pattern = re.compile(r"(\d+)_frame_(\d+)_")  # e.g., 5_frame_102_

    for img in os.listdir(folder_path):
        if img.lower().endswith(('.jpg', '.png')):
            match = pattern.match(img)
            if match:
                vehicle_id = int(match.group(1))
                frame_number = int(match.group(2))
                if vehicle_id in valid_vehicle_ids:
                    vehicle_images[vehicle_id].append((frame_number, img))

    selected_images = []

    for vehicle_id, frames in vehicle_images.items():
        frames.sort(key=lambda x: x[0])
        first_two = frames[:2]
        last_two = frames[-2:]

        for _, img_name in (first_two + last_two):
            img_url = f'/violation-frame/{violation_type}/{img_name}'
            selected_images.append(img_url)

    return jsonify(selected_images)

@app.route('/viewViolatedFrameByVehicle/<violation_type>/<vehicle_id>', methods=['GET'])
def view_violated_frames_by_vehicle(violation_type, vehicle_id):
    folder_path = os.path.join('violations', violation_type)
    if not os.path.exists(folder_path):
        return jsonify([])

    pattern = re.compile(rf"^{vehicle_id}_frame_(\d+)_")  # Match frame number
    frame_images = []

    for img in os.listdir(folder_path):
        if img.lower().endswith(('.jpg', '.png')) and img.startswith(f"{vehicle_id}_"):
            match = pattern.match(img)
            if match:
                frame_number = int(match.group(1))
                frame_images.append((frame_number, img))

    # Sort by frame number
    frame_images.sort(key=lambda x: x[0])

    # Select 2 from start and 2 from end
    selected = frame_images[:2] + frame_images[-2:]

    # Remove duplicates if total < 4
    selected = list(dict.fromkeys(selected))

    # Create URLs
    result = [f'/violation-frame/{violation_type}/{img_name}' for _, img_name in selected]

    return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True)
