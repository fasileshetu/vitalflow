with stackoverflow as (
    select * from {{ ref('stg_stackoverflow') }}
),

final as (
    select
        -- Identity
        response_id,

        -- Demographics
        country,
        age,
        education_level,

        -- Employment
        employment_status,
        remote_work,
        developer_type,
        org_size,
        years_coding,
        years_coding_professional,
        work_experience,
        industry,
        individual_contributor_or_manager,

        -- Compensation
        compensation_yearly_usd,
        currency,

        -- Tech
        languages_used,
        databases_used,
        os_personal,
        os_professional,

        -- AI sentiment
        ai_usage,
        ai_sentiment,
        ai_accuracy,
        ai_benefit,

        -- Derived
        case
            when employment_status like '%full-time%' then 'full_time'
            when employment_status like '%part-time%' then 'part_time'
            when employment_status like '%freelance%' then 'freelance'
            else 'other'
        end as employment_category

    from stackoverflow
    where response_id is not null
)

select * from final