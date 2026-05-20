with source as (
    select * from {{ source('raw', 'brfss_2023') }}
),

renamed as (
    select
        state_code,
        interview_year,
        sex,
        age_group,
        education,
        income,
        general_health,
        physical_health_days,
        mental_health_days,
        exercise,
        smoking_status,
        bmi_category,
        bmi,
        diabetes,
        heart_disease,
        asthma,
        race
    from source
)

select * from renamed