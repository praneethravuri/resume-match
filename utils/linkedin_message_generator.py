def generate_linkedin_message(company: str, job_title: str, job_id: str = "", recipient_name: str = "there") -> str:
    """
    Generate a LinkedIn message for a job application.

    Args:
        company (str): The company name.
        job_title (str): The job title.
        job_id (str, optional): The job identifier. Defaults to an empty string.
        recipient_name (str, optional): The recipient's name. Defaults to "there".

    Returns:
        str: The generated LinkedIn message.
    """
    job_id_text = f"(Job Id: {job_id})" if job_id else ""
    message = (
        f"Hi {recipient_name}, I'm a Software Engineer at Prodapt in Dallas exploring new opportunities and "
        f"wanted to connect regarding the {job_title} position {job_id_text} at {company}. Please take a look at my profile—"
        " I'd love to discuss how my skills could be a great fit. Thank you!"
    )
    return message
