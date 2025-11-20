# _utils.py
import numpy as np
import isodate
import datetime

def get_todays_date():
	# YYYY-MM-DD
	return datetime.datetime.now().strftime('%Y-%m-%d')

def calculate_fp(player_stats):
	FP_WEIGHTS = {
		'points': 1,
		'reboundsTotal': 1.2,
		'assists': 1.5,
		'steals': 3,
		'blocks': 3,
		'turnovers': -1,
	}

	stats = np.array([player_stats.get(stat, 0) for stat in FP_WEIGHTS.keys()])
	weights = np.array(list(FP_WEIGHTS.values()))
	fp = np.dot(stats, weights)
	fp = round(fp, 2)
	return fp

def parse_iso_duration(iso_duration):
	parsed_duration = isodate.parse_duration(iso_duration)
	total_seconds = int(parsed_duration.total_seconds())
	minutes = total_seconds // 60
	seconds = total_seconds % 60

	return minutes, seconds

def parse_duration_to_seconds(iso_duration):
	parsed_duration = isodate.parse_duration(iso_duration)
	total_seconds = int(parsed_duration.total_seconds())
	
	return total_seconds

def parse_iso_datetime(iso_datetime):
	return isodate.parse_datetime(iso_datetime)

def apply_colmap_dict(data, colmap, keep_other_columns=False):
	transformed_data = []

	for row in data:
		transformed_row = {}

		# Add original columns if selected
		if keep_other_columns:
			for col, value in row.items():
				if col not in colmap:
					transformed_row[col] = value

		for col, rules in colmap.items():
			# Check if column exists
			if col not in row:
				if rules.get('optional', False):
					continue
				else:
					raise KeyError(f"Missing required column: {col}")

			# Get the value from the row
			value = row[col]

			# Apply transformations
			if 'lambda' in rules:
				funcs = rules['lambda']
				if not isinstance(funcs, list):
					funcs = [funcs]
				for func in funcs:
					value = func(value)

			# Rename column
			new_col = rules.get('rename', col)
			transformed_row[new_col] = value

			# Drop old column
			if 'drop' in rules:
				del transformed_row[col]

		# Add transformed row to the list
		transformed_data.append(transformed_row)

	return transformed_data