from django.shortcuts import render, redirect , get_object_or_404
from django.contrib import messages
from .models import *
from django.contrib.auth import authenticate, login
from django.contrib.auth.hashers import make_password,check_password
from django.db.models import Q
from .utils import *
from django.core.mail import send_mail, BadHeaderError
from django.shortcuts import redirect, render
from django.http import FileResponse, Http404
from wsgiref.util import FileWrapper
from django.conf import settings
import os
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core import signing


def cleanup_messages(request):
    storage = messages.get_messages(request)
    storage.used = True  # Marks all messages as used

# Create your views here.
def home(request):
    return render(request,'landing_page.html')
def about_us(request):
    return render(request,'about_us.html')

def company_reg(request):
    context = {}
    if request.method == 'POST':
        # get form data
        name = request.POST.get('name')
        email = request.POST.get('email')
        location = request.POST.get('location')
        description = request.POST.get('description')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        # check if password and confirm_password matches
        if password != confirm_password:
            context = {'error_message': 'Passwords do not match'}
        
        # check if email already exists in database
        elif Company.objects.filter(email=email).exists():
            context = {'error_message': 'Email Already Exists'}
        
        else:
            final_password = make_password(password)
            company = Company(name=name, email=email, location=location, description=description , password_hash = final_password )

            company.save()
            messages.success(request, 'Company registered successfully')
            return redirect('company_log')
    
    return render(request, 'company_register.html',context)






def company_log(request):
    context = {}

    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        
        try:
            company = Company.objects.get(email=email)
            if check_password(password, company.password_hash):
                request.session['company_id'] = company.id
                return redirect('company_home')
            else:
                context = {'error_message': 'Invalid login credentials. Please try again.'}
        except Company.DoesNotExist:
            context = {'error_message': 'Invalid login credentials. Please try again.'}
    
    return render(request, 'company_login.html',context)



# company password reset 
def company_forgot_password(request):
    if request.method == 'POST':
        email = request.POST['email']
        try:
            company = Company.objects.get(email=email)
        except Company.DoesNotExist:
            messages.error(request, 'Invalid email. Please try again.')
            return redirect('company_forgot_password')

        token = company.id 

        reset_link = f"{settings.BASE_URL}/company/reset_password/{token}/"

        # Send the password reset email
        subject = 'Reset Your Password HireEase Team'
        message = f"Hi {company.name},\n\n" \
          f"You have requested to reset your password.\n" \
          f"Please click the following link to reset your password:\n\n" \
          f"{reset_link}\n\n" \
          f"If you did not request a password reset, please ignore this email.\n\n" \
          f"Best regards,\n" \
          f"The HireEase Team"

        send_mail(subject, message, settings.EMAIL_HOST_USER, [company.email])

        messages.success(request, 'Password reset instructions have been sent to your email.')

    return render(request, 'forgot_pass_company.html')



def company_reset_password(request, token):
    company = Company.objects.get(id = token)

    if request.method == 'POST':
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']
        email = request.POST['email']
        
        if new_password == confirm_password:
            if email == company.email:
                # Update the company's password
                company.password_hash = make_password(new_password)   
                company.save()
                messages.success(request, 'Your password has been reset. You can now log in with your new password.')
                return redirect('company_log')
            else:
                messages.error(request, 'Invalid email. Please try again.')
                return redirect('company_reset_password', token=token)
        else:
            messages.error(request, 'Passwords do not match. Please try again.')
            return redirect('company_reset_password', token=token)

    return render(request, 'reset_password_company.html')



def company_logout(request):
    request.session.flush()
    return redirect('company_log')



def company_home(request):

    company_id = request.session.get('company_id')
    if not company_id:
        return redirect('company_login')

    company = get_object_or_404(Company, pk=company_id)
    posts = Job.objects.filter(posted_by=company)
    
    context = {
        'company': company,
        'posts': posts,
    }
    
    return render(request,'company_templates/company_dashboard.html',context) 




def company_profile(request):

    company_id = request.session.get('company_id', None)
    company = Company.objects.get(id=company_id)
    context = {'company':company}
    
    if request.method == 'POST':
        
        name = request.POST.get('name')
        location = request.POST.get('location')
        description = request.POST.get('description')

        # Updating
        company.name = name
        company.location = location
        company.description = description
        company.save()
        
    return render(request,'company_templates/company_profile.html',context) 





