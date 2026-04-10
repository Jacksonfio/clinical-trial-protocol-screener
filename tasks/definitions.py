from env.models import Patient, Protocol

# ─────────────────────────────────────────────
# TASK DEFINITIONS  (Easy → Medium → Hard → Expert)
# Each task has 5 carefully crafted edge-case patients
# ─────────────────────────────────────────────

TASKS = {

    # ──────────────────────────────────────────
    # EASY: Hypertension Trial
    # Tests basic 1-2 boolean inclusion/exclusion checks
    # ──────────────────────────────────────────
    'easy': {
        'protocol': Protocol(
            id='P001',
            name='Hypertension Cardiovascular Study',
            inclusion=['hypertension'],
            exclusion=['diabetes', 'chronic_kidney_disease'],
            required_labs={'creatinine': {'min': 0.5, 'max': 1.5}},
            banned_medications=['warfarin'],
        ),
        'patients': [
            # E1: Clear approve — hypertension, clean labs, no exclusions
            Patient(id='E1', age=45, sex='male',
                    conditions=['hypertension'],
                    medications=['lisinopril'],
                    labs={'creatinine': 1.0},
                    consent_signed=True),
            # E2: Reject — has diabetes (exclusion criterion)
            Patient(id='E2', age=60, sex='female',
                    conditions=['hypertension', 'diabetes'],
                    medications=['metformin'],
                    labs={'creatinine': 1.2},
                    consent_signed=True),
            # E3: Reject — warfarin is a banned medication
            Patient(id='E3', age=55, sex='female',
                    conditions=['hypertension'],
                    medications=['warfarin', 'amlodipine'],
                    labs={'creatinine': 1.1},
                    consent_signed=True),
            # E4: Reject — no consent signed
            Patient(id='E4', age=50, sex='male',
                    conditions=['hypertension'],
                    medications=['atenolol'],
                    labs={'creatinine': 0.9},
                    consent_signed=False),
            # E5: Request more info — creatinine lab missing
            Patient(id='E5', age=62, sex='female',
                    conditions=['hypertension'],
                    medications=['amlodipine'],
                    labs={},
                    consent_signed=True),
        ],
    },

    # ──────────────────────────────────────────
    # MEDIUM: Heart Failure Trial
    # Tests 7+ multi-variable lab bounds + medication exclusions
    # ──────────────────────────────────────────
    'medium': {
        'protocol': Protocol(
            id='P002',
            name='Heart Failure Carvedilol Extension Trial',
            inclusion=['heart_failure'],
            exclusion=['renal_failure', 'diabetes'],
            required_labs={
                'creatinine': {'min': 0.5, 'max': 1.4},
                'potassium': {'min': 3.5, 'max': 5.0},
                'BNP': {'min': 0.0, 'max': 400.0},
            },
            banned_medications=['amiodarone', 'digoxin'],
            drug_interactions=[
                ['carvedilol', 'verapamil'],  # combined beta-blockade + Ca-channel block = contraindicated
            ],
        ),
        'patients': [
            # M1: Clear approve — heart failure, all labs in range, no exclusions
            Patient(id='M1', age=70, sex='male',
                    conditions=['heart_failure'],
                    medications=['lisinopril', 'furosemide'],
                    labs={'creatinine': 1.1, 'potassium': 4.5, 'BNP': 300.0},
                    consent_signed=True),
            # M2: Reject — renal_failure (exclusion) + creatinine out of range
            Patient(id='M2', age=67, sex='female',
                    conditions=['heart_failure', 'renal_failure'],
                    medications=['metoprolol'],
                    labs={'creatinine': 1.6, 'potassium': 4.1, 'BNP': 350.0},
                    consent_signed=True),
            # M3: Reject — consent not signed + amiodarone (banned)
            Patient(id='M3', age=65, sex='female',
                    conditions=['heart_failure'],
                    medications=['amiodarone'],
                    labs={'creatinine': 1.2, 'potassium': 4.8, 'BNP': 290.0},
                    consent_signed=False),
            # M4: Reject — drug-drug interaction: carvedilol + verapamil
            Patient(id='M4', age=72, sex='male',
                    conditions=['heart_failure'],
                    medications=['carvedilol', 'verapamil'],
                    labs={'creatinine': 1.0, 'potassium': 4.2, 'BNP': 310.0},
                    consent_signed=True),
            # M5: Request more info — BNP lab is missing
            Patient(id='M5', age=68, sex='female',
                    conditions=['heart_failure'],
                    medications=['lisinopril'],
                    labs={'creatinine': 1.3, 'potassium': 4.0},
                    consent_signed=True),
        ],
    },

    # ──────────────────────────────────────────
    # HARD: Oncology Immunotherapy Trial
    # Tests 15+ variables, organ-level lab checks, complex medication contraindications
    # ──────────────────────────────────────────
    'hard': {
        'protocol': Protocol(
            id='P003',
            name='PD-L1 Inhibitor Immunotherapy Phase II',
            inclusion=['solid_tumor', 'measurable_disease'],
            exclusion=['autoimmune_disease', 'active_infection', 'liver_metastasis'],
            required_labs={
                'AST': {'min': 0.0, 'max': 40.0},
                'ALT': {'min': 0.0, 'max': 45.0},
                'neutrophils': {'min': 1.5, 'max': 8.0},
                'hemoglobin': {'min': 9.0, 'max': 18.0},
                'platelets': {'min': 100.0, 'max': 600.0},
            },
            banned_medications=['systemic_steroids', 'cyclophosphamide', 'rituximab'],
            drug_interactions=[
                ['immunotherapy', 'systemic_steroids'],  # steroids ablate immunotherapy efficacy
            ],
        ),
        'patients': [
            # H1: Clear approve — solid tumor, all labs clean, no contraindications
            Patient(id='H1', age=52, sex='male',
                    conditions=['solid_tumor', 'measurable_disease'],
                    medications=['aspirin', 'ondansetron'],
                    labs={'AST': 30.0, 'ALT': 34.0, 'neutrophils': 3.2,
                          'hemoglobin': 12.5, 'platelets': 230.0},
                    consent_signed=True),
            # H2: Reject — autoimmune_disease exclusion
            Patient(id='H2', age=58, sex='female',
                    conditions=['solid_tumor', 'autoimmune_disease'],
                    medications=['nsaids'],
                    labs={'AST': 28.0, 'ALT': 40.0, 'neutrophils': 4.0,
                          'hemoglobin': 11.0, 'platelets': 280.0},
                    consent_signed=True),
            # H3: Reject — active_infection + systemic_steroids (banned)
            Patient(id='H3', age=63, sex='male',
                    conditions=['solid_tumor', 'measurable_disease', 'active_infection'],
                    medications=['systemic_steroids'],
                    labs={'AST': 25.0, 'ALT': 30.0, 'neutrophils': 2.0,
                          'hemoglobin': 10.5, 'platelets': 190.0},
                    consent_signed=True),
            # H4: Reject — platelets dangerously low (out of range)
            Patient(id='H4', age=47, sex='female',
                    conditions=['solid_tumor', 'measurable_disease'],
                    medications=['ondansetron'],
                    labs={'AST': 35.0, 'ALT': 42.0, 'neutrophils': 2.8,
                          'hemoglobin': 11.5, 'platelets': 75.0},
                    consent_signed=True),
            # H5: Request more info — platelets and hemoglobin missing
            Patient(id='H5', age=55, sex='male',
                    conditions=['solid_tumor', 'measurable_disease'],
                    medications=['aspirin'],
                    labs={'AST': 28.0, 'ALT': 36.0, 'neutrophils': 3.5},
                    consent_signed=True),
        ],
    },

    # ──────────────────────────────────────────
    # EXPERT: Rare Disease Gene Therapy Trial
    # Tests IMPLICIT reasoning — the condition name is NEVER given.
    # The agent must infer exclusions from raw lab values using medical knowledge.
    # e.g. eGFR=22 → must infer "severe renal impairment" without being told.
    # ──────────────────────────────────────────
    'expert': {
        'protocol': Protocol(
            id='P004',
            name='AAV9 Gene Therapy for Spinal Muscular Atrophy',
            inclusion=['spinal_muscular_atrophy', 'age_under_2_years'],
            exclusion=['severe_renal_impairment', 'hepatic_dysfunction', 'active_viral_infection'],
            required_labs={
                # eGFR < 30 indicates severe renal impairment → reject
                'eGFR': {'min': 30.0, 'max': 120.0},
                # ALT > 3x upper limit of normal (45) = hepatic dysfunction → reject
                'ALT': {'min': 0.0, 'max': 135.0},
                'AST': {'min': 0.0, 'max': 120.0},
                # Low viral titer confirms no active AAV antibodies
                'AAV9_antibody_titer': {'min': 0.0, 'max': 1.0},
            },
            banned_medications=['nusinersen', 'risdiplam'],  # competing SMA therapies
            implicit_exclusion_labs={
                # eGFR below this means "severe renal impairment" even if not labelled
                'eGFR': {'max_for_exclusion': 30.0},
                # ALT above this means "hepatic dysfunction" even if not labelled
                'ALT': {'max_for_exclusion': 135.0},
            },
        ),
        'patients': [
            # X1: Approve — SMA confirmed, infant age, all labs clean, no competing therapy
            Patient(id='X1', age=1, sex='female',
                    conditions=['spinal_muscular_atrophy', 'age_under_2_years'],
                    medications=['riboflavin'],
                    labs={'eGFR': 85.0, 'ALT': 22.0, 'AST': 18.0, 'AAV9_antibody_titer': 0.2},
                    consent_signed=True),
            # X2: Reject — eGFR=22 → must INFER severe renal impairment without being told
            Patient(id='X2', age=1, sex='male',
                    conditions=['spinal_muscular_atrophy', 'age_under_2_years'],
                    medications=['riboflavin'],
                    labs={'eGFR': 22.0, 'ALT': 30.0, 'AST': 25.0, 'AAV9_antibody_titer': 0.3},
                    consent_signed=True),
            # X3: Reject — AAV9 antibody titer=3.2 → active viral antibodies, cannot receive gene therapy
            Patient(id='X3', age=0, sex='male',
                    conditions=['spinal_muscular_atrophy', 'age_under_2_years'],
                    medications=[],
                    labs={'eGFR': 90.0, 'ALT': 18.0, 'AST': 15.0, 'AAV9_antibody_titer': 3.2},
                    consent_signed=True),
            # X4: Reject — on nusinersen (banned competing SMA therapy)
            Patient(id='X4', age=1, sex='female',
                    conditions=['spinal_muscular_atrophy', 'age_under_2_years'],
                    medications=['nusinersen'],
                    labs={'eGFR': 75.0, 'ALT': 25.0, 'AST': 20.0, 'AAV9_antibody_titer': 0.1},
                    consent_signed=True),
            # X5: Request more info — AAV9 antibody titer not tested yet (missing)
            Patient(id='X5', age=1, sex='male',
                    conditions=['spinal_muscular_atrophy', 'age_under_2_years'],
                    medications=['riboflavin'],
                    labs={'eGFR': 82.0, 'ALT': 28.0, 'AST': 22.0},
                    consent_signed=True),
        ],
    },
}
