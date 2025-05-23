import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
django.setup()

from django.core.mail import EmailMultiAlternatives

from jobs.models import Job
from profiles.models import TalentProfile

# helpful resource : 
# https://docs.djangoproject.com/en/5.2/topics/email/

# email setup is in settings.py 


def render_template(filename, context):
    # Load html
    base_dir = os.path.dirname(os.path.dirname(__file__)) 
    template_path = os.path.join(base_dir, 'templates', filename)

    with open(template_path, 'r') as f:
        content = f.read()

    for key, value in context.items():
        content = content.replace(f'{{{{ {key} }}}}', value)
    return content

def send_calendly_invite(email, name, job_title, calendly_link):
    subject = "📅 Schedule Your Screening Interview with Pairwise AI!"

    from_email = None
    to = [email]

    text_content = f"Hi {name}, thanks for you interest in {job_title} position. please schedule your screening interview with PAIRWISE here: {calendly_link}"
    html_content = render_template("calendly_invite.html", {"name": name, "job" : job_title, "link": calendly_link})

    msg = EmailMultiAlternatives(subject, text_content, from_email, to)
    msg.attach_alternative(html_content, "text/html")
    msg.send()

    print(f"✅ Sent email to {email}")

if __name__ == "__main__":

    rand_job = Job.objects.order_by('?').first()
    rand_talent = TalentProfile.objects.order_by('?').first()

    candidate_fullname = rand_talent.user.first_name + " " + rand_talent.user.last_name
    job_title = rand_job.title 


    # DO NOT UNCOMMENT
    # TO GET CANDIDATE EMAIL FROM DB: 
    ####### candidate_email = rand_talent.user.email


    candidate_email = "PUT_CANDIDATE_EMAIL_HERE"

    calendly_link = "CALENDLY_LINK_HERE"


    send_calendly_invite (email= candidate_email ,
                          name=candidate_fullname,
                          job_title = job_title,
                          calendly_link= calendly_link )

