from datetime import datetime
def get_studies_metadata(studies):
    results = []
    for study in studies:
        study_description = ""
        patient_name = ""
        patient_id = ""
        modality = ""
        study_id = ""
        study_date = ""
        study_time = ""
        patients_age = ""
        for series in study:
            for instance in series:
                study_description = instance.StudyDescription
                patient_name = instance.PatientName
                patient_id = instance.PatientID
                modality = instance.Modality
                study_id = instance.StudyID
                study_date = instance.StudyDate
                study_time = instance.StudyTime
                # patients_age = instance.PatientsAge
        results.append({
            "study_description": str(study_description),
            "patient_name": str(patient_name),
            "patient_id": str(patient_id),
            "modality": str(modality),
            "study_id": str(study_id),
            "study_date": f"{datetime.strptime(study_date, '%Y%m%d'):%d-%m-%Y}",
            "study_time": f"{datetime.strptime(study_time, '%H%M%S.%f'):%H:%M:%S}",
            # "patients_age": str(patients_age)
        })
    return results