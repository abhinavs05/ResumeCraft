import json
from io import BytesIO
from types import SimpleNamespace
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.template.loader import get_template
from django.db import transaction
from xhtml2pdf import pisa

from .models import Resume, PersonalInfo, Education, Experience, Project, Skill, Achievement

# Simple helper class for live AJAX previews to mimic DB models with 'bullets' property
class TempItem:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
    
    @property
    def bullets(self):
        desc = getattr(self, 'description', '')
        if not desc:
            return []
        return [line.strip().lstrip('-').lstrip('•').strip() for line in desc.split('\n') if line.strip()]

# ----------------- User Authentication -----------------

def landing_page(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'resumes/landing.html')

def register_user(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        u = request.POST.get('username')
        e = request.POST.get('email')
        p = request.POST.get('password')
        pc = request.POST.get('password_confirm')
        if p != pc:
            return render(request, 'resumes/register.html', {'error_messages': 'Passwords do not match'})
        if User.objects.filter(username=u).exists():
            return render(request, 'resumes/register.html', {'error_messages': 'Username already taken'})
        user = User.objects.create_user(username=u, email=e, password=p)
        login(request, user)
        messages.success(request, f"Welcome to ResumeCraft, {user.username}!")
        return redirect('dashboard')
    return render(request, 'resumes/register.html')

def login_user(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        u = request.POST.get('username')
        p = request.POST.get('password')
        user = authenticate(request, username=u, password=p)
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect('dashboard')
        else:
            return render(request, 'resumes/login.html', {'error_messages': 'Invalid username or password'})
    return render(request, 'resumes/login.html')

def logout_user(request):
    logout(request)
    messages.info(request, "Successfully logged out.")
    return redirect('landing_page')

# ----------------- Dashboard & Lifecycle -----------------

@login_required
def dashboard(request):
    resumes = Resume.objects.filter(user=request.user).order_by('-updated_at')
    return render(request, 'resumes/dashboard.html', {'resumes': resumes})

@login_required
def resume_quick_create(request):
    resume = Resume.objects.create(user=request.user, title="My Resume", template_name="jakes")
    # Create empty PersonalInfo to avoid OneToOne errors on loading form
    PersonalInfo.objects.create(
        resume=resume,
        first_name="",
        last_name="",
        email=request.user.email or "",
        phone="",
        location="",
        summary=""
    )
    return redirect('resume_edit', resume_id=resume.id)

@login_required
def resume_delete(request, resume_id):
    if request.method == 'POST':
        resume = get_object_or_404(Resume, id=resume_id, user=request.user)
        resume.delete()
        messages.success(request, "Resume deleted successfully.")
    return redirect('dashboard')

@login_required
def resume_duplicate(request, resume_id):
    if request.method == 'POST':
        old_resume = get_object_or_404(Resume, id=resume_id, user=request.user)
        with transaction.atomic():
            new_resume = Resume.objects.create(
                user=request.user,
                title=f"{old_resume.title} (Copy)",
                template_name=old_resume.template_name
            )
            
            # Duplicate PersonalInfo
            if hasattr(old_resume, 'personal_info'):
                pi = old_resume.personal_info
                PersonalInfo.objects.create(
                    resume=new_resume,
                    first_name=pi.first_name,
                    last_name=pi.last_name,
                    email=pi.email,
                    phone=pi.phone,
                    location=pi.location,
                    website=pi.website,
                    github=pi.github,
                    linkedin=pi.linkedin,
                    portfolio=pi.portfolio,
                    summary=pi.summary
                )
            
            # Duplicate Education
            for edu in old_resume.educations.all():
                Education.objects.create(
                    resume=new_resume,
                    institution=edu.institution,
                    degree=edu.degree,
                    major=edu.major,
                    gpa=edu.gpa,
                    location=edu.location,
                    start_date=edu.start_date,
                    end_date=edu.end_date,
                    is_current=edu.is_current,
                    description=edu.description
                )
                
            # Duplicate Experience
            for exp in old_resume.experiences.all():
                Experience.objects.create(
                    resume=new_resume,
                    company=exp.company,
                    position=exp.position,
                    location=exp.location,
                    start_date=exp.start_date,
                    end_date=exp.end_date,
                    is_current=exp.is_current,
                    description=exp.description
                )
                
            # Duplicate Projects
            for proj in old_resume.projects.all():
                Project.objects.create(
                    resume=new_resume,
                    title=proj.title,
                    technologies=proj.technologies,
                    link=proj.link,
                    start_date=proj.start_date,
                    end_date=proj.end_date,
                    description=proj.description
                )
                
            # Duplicate Skills
            for sk in old_resume.skills.all():
                Skill.objects.create(
                    resume=new_resume,
                    category=sk.category,
                    skills=sk.skills
                )
                
            # Duplicate Achievements
            for ach in old_resume.achievements.all():
                Achievement.objects.create(
                    resume=new_resume,
                    title=ach.title,
                    date=ach.date,
                    description=ach.description
                )
                
        messages.success(request, f"Duplicated '{old_resume.title}' successfully.")
    return redirect('dashboard')

# ----------------- Resume Form Editor -----------------

@login_required
def resume_edit(request, resume_id):
    resume = get_object_or_404(Resume, id=resume_id, user=request.user)
    
    # Try fetching personal info or create it
    try:
        personal_info = resume.personal_info
    except PersonalInfo.DoesNotExist:
        personal_info = PersonalInfo.objects.create(resume=resume, first_name="", last_name="", email=request.user.email or "")
        
    context = {
        'resume': resume,
        'personal_info': personal_info,
        'educations': resume.educations.all(),
        'experiences': resume.experiences.all(),
        'projects': resume.projects.all(),
        'skills': resume.skills.all(),
        'achievements': resume.achievements.all(),
        'is_edit': True
    }
    return render(request, 'resumes/resume_form.html', context)

@login_required
def resume_save(request, resume_id):
    if request.method != 'POST':
        return redirect('dashboard')
        
    resume = get_object_or_404(Resume, id=resume_id, user=request.user)
    
    with transaction.atomic():
        # Update General Resume Settings
        resume.title = request.POST.get('resume_title', resume.title)
        resume.template_name = request.POST.get('template_name', resume.template_name)
        resume.save()
        
        # Update PersonalInfo
        pi, _ = PersonalInfo.objects.get_or_create(resume=resume)
        pi.first_name = request.POST.get('first_name', '')
        pi.last_name = request.POST.get('last_name', '')
        pi.email = request.POST.get('email', '')
        pi.phone = request.POST.get('phone', '')
        pi.location = request.POST.get('location', '')
        pi.website = request.POST.get('website', '')
        pi.github = request.POST.get('github', '')
        pi.linkedin = request.POST.get('linkedin', '')
        pi.portfolio = request.POST.get('portfolio', '')
        pi.summary = request.POST.get('summary', '')
        pi.save()
        
        # 1. Update Educations
        resume.educations.all().delete()
        institutions = request.POST.getlist('institution[]')
        degrees = request.POST.getlist('degree[]')
        majors = request.POST.getlist('major[]')
        gpas = request.POST.getlist('gpa[]')
        locations = request.POST.getlist('location[]')
        start_dates = request.POST.getlist('start_date[]')
        end_dates = request.POST.getlist('end_date[]')
        descriptions = request.POST.getlist('description[]')
        
        for i in range(len(institutions)):
            if institutions[i].strip():
                Education.objects.create(
                    resume=resume,
                    institution=institutions[i],
                    degree=degrees[i] if i < len(degrees) else '',
                    major=majors[i] if i < len(majors) else '',
                    gpa=gpas[i] if i < len(gpas) else '',
                    location=locations[i] if i < len(locations) else '',
                    start_date=start_dates[i] if i < len(start_dates) else '',
                    end_date=end_dates[i] if i < len(end_dates) else '',
                    description=descriptions[i] if i < len(descriptions) else ''
                )
                
        # 2. Update Experiences
        resume.experiences.all().delete()
        companies = request.POST.getlist('company[]')
        positions = request.POST.getlist('position[]')
        exp_locations = request.POST.getlist('exp_location[]')
        exp_dates = request.POST.getlist('exp_dates[]')
        exp_descriptions = request.POST.getlist('exp_description[]')
        
        for i in range(len(companies)):
            if companies[i].strip():
                Experience.objects.create(
                    resume=resume,
                    company=companies[i],
                    position=positions[i] if i < len(positions) else '',
                    location=exp_locations[i] if i < len(exp_locations) else '',
                    start_date=exp_dates[i] if i < len(exp_dates) else '',
                    description=exp_descriptions[i] if i < len(exp_descriptions) else ''
                )
                
        # 3. Update Projects
        resume.projects.all().delete()
        proj_titles = request.POST.getlist('proj_title[]')
        proj_techs = request.POST.getlist('proj_technologies[]')
        proj_links = request.POST.getlist('proj_link[]')
        proj_dates = request.POST.getlist('proj_dates[]')
        proj_descriptions = request.POST.getlist('proj_description[]')
        
        for i in range(len(proj_titles)):
            if proj_titles[i].strip():
                Project.objects.create(
                    resume=resume,
                    title=proj_titles[i],
                    technologies=proj_techs[i] if i < len(proj_techs) else '',
                    link=proj_links[i] if i < len(proj_links) else '',
                    start_date=proj_dates[i] if i < len(proj_dates) else '',
                    description=proj_descriptions[i] if i < len(proj_descriptions) else ''
                )
                
        # 4. Update Skills
        resume.skills.all().delete()
        skill_cats = request.POST.getlist('skill_category[]')
        skills_csv = request.POST.getlist('skills[]')
        
        for i in range(len(skill_cats)):
            if skill_cats[i].strip():
                Skill.objects.create(
                    resume=resume,
                    category=skill_cats[i],
                    skills=skills_csv[i] if i < len(skills_csv) else ''
                )
                
        # 5. Update Achievements
        resume.achievements.all().delete()
        ach_titles = request.POST.getlist('ach_title[]')
        ach_dates = request.POST.getlist('ach_date[]')
        ach_descriptions = request.POST.getlist('ach_description[]')
        
        for i in range(len(ach_titles)):
            if ach_titles[i].strip():
                Achievement.objects.create(
                    resume=resume,
                    title=ach_titles[i],
                    date=ach_dates[i] if i < len(ach_dates) else '',
                    description=ach_descriptions[i] if i < len(ach_descriptions) else ''
                )
                
    messages.success(request, "Resume saved successfully.")
    return redirect('resume_edit', resume_id=resume.id)

# ----------------- AJAX Real-Time Preview -----------------

@login_required
def resume_preview_ajax(request, resume_id):
    if request.method != 'POST':
        return HttpResponse("Invalid request", status=400)
        
    # Build list of entities dynamically from form fields in memory
    # Personal Info
    personal_info = {
        'first_name': request.POST.get('first_name', ''),
        'last_name': request.POST.get('last_name', ''),
        'email': request.POST.get('email', ''),
        'phone': request.POST.get('phone', ''),
        'location': request.POST.get('location', ''),
        'website': request.POST.get('website', ''),
        'github': request.POST.get('github', ''),
        'linkedin': request.POST.get('linkedin', ''),
        'portfolio': request.POST.get('portfolio', ''),
        'summary': request.POST.get('summary', ''),
    }

    # Educations
    institutions = request.POST.getlist('institution[]')
    degrees = request.POST.getlist('degree[]')
    majors = request.POST.getlist('major[]')
    gpas = request.POST.getlist('gpa[]')
    locations = request.POST.getlist('location[]')
    start_dates = request.POST.getlist('start_date[]')
    end_dates = request.POST.getlist('end_date[]')
    descriptions = request.POST.getlist('description[]')
    
    educations = []
    for i in range(len(institutions)):
        if institutions[i].strip():
            educations.append(TempItem(
                institution=institutions[i],
                degree=degrees[i] if i < len(degrees) else '',
                major=majors[i] if i < len(majors) else '',
                gpa=gpas[i] if i < len(gpas) else '',
                location=locations[i] if i < len(locations) else '',
                start_date=start_dates[i] if i < len(start_dates) else '',
                end_date=end_dates[i] if i < len(end_dates) else '',
                description=descriptions[i] if i < len(descriptions) else ''
            ))
            
    # Experiences
    companies = request.POST.getlist('company[]')
    positions = request.POST.getlist('position[]')
    exp_locations = request.POST.getlist('exp_location[]')
    exp_dates = request.POST.getlist('exp_dates[]')
    exp_descriptions = request.POST.getlist('exp_description[]')
    
    experiences = []
    for i in range(len(companies)):
        if companies[i].strip():
            experiences.append(TempItem(
                company=companies[i],
                position=positions[i] if i < len(positions) else '',
                location=exp_locations[i] if i < len(exp_locations) else '',
                start_date=exp_dates[i] if i < len(exp_dates) else '',
                description=exp_descriptions[i] if i < len(exp_descriptions) else ''
            ))
            
    # Projects
    proj_titles = request.POST.getlist('proj_title[]')
    proj_techs = request.POST.getlist('proj_technologies[]')
    proj_links = request.POST.getlist('proj_link[]')
    proj_dates = request.POST.getlist('proj_dates[]')
    proj_descriptions = request.POST.getlist('proj_description[]')
    
    projects = []
    for i in range(len(proj_titles)):
        if proj_titles[i].strip():
            projects.append(TempItem(
                title=proj_titles[i],
                technologies=proj_techs[i] if i < len(proj_techs) else '',
                link=proj_links[i] if i < len(proj_links) else '',
                start_date=proj_dates[i] if i < len(proj_dates) else '',
                description=proj_descriptions[i] if i < len(proj_descriptions) else ''
            ))
            
    # Skills
    skill_cats = request.POST.getlist('skill_category[]')
    skills_csv = request.POST.getlist('skills[]')
    
    skills = []
    for i in range(len(skill_cats)):
        if skill_cats[i].strip():
            skills.append(TempItem(
                category=skill_cats[i],
                skills=skills_csv[i] if i < len(skills_csv) else ''
            ))
            
    # Achievements
    ach_titles = request.POST.getlist('ach_title[]')
    ach_dates = request.POST.getlist('ach_date[]')
    ach_descriptions = request.POST.getlist('ach_description[]')
    
    achievements = []
    for i in range(len(ach_titles)):
        if ach_titles[i].strip():
            achievements.append(TempItem(
                title=ach_titles[i],
                date=ach_dates[i] if i < len(ach_dates) else '',
                description=ach_descriptions[i] if i < len(ach_descriptions) else ''
            ))

    template_name = request.POST.get('template_name', 'jakes')
    context = {
        'personal_info': personal_info,
        'educations': educations,
        'experiences': experiences,
        'projects': projects,
        'skills': skills,
        'achievements': achievements
    }
    
    template_path = f"resumes/templates/{template_name}.html"
    return render(request, template_path, context)

# ----------------- Server-Side PDF Generation -----------------

@login_required
def resume_pdf(request, resume_id):
    resume = get_object_or_404(Resume, id=resume_id, user=request.user)
    
    try:
        personal_info = resume.personal_info
    except PersonalInfo.DoesNotExist:
        personal_info = None
        
    context = {
        'resume': resume,
        'personal_info': personal_info,
        'educations': resume.educations.all(),
        'experiences': resume.experiences.all(),
        'projects': resume.projects.all(),
        'skills': resume.skills.all(),
        'achievements': resume.achievements.all(),
    }
    
    template_path = f"resumes/templates/{resume.template_name}.html"
    template = get_template(template_path)
    html = template.render(context)
    
    result = BytesIO()
    # Compile HTML/CSS into PDF using xhtml2pdf
    pdf = pisa.pisaDocument(BytesIO(html.encode("utf-8")), result)
    
    if not pdf.err:
        response = HttpResponse(result.getvalue(), content_type='application/pdf')
        filename = f"{resume.title.replace(' ', '_')}.pdf"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
        
    return HttpResponse("Error compiling PDF", status=500)

# ----------------- Sample Data Loader -----------------

@login_required
def load_sample_data(request, resume_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request'}, status=400)
        
    resume = get_object_or_404(Resume, id=resume_id, user=request.user)
    
    with transaction.atomic():
        # Clear existing relations
        resume.educations.all().delete()
        resume.experiences.all().delete()
        resume.projects.all().delete()
        resume.skills.all().delete()
        resume.achievements.all().delete()
        
        # Populate Personal Info
        pi, _ = PersonalInfo.objects.get_or_create(resume=resume)
        pi.first_name = "Dhruv"
        pi.last_name = "Nimbalkar"
        pi.email = "dhruvnimbalkar2015@gmail.com"
        pi.phone = "9971084004"
        pi.location = "New Delhi"
        pi.website = "https://example.com"
        pi.github = "https://github.com/Dhruv"
        pi.linkedin = "https://linkedin.com/in/Dhruv-Nimbalkar"
        pi.summary = "Third-year Computer Science student with strong foundations in backend development using Python and Django. Experienced in building secure, scalable REST APIs and managing SQL databases. Proficient in C++, data structures, and algorithmic problem-solving. Seeking a backend engineering internship to contribute to scalable REST API development."
        pi.save()
        
        # Populate Education
        Education.objects.create(
            resume=resume,
            institution="Guru Gobind Singh Indraprastha University",
            degree="B.tech",
            major="Information Technology",
            gpa="8.5/10",
            location="New Delhi",
            start_date="2023",
            end_date="2027",
            description="Focusing on Computer Science core courses: Algorithms, Database Management, and Operating Systems."
        )
        
        # Populate Experiences
        Experience.objects.create(
            resume=resume,
            company="Resume Builder Project",
            position="Lead Developer",
            location="Self-Project",
            start_date="May 2026",
            description="- Developed a full-stack web application using Django to generate professional ATS-friendly PDF resumes.\n- Integrated LaTeX and pdflatex for automated high-quality resume PDF generation based on the Jake's Resume template.\n- Built dynamic forms for user input including education, experience, projects, and skills.\n- Implemented backend logic to convert structured form data into formatted documents automatically."
        )
        
        Experience.objects.create(
            resume=resume,
            company="Todo Web Application",
            position="Backend Engineer",
            location="Open Source Contribution",
            start_date="Jan 2026",
            description="- Developed a task management web application using Django with secure user authentication.\n- Implemented CRUD operations for task management with status, priority, and due-date tracking.\n- Designed a responsive dashboard UI using HTML, CSS, and Bootstrap with SQLite database integration."
        )
        
        # Populate Projects
        Project.objects.create(
            resume=resume,
            title="Resume Builder App",
            technologies="Django, LaTeX, HTML/CSS",
            link="https://github.com/Dhruv/resume-builder",
            start_date="May 2026",
            description="- Developed automated ATS resume builder with real-time PDF preview.\n- Enabled 5 distinct layouts including Jake's template."
        )
        
        # Populate Skills
        Skill.objects.create(resume=resume, category="Languages", skills="C++, Python, JavaScript, Java")
        Skill.objects.create(resume=resume, category="Backend", skills="Django, Django REST Framework, REST APIs")
        Skill.objects.create(resume=resume, category="Database", skills="PostgreSQL, SQL, DBMS")
        Skill.objects.create(resume=resume, category="AI/ML", skills="NumPy, Pandas, Machine Learning (basics)")
        Skill.objects.create(resume=resume, category="Tools", skills="Git, GitHub, VS Code")
        Skill.objects.create(resume=resume, category="Core Concepts", skills="Data Structures & Algorithms, OOP, DBMS, CN")
        
        # Populate Achievements
        Achievement.objects.create(
            resume=resume,
            title="Solved 400+ problems on competitive programming platforms, demonstrating strong proficiency in Data Structures and Algorithms.",
            date="2025 - Present"
        )
        Achievement.objects.create(
            resume=resume,
            title="Independently designed, developed, and deployed multiple projects, managing the full software development lifecycle.",
            date="2025"
        )
        
    return JsonResponse({'status': 'success'})

# ----------------- ATS Keyword Match Scanner -----------------

@login_required
def resume_ats_scan(request, resume_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request'}, status=400)
        
    jd = request.POST.get('job_description', '').lower()
    if not jd:
        return JsonResponse({'error': 'Job description is empty'}, status=400)
        
    # Get all text from resume to search
    resume = get_object_or_404(Resume, id=resume_id, user=request.user)
    
    resume_text_parts = []
    
    # 1. Personal summary
    try:
        pi = resume.personal_info
        resume_text_parts.append(pi.summary or '')
    except PersonalInfo.DoesNotExist:
        pass
        
    # 2. Experiences
    for exp in resume.experiences.all():
        resume_text_parts.append(exp.position)
        resume_text_parts.append(exp.company)
        resume_text_parts.append(exp.description or '')
        
    # 3. Projects
    for proj in resume.projects.all():
        resume_text_parts.append(proj.title)
        resume_text_parts.append(proj.technologies or '')
        resume_text_parts.append(proj.description or '')
        
    # 4. Skills
    for sk in resume.skills.all():
        resume_text_parts.append(sk.category)
        resume_text_parts.append(sk.skills)
        
    resume_text = " ".join(resume_text_parts).lower()
    
    # List of technical/professional keywords to extract & look for in job desc
    target_keywords_bank = [
        # Languages
        'python', 'c++', 'javascript', 'java', 'html', 'css', 'sql', 'typescript', 'rust', 'go', 'php', 'ruby', 'c#',
        # Backend / Frameworks
        'django', 'flask', 'fastapi', 'rest api', 'graphql', 'express', 'node.js', 'spring boot', 'laravel', 'react', 'next.js', 'vue', 'angular',
        # DB & Cloud
        'postgresql', 'mysql', 'sqlite', 'mongodb', 'redis', 'aws', 'docker', 'kubernetes', 'cloud', 'gcp', 'azure',
        # Concepts / Methods
        'data structures', 'algorithms', 'oop', 'dbms', 'git', 'github', 'agile', 'scrum', 'testing', 'unit tests', 'ci/cd',
        'machine learning', 'deep learning', 'nlp', 'numpy', 'pandas', 'scikit-learn', 'tensorflow', 'pytorch',
        # Soft skills / general
        'leadership', 'teamwork', 'communication', 'problem solving', 'analytical', 'development', 'internship'
    ]
    
    # Find which target keywords are present in the job description
    jd_keywords = set()
    for kw in target_keywords_bank:
        if kw in jd:
            jd_keywords.add(kw)
            
    # Compute keyword matching
    matched_keywords = []
    missing_keywords = []
    
    for kw in jd_keywords:
        if kw in resume_text:
            matched_keywords.append(kw)
        else:
            missing_keywords.append(kw)
            
    # Calculate simple match score
    total_jd_kws = len(jd_keywords)
    if total_jd_kws > 0:
        score = int((len(matched_keywords) / total_jd_kws) * 100)
    else:
        score = 0
        
    return JsonResponse({
        'score': score,
        'matched_keywords': sorted(matched_keywords),
        'missing_keywords': sorted(missing_keywords)
    })

# ----------------- JSON Backup & Portability -----------------

@login_required
def resume_export_json(request, resume_id):
    resume = get_object_or_404(Resume, id=resume_id, user=request.user)
    
    try:
        pi = resume.personal_info
        pi_data = {
            'first_name': pi.first_name,
            'last_name': pi.last_name,
            'email': pi.email,
            'phone': pi.phone,
            'location': pi.location,
            'website': pi.website,
            'github': pi.github,
            'linkedin': pi.linkedin,
            'portfolio': pi.portfolio,
            'summary': pi.summary
        }
    except PersonalInfo.DoesNotExist:
        pi_data = {}
        
    data = {
        'title': resume.title,
        'template_name': resume.template_name,
        'personal_info': pi_data,
        'educations': [
            {
                'institution': e.institution,
                'degree': e.degree,
                'major': e.major,
                'gpa': e.gpa,
                'location': e.location,
                'start_date': e.start_date,
                'end_date': e.end_date,
                'description': e.description
            } for e in resume.educations.all()
        ],
        'experiences': [
            {
                'company': e.company,
                'position': e.position,
                'location': e.location,
                'start_date': e.start_date,
                'description': e.description
            } for e in resume.experiences.all()
        ],
        'projects': [
            {
                'title': p.title,
                'technologies': p.technologies,
                'link': p.link,
                'start_date': p.start_date,
                'description': p.description
            } for p in resume.projects.all()
        ],
        'skills': [
            {
                'category': s.category,
                'skills': s.skills
            } for s in resume.skills.all()
        ],
        'achievements': [
            {
                'title': a.title,
                'date': a.date,
                'description': a.description
            } for a in resume.achievements.all()
        ]
    }
    
    response = JsonResponse(data, json_dumps_params={'indent': 2})
    response['Content-Disposition'] = f'attachment; filename="{resume.title.replace(" ", "_")}_backup.json"'
    return response

@login_required
def resume_import_json(request, resume_id):
    if request.method != 'POST' or 'json_file' not in request.FILES:
        messages.error(request, "Please upload a valid backup JSON file.")
        return redirect('resume_edit', resume_id=resume_id)
        
    resume = get_object_or_404(Resume, id=resume_id, user=request.user)
    
    try:
        raw_data = request.FILES['json_file'].read()
        data = json.loads(raw_data.decode('utf-8'))
        
        with transaction.atomic():
            # Update General Info
            resume.title = data.get('title', resume.title)
            resume.template_name = data.get('template_name', resume.template_name)
            resume.save()
            
            # Update Personal Info
            pi_data = data.get('personal_info', {})
            pi, _ = PersonalInfo.objects.get_or_create(resume=resume)
            pi.first_name = pi_data.get('first_name', '')
            pi.last_name = pi_data.get('last_name', '')
            pi.email = pi_data.get('email', '')
            pi.phone = pi_data.get('phone', '')
            pi.location = pi_data.get('location', '')
            pi.website = pi_data.get('website', '')
            pi.github = pi_data.get('github', '')
            pi.linkedin = pi_data.get('linkedin', '')
            pi.portfolio = pi_data.get('portfolio', '')
            pi.summary = pi_data.get('summary', '')
            pi.save()
            
            # Wipe and restore related objects
            resume.educations.all().delete()
            for edu in data.get('educations', []):
                Education.objects.create(
                    resume=resume,
                    institution=edu.get('institution', ''),
                    degree=edu.get('degree', ''),
                    major=edu.get('major', ''),
                    gpa=edu.get('gpa', ''),
                    location=edu.get('location', ''),
                    start_date=edu.get('start_date', ''),
                    end_date=edu.get('end_date', ''),
                    description=edu.get('description', '')
                )
                
            resume.experiences.all().delete()
            for exp in data.get('experiences', []):
                Experience.objects.create(
                    resume=resume,
                    company=exp.get('company', ''),
                    position=exp.get('position', ''),
                    location=exp.get('location', ''),
                    start_date=exp.get('start_date', ''),
                    description=exp.get('description', '')
                )
                
            resume.projects.all().delete()
            for proj in data.get('projects', []):
                Project.objects.create(
                    resume=resume,
                    title=proj.get('title', ''),
                    technologies=proj.get('technologies', ''),
                    link=proj.get('link', None),
                    start_date=proj.get('start_date', ''),
                    description=proj.get('description', '')
                )
                
            resume.skills.all().delete()
            for sk in data.get('skills', []):
                Skill.objects.create(
                    resume=resume,
                    category=sk.get('category', ''),
                    skills=sk.get('skills', '')
                )
                
            resume.achievements.all().delete()
            for ach in data.get('achievements', []):
                Achievement.objects.create(
                    resume=resume,
                    title=ach.get('title', ''),
                    date=ach.get('date', ''),
                    description=ach.get('description', '')
                )
                
        messages.success(request, "Resume restored from backup successfully!")
    except Exception as e:
        messages.error(request, f"Failed to restore backup: {str(e)}")
        
    return redirect('resume_edit', resume_id=resume_id)
