
from django.db import models

class Company(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField( unique=True)
    location = models.CharField(max_length=100)
    description = models.TextField()
    password_hash = models.CharField(max_length=100)
    last_login = models.DateTimeField(auto_now=True)

class Job(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    location = models.CharField(max_length=100)
    salary = models.CharField(max_length=100)
    posted_by = models.ForeignKey(Company, on_delete=models.CASCADE)
    date_posted = models.DateTimeField(auto_now_add=True)
    skills_required = models.CharField(max_length=500)
    eligibility_criteria = models.CharField(max_length=200)
    number_of_openings = models.IntegerField(default=0) 

class Recruiter(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField( unique=True)
    phone_number = models.CharField(max_length=20)
    password_hash = models.CharField(max_length=100)
    last_login = models.DateTimeField(auto_now=True)

class Resume(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    belongs_to_recruiter = models.ForeignKey(Recruiter, on_delete=models.CASCADE)
    file = models.FileField(upload_to='resumes/')


class Shortlisted(models.Model):
    job_post = models.ForeignKey(Job, on_delete=models.CASCADE)
    resume_id = models.ForeignKey(Resume, on_delete=models.CASCADE)
    resume_score = models.DecimalField(max_digits=15, decimal_places=5, default=0)
    email = models.CharField(max_length=254, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    resume_file = models.FileField(upload_to='shortlisted_resumes/', null=True, blank=True)
    Interview_Person = models.CharField(max_length=100,null=True,blank=True)
    Date = models.DateField(null=True,blank=True)
    Time = models.TimeField(null=True,blank=True)
    Status = models.CharField(max_length=100,null=True,blank=True,default="Pending")
    description = models.CharField(max_length=500,null=True,blank=True) 