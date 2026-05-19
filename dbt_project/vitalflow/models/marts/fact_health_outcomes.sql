with brfss as (
    select * from {{ ref('stg_brfss') }}
),

final as (
    select
        -- Demographics
        state_code,
        interview_date,
        sex,
        age_group,
        education,
        income,

        -- Health outcomes
        general_health,
        physical_health_days,
        mental_health_days,
        bmi_category,
        diabetes,
        heart_disease,
        asthma,

        -- Behaviors
        exercise,
        smoking_status,

        -- Health risk score (simple composite)
        case
            when general_health in ('1', '2') then 'low_risk'
            when general_health = '3' then 'medium_risk'
            when general_health in ('4', '5') then 'high_risk'
            else 'unknown'
        end as health_risk_segment

    from brfss
    where general_health is not null
        and general_health != '9'
        and general_health != '7'
)

select * from final