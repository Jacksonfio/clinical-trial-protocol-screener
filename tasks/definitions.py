from pydantic import BaseModel
from env.models import Patient, Protocol

# compose tasks dictionary keyed by difficulty
TASKS = {
    'easy': {
        'protocol': Protocol(
            id='P001', name='Hypertension trial',
            inclusion=['hypertension'],
            exclusion=['diabetes'],
            required_labs={'creatinine': {'min': 0.5, 'max': 1.5}},
            banned_medications=['warfarin']
        ),
        'patients': [
            Patient(id='E1', age=45, sex='male', conditions=['hypertension'], medications=['lisinopril'], labs={'creatinine': 1.0}, consent_signed=True),
            Patient(id='E2', age=60, sex='female', conditions=['hypertension', 'diabetes'], medications=['metformin'], labs={'creatinine': 1.2}, consent_signed=True),
            Patient(id='E3', age=55, sex='female', conditions=['hypertension'], medications=['warfarin'], labs={'creatinine': 1.1}, consent_signed=True),
        ],
    },
    'medium': {
        'protocol': Protocol(
            id='P002', name='Heart Failure trial',
            inclusion=['heart_failure'],
            exclusion=['renal_failure', 'diabetes'],
            required_labs={'creatinine': {'min': 0.5, 'max': 1.4}, 'potassium': {'min': 3.5, 'max': 5.0}},
            banned_medications=['amiodarone']
        ),
        'patients': [
            Patient(id='M1', age=70, sex='male', conditions=['heart_failure'], medications=['lisinopril'], labs={'creatinine': 1.1, 'potassium': 4.5}, consent_signed=True),
            Patient(id='M2', age=67, sex='female', conditions=['heart_failure', 'renal_failure'], medications=['metoprolol'], labs={'creatinine': 1.6, 'potassium': 4.1}, consent_signed=True),
            Patient(id='M3', age=65, sex='female', conditions=['heart_failure'], medications=['amiodarone'], labs={'creatinine': 1.2, 'potassium': 4.8}, consent_signed=False),
        ]
    },
    'hard': {
        'protocol': Protocol(
            id='P003', name='Oncology immunotherapy',
            inclusion=['solid_tumor', 'measurable_disease'],
            exclusion=['autoimmune_disease', 'active_infection'],
            required_labs={
                'AST': {'min': 0.0, 'max': 40.0},
                'ALT': {'min': 0.0, 'max': 45.0},
                'neutrophils': {'min': 1.5, 'max': 8.0},
            },
            banned_medications=['systemic_steroids', 'cyclophosphamide']
        ),
        'patients': [
            Patient(id='H1', age=52, sex='male', conditions=['solid_tumor', 'measurable_disease'], medications=['aspirin'], labs={'AST': 30.0, 'ALT': 34.0, 'neutrophils': 3.2}, consent_signed=True),
            Patient(id='H2', age=58, sex='female', conditions=['solid_tumor', 'autoimmune_disease'], medications=['nsaids'], labs={'AST': 28.0, 'ALT': 40.0, 'neutrophils': 4.0}, consent_signed=True),
            Patient(id='H3', age=63, sex='male', conditions=['solid_tumor', 'measurable_disease', 'active_infection'], medications=['systemic_steroids'], labs={'AST': 25.0, 'ALT': 30.0, 'neutrophils': 2.0}, consent_signed=True),
        ]
    }
}