def create_job_post(request):

    company_id = request.session.get('company_id', None)
    company = Company.objects.get(id=company_id)
    context = {'company':company}

    if request.method == 'POST':
        print(company_id)
        title = request.POST.get('title')
        description = request.POST.get('description')
        location = request.POST.get('location')
        salary = request.POST.get('salary')
        skills_required = request.POST.get('skills_required')
        eligibility_criteria = request.POST.get('eligibility_criteria')
        number_of_openings = request.POST.get('number_of_openings')

        job = Job(title=title, description=description, location=location, salary=salary, skills_required=skills_required, eligibility_criteria=eligibility_criteria,number_of_openings=number_of_openings ,posted_by=company)
        job.save()

        messages.success(request, 'Job posted successfully!')
        return redirect('create_job_post')
        
    return render(request,'company_templates/create_post.html') 





def my_posts(request):
    company_id = request.session.get('company_id')
    if not company_id:
        return redirect('company_login')

    company = get_object_or_404(Company, pk=company_id)
    job_posts = Job.objects.filter(posted_by=company_id)

    context = {
        'company': company,
        'job_posts': job_posts
    }

    # Delete
    if request.method == 'POST':
        job_post_id = request.POST.get('job_post_id')
        try:
            job_post = Job.objects.get(id=job_post_id, posted_by=company)
            job_post.delete()
            messages.success(request, 'Job post deleted successfully.')
        except Job.DoesNotExist:
            messages.error(request, 'Invalid job post id.')
    
    return render(request,'company_templates/company_posts.html',context) 




def update_job_post(request,job_post_id):
    company_id = request.session.get('company_id')
    if not company_id:
        return redirect('company_login')

    company = get_object_or_404(Company, pk=company_id)
    
    job_post = Job.objects.get(id=job_post_id, posted_by=company)

    if request.method == 'POST':
        job_post.title = request.POST.get('title')
        job_post.description = request.POST.get('description')
        job_post.location = request.POST.get('location')
        job_post.salary = request.POST.get('salary')
        job_post.skills_required = request.POST.get('skills_required')
        job_post.eligibility_criteria = request.POST.get('eligibility_criteria')
        job_post.number_of_openings = request.POST.get('number_of_openings')
        job_post.save()
        messages.success(request, 'Job Post updated successfully!')
        return redirect('my_posts')
    
    context = {
        'job_post': job_post
    }
    return render(request,'company_templates/update_post.html',context)



# //////////


def view_responses(request, job_post_id):
    company_id = request.session.get('company_id')
    if not company_id:
        return redirect('company_login')

    company = get_object_or_404(Company, pk=company_id)
    print(company.name)
    job_post = Job.objects.get(id=job_post_id, posted_by=company)

    shortlisted_resumes = Shortlisted.objects.filter(job_post=job_post).order_by('-resume_score')[:job_post.number_of_openings]

    
    context = {
        'job_post': job_post,
        'shortlisted_resumes': shortlisted_resumes,
    }

    if request.method == 'POST':
            email = request.POST.get('email')
            schedule =  get_object_or_404(Shortlisted, email=email)
            print(schedule)
            schedule.Interview_Person = request.POST.get('Iname')
            schedule.Date = request.POST.get('date')
            schedule.Time = request.POST.get('time')
            schedule.description = request.POST.get('description')
            schedule.Status = "Completed"
            schedule.save()
            #sending email

            subject = 'Are You Ready For Next Round ?'
            html_message = render_to_string('email.html', {'context_variable': {'date': schedule.Date, 'time': schedule.Time, 'description': schedule.description , 'comp_name':company.name}})

            plain_message = strip_tags(html_message)
            from_email = 'pccshireease@gmail.com'
            to_email = [email, email]
            send_mail(subject, plain_message, from_email, to_email, html_message=html_message)
            messages.success(request, 'Further Round scheduled successfully')

    return render(request, 'company_templates/responseToPosts.html', context)

# Recruiter views


