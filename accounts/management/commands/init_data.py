from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model
from core.models import SiteSettings
from jobs.models import JobCategory, Job
from blog.models import BlogCategory, BlogPost
from taggit.models import Tag
from datetime import timedelta

User = get_user_model()

class Command(BaseCommand):
    help = 'Initialize site data with sample content'

    def handle(self, *args, **options):
        # Create admin user if not exists
        admin_user, created = User.objects.get_or_create(
            email='admin@jobportalpro.com',
            defaults={
                'first_name': 'Admin',
                'last_name': 'User',
                'user_type': 'admin',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if created:
            admin_user.set_password('Admin@123')
            admin_user.save()
            self.stdout.write(self.style.SUCCESS('Admin user created: admin@jobportalpro.com / Admin@123'))
        else:
            self.stdout.write(self.style.WARNING('Admin user already exists'))

        # Create site settings if not exists
        if not SiteSettings.objects.exists():
            SiteSettings.objects.create(
                site_name='JobPortal Pro',
                tagline='Find Your Dream Job Today',
                about_title='About JobPortal Pro',
                about_description='''
                <p>JobPortal Pro is your premier destination for finding the perfect job match. 
                We connect talented professionals with top employers across various industries.</p>
                
                <p>Founded in 2024, we've quickly grown to become one of the most trusted job 
                portals in the industry. Our platform uses advanced matching algorithms to connect 
                job seekers with positions that match their skills, experience, and career aspirations.</p>
                
                <p>Whether you're looking for your first job, making a career change, or seeking 
                executive-level positions, JobPortal Pro has opportunities for professionals at 
                every stage of their career journey.</p>
                ''',
                mission='''
                <p>Our mission is to empower job seekers by providing them with the tools and 
                resources they need to find meaningful employment opportunities. We strive to 
                create a seamless bridge between talented individuals and organizations looking 
                to hire the best talent.</p>
                
                <p>We believe that everyone deserves the opportunity to find work that fulfills 
                them professionally and personally. That's why we've built a platform that's 
                accessible, intuitive, and effective for job seekers at all levels.</p>
                ''',
                vision='''
                <p>We envision a world where every professional can find a job that not only 
                matches their skills but also fulfills their career aspirations. We aim to be 
                the most trusted and efficient job portal, revolutionizing the way people find 
                employment.</p>
                
                <p>Our goal is to become the go-to platform for job seekers and employers alike, 
                known for our commitment to quality, innovation, and user satisfaction.</p>
                ''',
                email='contact@jobportalpro.com',
                phone='+1 (555) 123-4567',
                address='123 Business Avenue, Suite 100\nNew York, NY 10001\nUnited States',
                google_map_embed='<iframe src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3022.9663095919364!2d-73.98438768459429!3d40.74844097932847!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x89c259a9b3117469%3A0xd134e199a405a163!2sEmpire%20State%20Building!5e0!3m2!1sen!2sus!4v1635959562000!5m2!1sen!2sus" width="100%" height="300" style="border:0;" allowfullscreen="" loading="lazy"></iframe>',
                facebook='https://facebook.com/jobportalpro',
                twitter='https://twitter.com/jobportalpro',
                linkedin='https://linkedin.com/company/jobportalpro',
                instagram='https://instagram.com/jobportalpro',
                youtube='https://youtube.com/jobportalpro',
                meta_description='Find your dream job with JobPortal Pro. Browse thousands of job listings from top companies. Apply online and track your applications.',
                meta_keywords='jobs, careers, employment, job search, hiring, recruitment, remote jobs, full-time jobs',
                primary_color='#0d6efd',
                secondary_color='#6c757d',
                footer_text='JobPortal Pro is the leading online job board connecting job seekers with employers. We help professionals find their dream jobs and companies hire the best talent.',
                copyright_text='© 2024 JobPortal Pro. All rights reserved.'
            )
            self.stdout.write(self.style.SUCCESS('Site settings created successfully!'))
        else:
            self.stdout.write(self.style.WARNING('Site settings already exist.'))

        # Create job categories
        categories_data = [
            {'name': 'Technology', 'slug': 'technology', 'description': 'Software development, IT, and tech-related jobs', 'icon': 'fas fa-laptop-code'},
            {'name': 'Healthcare', 'slug': 'healthcare', 'description': 'Medical, nursing, and healthcare positions', 'icon': 'fas fa-hospital'},
            {'name': 'Finance', 'slug': 'finance', 'description': 'Banking, accounting, and financial services', 'icon': 'fas fa-chart-line'},
            {'name': 'Marketing', 'slug': 'marketing', 'description': 'Digital marketing, advertising, and PR roles', 'icon': 'fas fa-bullhorn'},
            {'name': 'Sales', 'slug': 'sales', 'description': 'Sales and business development positions', 'icon': 'fas fa-handshake'},
            {'name': 'Education', 'slug': 'education', 'description': 'Teaching, training, and educational roles', 'icon': 'fas fa-graduation-cap'},
            {'name': 'Engineering', 'slug': 'engineering', 'description': 'Engineering and technical positions', 'icon': 'fas fa-cogs'},
            {'name': 'Design', 'slug': 'design', 'description': 'UI/UX, graphic design, and creative roles', 'icon': 'fas fa-palette'},
        ]
        
        categories = {}
        for cat_data in categories_data:
            category, created = JobCategory.objects.get_or_create(
                slug=cat_data['slug'],
                defaults=cat_data
            )
            categories[cat_data['slug']] = category
            if created:
                self.stdout.write(self.style.SUCCESS(f'Category created: {category.name}'))
        
        # Create blog categories
        blog_categories_data = [
            {'name': 'Career Advice', 'slug': 'career-advice', 'description': 'Tips and guidance for career development'},
            {'name': 'Job Search Tips', 'slug': 'job-search-tips', 'description': 'Strategies for finding your next job'},
            {'name': 'Interview Preparation', 'slug': 'interview-preparation', 'description': 'How to ace your job interviews'},
            {'name': 'Resume Writing', 'slug': 'resume-writing', 'description': 'Create a standout resume'},
            {'name': 'Industry Insights', 'slug': 'industry-insights', 'description': 'Latest trends and news in various industries'},
            {'name': 'Workplace Culture', 'slug': 'workplace-culture', 'description': 'Navigating office dynamics and culture'},
        ]
        
        blog_categories = {}
        for cat_data in blog_categories_data:
            category, created = BlogCategory.objects.get_or_create(
                slug=cat_data['slug'],
                defaults=cat_data
            )
            blog_categories[cat_data['slug']] = category
            if created:
                self.stdout.write(self.style.SUCCESS(f'Blog category created: {category.name}'))

        # Create sample jobs
        now = timezone.now()
        
        jobs_data = [
            {
                'title': 'Senior Full Stack Developer',
                'slug': 'senior-full-stack-developer',
                'category': categories['technology'],
                'company_name': 'TechCorp Solutions',
                'company_website': 'https://techcorp.example.com',
                'location': 'New York, NY',
                'job_type': 'full_time',
                'experience_level': 'senior',
                'salary_min': 120000,
                'salary_max': 160000,
                'salary_currency': 'USD',
                'is_salary_negotiable': True,
                'description': '''
                <h3>About the Role</h3>
                <p>TechCorp Solutions is seeking a Senior Full Stack Developer to join our innovative engineering team. You'll be working on cutting-edge web applications that serve millions of users worldwide.</p>
                
                <h3>What You'll Do</h3>
                <ul>
                    <li>Design and develop scalable web applications using React, Node.js, and Python</li>
                    <li>Lead technical architecture decisions and mentor junior developers</li>
                    <li>Collaborate with cross-functional teams to define and implement new features</li>
                    <li>Optimize application performance and ensure high availability</li>
                    <li>Participate in code reviews and maintain code quality standards</li>
                </ul>
                
                <h3>What We're Looking For</h3>
                <ul>
                    <li>5+ years of experience in full-stack development</li>
                    <li>Strong proficiency in JavaScript/TypeScript and Python</li>
                    <li>Experience with React, Node.js, and PostgreSQL</li>
                    <li>Knowledge of cloud services (AWS/GCP/Azure)</li>
                    <li>Excellent problem-solving and communication skills</li>
                </ul>
                ''',
                'requirements': '''
                <h3>Required Qualifications</h3>
                <ul>
                    <li>Bachelor's degree in Computer Science or related field</li>
                    <li>5+ years of professional software development experience</li>
                    <li>Strong understanding of data structures and algorithms</li>
                    <li>Experience with Agile/Scrum methodologies</li>
                    <li>Proven track record of delivering complex web applications</li>
                </ul>
                
                <h3>Preferred Qualifications</h3>
                <ul>
                    <li>Master's degree in Computer Science</li>
                    <li>Experience with microservices architecture</li>
                    <li>Contributions to open-source projects</li>
                    <li>Knowledge of DevOps practices and CI/CD pipelines</li>
                </ul>
                ''',
                'benefits': '''
                <h3>What We Offer</h3>
                <ul>
                    <li>Competitive salary and equity package</li>
                    <li>Comprehensive health, dental, and vision insurance</li>
                    <li>Flexible work hours and remote work options</li>
                    <li>401(k) with company match</li>
                    <li>Annual learning and development budget ($5,000)</li>
                    <li>Free lunch and snacks in office</li>
                    <li>Gym membership reimbursement</li>
                    <li>Regular team events and offsites</li>
                </ul>
                ''',
                'skills_list': ['JavaScript', 'Python', 'React', 'Node.js', 'PostgreSQL', 'AWS', 'TypeScript', 'Docker', 'Git', 'REST APIs'],
                'vacancies': 2,
                'application_deadline': now + timedelta(days=30),
                'status': 'published',
                'is_featured': True,
                'is_remote': False,
                'posted_by': admin_user,
                'published_at': now - timedelta(days=2),
            },
            {
                'title': 'Marketing Manager',
                'slug': 'marketing-manager',
                'category': categories['marketing'],
                'company_name': 'GrowthGenius Inc.',
                'company_website': 'https://growthgenius.example.com',
                'location': 'Remote',
                'job_type': 'remote',
                'experience_level': 'mid',
                'salary_min': 80000,
                'salary_max': 110000,
                'salary_currency': 'USD',
                'is_salary_negotiable': False,
                'description': '''
                <h3>About the Role</h3>
                <p>GrowthGenius Inc. is looking for a creative and data-driven Marketing Manager to lead our digital marketing efforts. You'll be responsible for developing and executing marketing strategies that drive brand awareness and customer acquisition.</p>
                
                <h3>Key Responsibilities</h3>
                <ul>
                    <li>Develop and implement comprehensive digital marketing strategies</li>
                    <li>Manage multi-channel marketing campaigns (email, social media, PPC, SEO)</li>
                    <li>Analyze marketing metrics and optimize campaign performance</li>
                    <li>Lead a team of marketing specialists and content creators</li>
                    <li>Manage marketing budget and ROI reporting</li>
                </ul>
                
                <h3>What Success Looks Like</h3>
                <ul>
                    <li>20% increase in qualified leads within first 6 months</li>
                    <li>Improved conversion rates across all channels</li>
                    <li>Successful launch of at least 3 major campaigns per quarter</li>
                </ul>
                ''',
                'requirements': '''
                <h3>Requirements</h3>
                <ul>
                    <li>3-5 years of digital marketing experience</li>
                    <li>Proven track record of managing successful marketing campaigns</li>
                    <li>Experience with marketing automation tools (HubSpot, Marketo)</li>
                    <li>Strong analytical skills and data-driven mindset</li>
                    <li>Excellent written and verbal communication skills</li>
                    <li>Experience with A/B testing and conversion optimization</li>
                </ul>
                ''',
                'benefits': '''
                <h3>Perks & Benefits</h3>
                <ul>
                    <li>Competitive salary with performance bonuses</li>
                    <li>100% remote work environment</li>
                    <li>Flexible working hours</li>
                    <li>Health and wellness benefits</li>
                    <li>Home office setup stipend</li>
                    <li>Professional development opportunities</li>
                    <li>Annual company retreat</li>
                </ul>
                ''',
                'skills_list': ['Digital Marketing', 'SEO', 'Google Analytics', 'Content Strategy', 'PPC', 'Social Media Marketing', 'Email Marketing', 'HubSpot'],
                'vacancies': 1,
                'application_deadline': now + timedelta(days=21),
                'status': 'published',
                'is_featured': True,
                'is_remote': True,
                'posted_by': admin_user,
                'published_at': now - timedelta(days=1),
            },
            {
                'title': 'Data Scientist',
                'slug': 'data-scientist',
                'category': categories['technology'],
                'company_name': 'DataDriven Analytics',
                'company_website': 'https://datadriven.example.com',
                'location': 'San Francisco, CA',
                'job_type': 'full_time',
                'experience_level': 'mid',
                'salary_min': 130000,
                'salary_max': 170000,
                'salary_currency': 'USD',
                'is_salary_negotiable': True,
                'description': '''
                <h3>About DataDriven Analytics</h3>
                <p>We're a fast-growing analytics company helping businesses make data-driven decisions. We're looking for a talented Data Scientist to join our team and help us unlock insights from complex datasets.</p>
                
                <h3>What You'll Do</h3>
                <ul>
                    <li>Build and deploy machine learning models</li>
                    <li>Analyze large datasets to identify trends and patterns</li>
                    <li>Create data visualizations and dashboards</li>
                    <li>Collaborate with engineering and product teams</li>
                    <li>Present findings to stakeholders</li>
                </ul>
                ''',
                'requirements': '''
                <h3>Qualifications</h3>
                <ul>
                    <li>MS/PhD in Computer Science, Statistics, or related field</li>
                    <li>3+ years of experience in data science</li>
                    <li>Proficiency in Python, R, and SQL</li>
                    <li>Experience with machine learning frameworks (TensorFlow, PyTorch)</li>
                    <li>Strong statistical analysis skills</li>
                </ul>
                ''',
                'benefits': '''
                <h3>Benefits</h3>
                <ul>
                    <li>Competitive salary and stock options</li>
                    <li>Health, dental, and vision coverage</li>
                    <li>Unlimited PTO</li>
                    <li>Conference attendance budget</li>
                    <li>Flexible work arrangements</li>
                </ul>
                ''',
                'skills_list': ['Python', 'R', 'SQL', 'Machine Learning', 'TensorFlow', 'PyTorch', 'Statistics', 'Data Visualization', 'AWS'],
                'vacancies': 1,
                'application_deadline': now + timedelta(days=45),
                'status': 'published',
                'is_featured': False,
                'is_remote': False,
                'posted_by': admin_user,
                'published_at': now - timedelta(days=5),
            },
            {
                'title': 'UX/UI Designer',
                'slug': 'ux-ui-designer',
                'category': categories['design'],
                'company_name': 'CreativeLab Studios',
                'company_website': 'https://creativelab.example.com',
                'location': 'Austin, TX',
                'job_type': 'contract',
                'experience_level': 'mid',
                'salary_min': 70000,
                'salary_max': 95000,
                'salary_currency': 'USD',
                'is_salary_negotiable': True,
                'description': '''
                <h3>About the Position</h3>
                <p>CreativeLab Studios is seeking a talented UX/UI Designer to create beautiful, intuitive interfaces for our clients' web and mobile applications.</p>
                
                <h3>Responsibilities</h3>
                <ul>
                    <li>Design user interfaces for web and mobile applications</li>
                    <li>Create wireframes, prototypes, and high-fidelity mockups</li>
                    <li>Conduct user research and usability testing</li>
                    <li>Collaborate with developers to implement designs</li>
                    <li>Maintain design systems and style guides</li>
                </ul>
                ''',
                'requirements': '''
                <h3>Requirements</h3>
                <ul>
                    <li>3+ years of UX/UI design experience</li>
                    <li>Proficiency in Figma, Sketch, or Adobe XD</li>
                    <li>Strong portfolio showcasing web and mobile designs</li>
                    <li>Understanding of user-centered design principles</li>
                    <li>Experience with design systems</li>
                </ul>
                ''',
                'benefits': '''
                <h3>What We Offer</h3>
                <ul>
                    <li>Competitive contract rate</li>
                    <li>Flexible schedule</li>
                    <li>Creative work environment</li>
                    <li>Opportunity to work with major brands</li>
                </ul>
                ''',
                'skills_list': ['Figma', 'Sketch', 'Adobe XD', 'Wireframing', 'Prototyping', 'User Research', 'Design Systems', 'HTML/CSS'],
                'vacancies': 1,
                'application_deadline': now + timedelta(days=14),
                'status': 'published',
                'is_featured': False,
                'is_remote': False,
                'posted_by': admin_user,
                'published_at': now - timedelta(days=3),
            },
        ]
        
        for job_data in jobs_data:
            skills = job_data.pop('skills_list', [])
            job, created = Job.objects.get_or_create(
                slug=job_data['slug'],
                defaults=job_data
            )
            if created and skills:
                for skill in skills:
                    tag, _ = Tag.objects.get_or_create(name=skill)
                    job.skills_required.add(tag)
                self.stdout.write(self.style.SUCCESS(f'Job created: {job.title}'))
        
        # Create sample blog posts
        blog_posts_data = [
            {
                'title': '10 Tips for a Successful Job Interview',
                'slug': '10-tips-successful-job-interview',
                'category': blog_categories['interview-preparation'],
                'excerpt': 'Master your next job interview with these essential tips from industry experts. From preparation to follow-up, learn how to make a lasting impression.',
                'content': '''
                <h2>Introduction</h2>
                <p>Job interviews can be nerve-wracking, but with proper preparation, you can walk into any interview with confidence. Here are 10 essential tips to help you succeed.</p>
                
                <h3>1. Research the Company</h3>
                <p>Before your interview, thoroughly research the company. Understand their products, services, culture, and recent news. This knowledge will help you ask informed questions and show genuine interest.</p>
                
                <h3>2. Practice Common Questions</h3>
                <p>Prepare answers for common interview questions like "Tell me about yourself" and "Where do you see yourself in 5 years?" Practice with a friend or in front of a mirror.</p>
                
                <h3>3. Prepare Your Questions</h3>
                <p>Always have thoughtful questions ready for the interviewer. Ask about team culture, growth opportunities, and the company's vision. This shows you're engaged and serious about the position.</p>
                
                <h3>4. Dress Appropriately</h3>
                <p>Research the company's dress code and dress one level above it. When in doubt, it's better to be slightly overdressed than underdressed.</p>
                
                <h3>5. Arrive Early</h3>
                <p>Plan to arrive 10-15 minutes early. This gives you time to compose yourself and shows punctuality. For virtual interviews, log in 5 minutes early to test your equipment.</p>
                
                <h3>6. Bring Necessary Materials</h3>
                <p>Bring multiple copies of your resume, a list of references, and any portfolio materials. Have them organized in a professional folder.</p>
                
                <h3>7. Use the STAR Method</h3>
                <p>When answering behavioral questions, use the STAR method: Situation, Task, Action, Result. This structured approach helps you give clear, concise answers.</p>
                
                <h3>8. Show Enthusiasm</h3>
                <p>Employers want to hire people who are excited about the role. Show your enthusiasm through your tone of voice, body language, and the questions you ask.</p>
                
                <h3>9. Follow Up</h3>
                <p>Send a thank-you email within 24 hours of the interview. Reference specific topics discussed and reiterate your interest in the position.</p>
                
                <h3>10. Learn from Each Experience</h3>
                <p>Whether you get the job or not, each interview is a learning opportunity. Reflect on what went well and what you could improve for next time.</p>
                
                <h2>Conclusion</h2>
                <p>Remember, an interview is also your opportunity to evaluate if the company and role are right for you. Stay confident, be yourself, and good luck!</p>
                ''',
                'author': admin_user,
                'tags_list': ['interview', 'career advice', 'job search', 'interview tips', 'preparation'],
                'status': 'published',
                'published_at': now - timedelta(days=10),
            },
            {
                'title': 'How to Write a Resume That Gets Noticed',
                'slug': 'how-to-write-resume-that-gets-noticed',
                'category': blog_categories['resume-writing'],
                'excerpt': 'Learn how to create a compelling resume that stands out to recruiters and hiring managers. Discover the key elements that make your resume shine.',
                'content': '''
                <h2>Why Your Resume Matters</h2>
                <p>Your resume is often the first impression you make on a potential employer. In today's competitive job market, having a well-crafted resume is essential to getting noticed.</p>
                
                <h3>1. Start with a Strong Summary</h3>
                <p>Begin your resume with a compelling professional summary that highlights your key achievements and career goals. This should be 2-3 sentences that capture who you are as a professional.</p>
                
                <p><strong>Example:</strong> "Results-driven software engineer with 5+ years of experience building scalable web applications. Passionate about clean code and creating intuitive user experiences."</p>
                
                <h3>2. Quantify Your Achievements</h3>
                <p>Use numbers and metrics to demonstrate your impact. Instead of saying "Improved sales," say "Increased sales by 35% in Q3 2023."</p>
                
                <h3>3. Tailor Your Resume for Each Job</h3>
                <p>Customize your resume for each position you apply for. Use keywords from the job description and highlight relevant experience and skills.</p>
                
                <h3>4. Keep It Clean and Professional</h3>
                <ul>
                    <li>Use a clean, professional font (Arial, Calibri, or Garamond)</li>
                    <li>Keep font size between 10-12 points</li>
                    <li>Use consistent formatting throughout</li>
                    <li>Limit your resume to 1-2 pages</li>
                    <li>Use bullet points for easy scanning</li>
                </ul>
                
                <h3>5. Include Relevant Keywords</h3>
                <p>Many companies use Applicant Tracking Systems (ATS) to screen resumes. Include relevant keywords from the job description to increase your chances of passing the initial screening.</p>
                
                <h3>6. Highlight Skills</h3>
                <p>Create a dedicated skills section that lists your technical and soft skills. Be honest about your proficiency levels.</p>
                
                <h3>7. Proofread Carefully</h3>
                <p>Typos and grammatical errors can cost you an interview. Proofread your resume multiple times and ask someone else to review it as well.</p>
                
                <h2>Common Resume Mistakes to Avoid</h2>
                <ul>
                    <li>Including irrelevant personal information</li>
                    <li>Using an unprofessional email address</li>
                    <li>Having unexplained employment gaps</li>
                    <li>Using generic language and clichés</li>
                    <li>Forgetting to update contact information</li>
                </ul>
                
                <h2>Conclusion</h2>
                <p>A great resume opens doors. Take the time to craft a document that truly represents your professional brand and showcases your value to potential employers.</p>
                ''',
                'author': admin_user,
                'tags_list': ['resume', 'job search', 'career advice', 'resume writing', 'CV tips'],
                'status': 'published',
                'published_at': now - timedelta(days=7),
            },
            {
                'title': 'The Future of Remote Work in 2024',
                'slug': 'future-of-remote-work-2024',
                'category': blog_categories['workplace-culture'],
                'excerpt': 'Explore the latest trends in remote work and what they mean for job seekers and employers. Discover how to thrive in a distributed work environment.',
                'content': '''
                <h2>The Remote Work Revolution Continues</h2>
                <p>Remote work has transformed from a temporary solution during the pandemic to a permanent fixture in the modern workplace. As we move through 2024, several key trends are shaping the future of work.</p>
                
                <h3>1. Hybrid Work Models Become Standard</h3>
                <p>Companies are increasingly adopting hybrid models that combine remote and in-office work. This approach offers flexibility while maintaining team collaboration and company culture.</p>
                
                <h3>2. Investment in Remote Infrastructure</h3>
                <p>Organizations are investing heavily in tools and technologies that support remote work, including video conferencing, project management software, and virtual collaboration platforms.</p>
                
                <h3>3. Focus on Work-Life Balance</h3>
                <p>Remote work has blurred the lines between professional and personal life. Companies are implementing policies to protect employee well-being and prevent burnout.</p>
                
                <h3>4. Global Talent Pools</h3>
                <p>With geographical barriers removed, companies can now hire the best talent from anywhere in the world. This creates more opportunities for job seekers and increased competition.</p>
                
                <h3>5. Digital Nomad Lifestyle</h3>
                <p>More professionals are embracing the digital nomad lifestyle, working from different locations around the world. Countries are responding with special visas to attract remote workers.</p>
                
                <h2>Tips for Thriving in a Remote Work Environment</h2>
                <ul>
                    <li>Create a dedicated workspace</li>
                    <li>Establish a consistent routine</li>
                    <li>Communicate proactively with your team</li>
                    <li>Take regular breaks</li>
                    <li>Invest in professional development</li>
                    <li>Maintain social connections with colleagues</li>
                </ul>
                
                <h2>Conclusion</h2>
                <p>Remote work is here to stay, and those who adapt to this new way of working will have a competitive advantage in the job market. Embrace the flexibility while maintaining discipline and connection with your team.</p>
                ''',
                'author': admin_user,
                'tags_list': ['remote work', 'work from home', 'career trends', 'workplace', 'digital nomad'],
                'status': 'published',
                'published_at': now - timedelta(days=3),
            },
            {
                'title': 'Top 5 Skills Employers Are Looking For',
                'slug': 'top-5-skills-employers-looking-for',
                'category': blog_categories['career-advice'],
                'excerpt': 'Discover the most in-demand skills that employers are seeking in 2024. Learn which skills can boost your career and make you more marketable.',
                'content': '''
                <h2>Introduction</h2>
                <p>In today's rapidly evolving job market, staying relevant means continuously updating your skill set. Here are the top 5 skills that employers are prioritizing in 2024.</p>
                
                <h3>1. Artificial Intelligence and Machine Learning</h3>
                <p>AI and ML skills are in high demand across industries. Even basic understanding of AI concepts can give you an edge in many roles.</p>
                
                <h3>2. Data Analysis</h3>
                <p>The ability to interpret and derive insights from data is crucial. Skills in SQL, Excel, and data visualization tools are highly valued.</p>
                
                <h3>3. Digital Marketing</h3>
                <p>With businesses increasingly moving online, digital marketing skills including SEO, SEM, and social media marketing are essential.</p>
                
                <h3>4. Emotional Intelligence</h3>
                <p>Soft skills like emotional intelligence, empathy, and communication are becoming more important as automation handles technical tasks.</p>
                
                <h3>5. Adaptability and Resilience</h3>
                <p>The ability to adapt to change and bounce back from setbacks is crucial in today's fast-paced business environment.</p>
                
                <h2>How to Develop These Skills</h2>
                <ul>
                    <li>Take online courses on platforms like Coursera and Udemy</li>
                    <li>Work on personal projects</li>
                    <li>Seek mentorship opportunities</li>
                    <li>Attend industry conferences</li>
                    <li>Join professional communities</li>
                </ul>
                
                <h2>Conclusion</h2>
                <p>Invest in developing these skills to stay competitive in the job market. Remember that learning is a lifelong journey.</p>
                ''',
                'author': admin_user,
                'tags_list': ['skills', 'career development', 'job market', 'professional growth', 'employability'],
                'status': 'published',
                'published_at': now - timedelta(days=5),
            },
        ]
        
        for post_data in blog_posts_data:
            tags = post_data.pop('tags_list', [])
            post, created = BlogPost.objects.get_or_create(
                slug=post_data['slug'],
                defaults=post_data
            )
            if created and tags:
                for tag in tags:
                    tag_obj, _ = Tag.objects.get_or_create(name=tag)
                    post.tags.add(tag_obj)
                self.stdout.write(self.style.SUCCESS(f'Blog post created: {post.title}'))
        
        self.stdout.write(self.style.SUCCESS('\n✅ All sample data created successfully!'))
        self.stdout.write(self.style.SUCCESS('\n📋 Summary:'))
        self.stdout.write(f'   - Admin User: admin@jobportalpro.com / Admin@123')
        self.stdout.write(f'   - Site Settings: 1')
        self.stdout.write(f'   - Job Categories: {JobCategory.objects.count()}')
        self.stdout.write(f'   - Jobs: {Job.objects.count()}')
        self.stdout.write(f'   - Blog Categories: {BlogCategory.objects.count()}')
        self.stdout.write(f'   - Blog Posts: {BlogPost.objects.count()}')