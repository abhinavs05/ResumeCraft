from django.db import models
from django.contrib.auth.models import User

class Resume(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='resumes')
    title = models.CharField(max_length=200, default="My Resume")
    template_name = models.CharField(max_length=50, default='jakes')  # jakes, modern, creative, corporate, academic
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} ({self.user.username})"

class PersonalInfo(models.Model):
    resume = models.OneToOneField(Resume, on_delete=models.CASCADE, related_name='personal_info')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=50, blank=True, null=True)
    location = models.CharField(max_length=200, blank=True, null=True)  # e.g., "New Delhi, India"
    website = models.URLField(blank=True, null=True)
    github = models.URLField(blank=True, null=True)
    linkedin = models.URLField(blank=True, null=True)
    portfolio = models.URLField(blank=True, null=True)
    summary = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Education(models.Model):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='educations')
    institution = models.CharField(max_length=200)
    degree = models.CharField(max_length=200)
    major = models.CharField(max_length=200, blank=True, null=True)
    gpa = models.CharField(max_length=50, blank=True, null=True)
    location = models.CharField(max_length=200, blank=True, null=True)
    start_date = models.CharField(max_length=50, blank=True, null=True)
    end_date = models.CharField(max_length=50, blank=True, null=True)
    is_current = models.BooleanField(default=False)
    description = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f"{self.degree} at {self.institution}"

    @property
    def bullets(self):
        if not self.description:
            return []
        return [line.strip().lstrip('-').lstrip('•').strip() for line in self.description.split('\n') if line.strip()]

class Experience(models.Model):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='experiences')
    company = models.CharField(max_length=200)
    position = models.CharField(max_length=200)
    location = models.CharField(max_length=200, blank=True, null=True)
    start_date = models.CharField(max_length=50, blank=True, null=True)
    end_date = models.CharField(max_length=50, blank=True, null=True)
    is_current = models.BooleanField(default=False)
    description = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f"{self.position} at {self.company}"

    @property
    def bullets(self):
        if not self.description:
            return []
        return [line.strip().lstrip('-').lstrip('•').strip() for line in self.description.split('\n') if line.strip()]

class Project(models.Model):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='projects')
    title = models.CharField(max_length=200)
    technologies = models.CharField(max_length=200, blank=True, null=True)  # e.g., "Django, LaTeX, HTML/CSS"
    link = models.URLField(blank=True, null=True)
    start_date = models.CharField(max_length=50, blank=True, null=True)
    end_date = models.CharField(max_length=50, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.title

    @property
    def bullets(self):
        if not self.description:
            return []
        return [line.strip().lstrip('-').lstrip('•').strip() for line in self.description.split('\n') if line.strip()]

class Skill(models.Model):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='skills')
    category = models.CharField(max_length=100)  # e.g., "Languages", "Backend", "Tools"
    skills = models.CharField(max_length=500)  # e.g., "C++, Python, JavaScript"

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f"{self.category}: {self.skills}"

class Achievement(models.Model):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='achievements')
    title = models.CharField(max_length=200)
    date = models.CharField(max_length=50, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.title

    @property
    def bullets(self):
        if not self.description:
            return []
        return [line.strip().lstrip('-').lstrip('•').strip() for line in self.description.split('\n') if line.strip()]