# recruiter password reset 
def rec_forgot_password(request):
    if request.method == 'POST':
        email = request.POST['email']
        try:
            recruiter = Recruiter.objects.get(email=email)
        except Company.DoesNotExist:
            messages.error(request, 'Invalid email. Please try again.')
            return redirect('rec_forgot_password')

        token = recruiter.id 

        reset_link = f"{settings.BASE_URL}/rec/reset_password/{token}/"

        # Send the password reset email
        subject = 'Reset Your Password HireEase Team'
        message = f"Hi {recruiter.name},\n\n" \
          f"You have requested to reset your password.\n" \
          f"Please click the following link to reset your password:\n\n" \
          f"{reset_link}\n\n" \
          f"If you did not request a password reset, please ignore this email.\n\n" \
          f"Best regards,\n" \
          f"The HireEase Team"

        send_mail(subject, message, settings.EMAIL_HOST_USER, [recruiter.email])

        messages.success(request, 'Password reset instructions have been sent to your email.')

    return render(request, 'forgot_pass_recruiter.html')



def rec_reset_password(request, token):
    recruiter = Recruiter.objects.get(id = token)

    if request.method == 'POST':
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']
        email = request.POST['email']
        
        if new_password == confirm_password:
            if email == recruiter.email:
                # Update the company's password
                recruiter.password_hash = make_password(new_password)   
                recruiter.save()
                messages.success(request, 'Your password has been reset. You can now log in with your new password.')
                return redirect('recruiter_log')
            else:
                messages.error(request, 'Invalid email. Please try again.')
                return redirect('rec_reset_password', token=token)
        else:
            messages.error(request, 'Passwords do not match. Please try again.')
            return redirect('rec_reset_password', token=token)

    return render(request, 'reset_password_recruiter.html')




def recruiter_reg(request):
    context = {}

    if request.method == 'POST':
        # get form data
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        # check if password and confirm_password matches
        if password != confirm_password:
           context = {'error_message': "Password Not Matched"}
        
        # check if email already exists in database
        elif Recruiter.objects.filter(email=email).exists():
            context = {'error_message': "Email Already Exists"}
            
        # create company object
        else :
            final_password = make_password(password)
            recruiter = Recruiter(name=name, email=email,phone_number=phone_number, password_hash = final_password )

            recruiter.save()
            messages.success(request, 'Recruiter registered successfully')
            return redirect('recruiter_log')
    
    return render(request, 'recruiter_register.html', context)
    



def recruiter_log(request):
    context = {}

    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        
        try:
            recruiter = Recruiter.objects.get(email=email)
            if check_password(password, recruiter.password_hash):
                # If the password is correct, log the company in
                request.session['recruiter_id'] = recruiter.id
                return redirect('rec_home')
            else:
                context = {'error_message': 'Invalid login credentials. Please try again.'}
        except Recruiter.DoesNotExist:
            context = {'error_message': 'Invalid login credentials. Please try again.'}
    
    return render(request, 'recruiter_login.html',context)


def rec_logout(request):
    request.session.flush()
    return redirect('recruiter_log')


def rec_home(request):
    recruiter_id = request.session.get('recruiter_id')
    if not recruiter_id:
        return redirect('recruiter_log')

    recruiter = get_object_or_404(Recruiter, pk=recruiter_id)
    
    resumes = Resume.objects.filter(belongs_to_recruiter=recruiter)
    resume_count = resumes.count()
    
    shortlists = Shortlisted.objects.filter(resume_id__belongs_to_recruiter=recruiter)

    shortlisted_resumes_count = shortlists.count()

    pending_count = shortlists.filter(Status='Pending').count()
    completed_count = shortlists.filter(Status='Completed').count()

    context = {
        'recruiter': recruiter,
        'resume_count': resume_count,
        'shortlisted_count' : shortlisted_resumes_count,
        'pending_count': pending_count,
        'completed_count': completed_count,
    }
    
    return render(request,'recruiter_templates/recruiter_dashboard.html',context) 


def rec_profile(request):

    recruiter_id = request.session.get('recruiter_id')
    if not recruiter_id:
        return redirect('recruiter_log')
    
    recruiter = Recruiter.objects.get(id=recruiter_id)

    context = {'recruiter':recruiter}
    
    if request.method == 'POST':
        
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone_number')

        # Updating
        recruiter.name = name
        recruiter.email = email
        recruiter.phone_number = phone
        recruiter.save()
        
    return render(request,'recruiter_templates/recruiter_profile.html',context)


