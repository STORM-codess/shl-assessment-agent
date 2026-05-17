def format_assessment_context(
    retrieved_assessments
):

    formatted_text = ""

    for i, assessment in enumerate(
        retrieved_assessments,
        start=1
    ):

        # -----------------------------------
        # Format test types
        # -----------------------------------

        test_types = []

        for test_type in assessment.get(
            "test_types",
            []
        ):

            test_types.append(
                test_type.get(
                    "name",
                    ""
                )
            )

        test_types_text = ", ".join(
            test_types
        )

        # -----------------------------------
        # Format job levels
        # -----------------------------------

        job_levels_text = ", ".join(
            assessment.get(
                "job_levels",
                []
            )
        )

        # -----------------------------------
        # Build formatted context
        # -----------------------------------

        formatted_text += f"""

ASSESSMENT {i}

Name:
{assessment.get('name', '')}

Description:
{assessment.get('description', '')}

Assessment Types:
{test_types_text}

Supported Job Levels:
{job_levels_text}

Remote Testing:
{assessment.get('remote', 'unknown')}

Adaptive/IRT:
{assessment.get('adaptive', 'unknown')}

Catalog URL:
{assessment.get('url', '')}

--------------------------------------------------
"""

    return formatted_text