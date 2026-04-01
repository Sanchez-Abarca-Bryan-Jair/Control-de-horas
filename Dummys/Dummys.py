import pandas as pd
import random
from datetime import datetime, timedelta

# Parameters
employees = ['AV9029','BE3019','CD0001','CD0002','DR8901','RH8901','V09973','V56718','V83021','V89890']

justifications = [
    'Requerimiento del almacen',
    'Requerimiento de proyectos',
    'Operacion de Emergencia',
    'Voluntariado',
    'Revision de inventario trimestral',
    'AOG de ultimo momento',
    'Capacitacion',
    'Mantenimiento',
    'Reunion de proyectos'
]

# Generate 800 records
records = []
start_date = datetime(2024, 1, 1)
end_date = datetime(2026, 4, 30)

for _ in range(2000):
    employee = random.choice(employees)
    hours = random.choice([1, 1, 2, 2, 2, 3, 3, 4, 5])  # Weighted toward 2-3 hours
    justification = random.choice(justifications)
    
    # Random date within range
    random_days = random.randint(0, (end_date - start_date).days)
    record_date = start_date + timedelta(days=random_days)
    
    # Add random time
    record_datetime = record_date.replace(
        hour=random.randint(8, 18),
        minute=random.randint(0, 59),
        second=random.randint(0, 59),
        microsecond=random.randint(0, 999999)
    )
    
    records.append({
        'empleado_num': employee,
        'cantidad_horas': hours,
        'justificacion': justification,
        'fecha_registro': record_datetime
    })

# Create DataFrame
df = pd.DataFrame(records)

# Export to CSV (for bulk insert)
df.to_csv('dummy_registros_tiempo.csv', index=False)

# Or generate SQL INSERT statements
sql_statements = []
for _, row in df.iterrows():
    sql = f"""INSERT INTO horas_extra (empleado_num, cantidad_horas, justificacion, fecha_registro) 
VALUES ('{row['empleado_num']}', {row['cantidad_horas']}, '{row['justificacion']}', '{row['fecha_registro'].isoformat()}');"""
    sql_statements.append(sql)

with open('insert_registros.sql', 'w') as f:
    f.write('\n'.join(sql_statements))

print(f"Generated {len(records)} dummy records")