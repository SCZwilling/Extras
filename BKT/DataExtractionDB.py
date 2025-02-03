import psycopg2
import os
# import csv
# from datetime import datetime, timedelta

def export_data_by_day(db_params, table, time_since, directory):
    # Query to get distinct dates
    get_dates_query = f"SELECT DISTINCT DATE(time) AS day FROM {table} where time>{time_since} ORDER BY day;"

    # Query to get data for a specific date
    get_data_query_template = f"""
    COPY (
        SELECT * FROM {table}
        WHERE DATE(time) = '%s'
    ) TO STDOUT WITH CSV HEADER;
    """
    print(f"Exporting data for {table}...")
    try:
        # Connect to the database
        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor()
        
        # Fetch distinct dates
        cursor.execute(get_dates_query)
        dates = cursor.fetchall()  # List of tuples, e.g., [(date1,), (date2,), ...]

        # Iterate over dates and export data
        for date_tuple in dates:
            date_str = date_tuple[0].strftime('%Y-%m-%d')
            file_name = os.path.join(directory, f"{date_str}.csv")
            
            get_data_query = get_data_query_template % date_str
            
            with open(file_name, 'w') as f:
                cursor.copy_expert(get_data_query, f)
            print(f"Data for {date_str} exported to {file_name}.")
        
    except Exception as e:
        print("Error:", e)
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    # Database connection parameters
    db_params = {
        'dbname': 'bkt',
        'user': 'user',
        'password': 'pass',
        'host': '43.205.149.35',
        'port': '5432'
    }
    export_data_by_day(db_params, "tpms", "'2024-12-01 00:00:00'", "TPMS")
    export_data_by_day(db_params, "gps", "'2024-12-01 00:00:00'", "GPS")
    export_data_by_day(db_params, "height", "'2024-12-01 00:00:00'", "Height")
    export_data_by_day(db_params, "rpm", "'2024-12-01 00:00:00'", "RPM")
    
