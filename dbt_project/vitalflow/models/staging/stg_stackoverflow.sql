with source as (
    select * from {{ source('raw', 'stackoverflow_survey') }}
),

renamed as (
    select
        -- Identity
        ResponseId                          as response_id,

        -- Demographics
        Country                             as country,
        Age                                 as age,
        EdLevel                             as education_level,

        -- Employment
        Employment                          as employment_status,
        RemoteWork                          as remote_work,
        DevType                             as developer_type,
        OrgSize                             as org_size,
        YearsCode                           as years_coding,
        YearsCodePro                        as years_coding_professional,
        WorkExp                             as work_experience,
        Industry                            as industry,
        ICorPM                              as individual_contributor_or_manager,

        -- Compensation
        Currency                            as currency,
        CompTotal                           as compensation_total,
        ConvertedCompYearly                 as compensation_yearly_usd,

        -- Tech stack
        LanguageHaveWorkedWith              as languages_used,
        DatabaseHaveWorkedWith              as databases_used,
        PlatformHaveWorkedWith              as platforms_used,
        OpSysPersonal_use                   as os_personal,
        OpSysProfessional_use               as os_professional,

        -- AI
        AISelect                            as ai_usage,
        AISent                              as ai_sentiment,
        AIAcc                               as ai_accuracy,
        AIBen                               as ai_benefit,

        -- Stack Overflow
        SOVisitFreq                         as so_visit_frequency,
        SOAccount                           as so_has_account,
        SOComm                              as so_community_member,

        -- Survey metadata
        SurveyLength                        as survey_length_rating,
        SurveyEase                          as survey_ease_rating

    from source
)

select * from renamed