def all_jobs(request):
    recruiter_id = request.session.get('recruiter_id')
    if not recruiter_id:
        return redirect('recruiter_log')
    
    jobs = Job.objects.all()

    query = request.GET.get('q')
    if query:
        jobs = jobs.filter(Q(title__icontains=query))

    context = {
        'jobs': jobs
    }
    return render(request, 'recruiter_templates/all_jobs.html', context)


def search_job(request):
    if request.method == 'GET':
        keyword = request.GET.get('q')
        if keyword:
            jobs = Job.objects.filter(title__icontains=keyword)
            return render(request, 'recruiter_templates/search_results.html', {'jobs': jobs,'keyword':keyword})
    return render(request, 'recruiter_templates/search_results.html')


def job_detail(request,job_id):
    job = get_object_or_404(Job, id=job_id)
    return render(request, 'recruiter_templates/job_detail.html', {'job': job})



def upload_resumes(request):
    recruiter_id = request.session.get('recruiter_id')
    if not recruiter_id:
        return redirect('recruiter_log')

    recruiter = Recruiter.objects.get(id=recruiter_id)

    resumes = Resume.objects.filter(belongs_to_recruiter=recruiter)

    context = {'resumes': resumes}

    if request.method == 'POST':
        files = request.FILES.getlist('resume')  # Get a list of uploaded files
        for file in files:
            name = file.name  # Get the name of each uploaded file
            resume = Resume(belongs_to_recruiter=recruiter, name=name, file=file)
            resume.save()
        return redirect('upload_resumes')

    return render(request, 'recruiter_templates/upload_resumes.html', context)




def delete_resume(request,resume_id):
    resume = Resume.objects.get(id=resume_id)
    resume.delete()
    messages.success(request, 'Resume deleted successfully')

    return redirect('upload_resumes')




def send_resumes(request, job_id):

    recruiter_id = request.session.get('recruiter_id')
    if not recruiter_id:
        return redirect('recruiter_log')

    recruiter = Recruiter.objects.get(id=recruiter_id)

    resumes = Resume.objects.filter(belongs_to_recruiter=recruiter)

    if request.method == 'POST':
        job = Job.objects.get(pk=job_id)

        for resume in resumes:
            # Extract skills from the resume file
            resume_file = resume.file.path
            resume_text = extract_text_from_pdf(resume_file)
            # resume_skills = extract_skills(resume_text)
            contact_details = extract_contact_details(resume_text)
            
            # Calculate the score
            # common_skills = set(resume_skills).intersection(set(job_skills))
            score = extract_skills_with_score(resume_text,job.skills_required)
            score = round(score,3)
            
            # Check if the resume has already been shortlisted
            shortlist, created = Shortlisted.objects.get_or_create(job_post=job, resume_id=resume)

            shortlist.resume_file = resume_file
            shortlist.resume_score = score
            shortlist.email = contact_details.get('email')[0] ;
            # print(contact_details.get('email')[0])
            shortlist.phone_number = contact_details.get('phone')[0] ;
            # print(contact_details.get('phone')[0])
            shortlist.save()

        messages.success(request, 'Resumes sent successfully')
        return redirect('job_detail', job_id=job_id)

    return render(request, 'recruiter_templates/job_detail.html', {'job': job})


def candidates_per_job(request):
    recruiter_id = request.session.get('recruiter_id')
    if not recruiter_id:
        return redirect('recruiter_log')

    recruiter = Recruiter.objects.get(id=recruiter_id)

    shortlisted_resumes = Shortlisted.objects.filter(resume_id__belongs_to_recruiter=recruiter)

    context = {
        'shortlisted' : shortlisted_resumes,
    }
    return render(request, 'recruiter_templates/candidates_per_job.html',context)


def download_resume(request, filename):
    resume_path = os.path.join(settings.MEDIA_ROOT, 'resumes', filename)
    if os.path.exists(resume_path):
        file_wrapper = FileWrapper(open(resume_path, 'rb'))
        response = FileResponse(file_wrapper, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename=' + os.path.basename(resume_path)
        return response
    else:
        raise Http404("Resume not found")
    






