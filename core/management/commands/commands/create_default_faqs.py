from django.core.management.base import BaseCommand
from core.models import FAQ, WhyChooseUs

class Command(BaseCommand):
    help = 'Create default FAQs and Why Choose Us features'

    def handle(self, *args, **options):
        # Create default FAQs
        if FAQ.objects.count() == 0:
            faqs = [
                {
                    'question': 'How do I create an account?',
                    'answer': 'Click the "Sign Up" button in the navigation menu and fill in your details. You can also sign up using your Google account for faster registration. Once registered, you can complete your profile and start applying for jobs immediately.',
                    'order': 1
                },
                {
                    'question': 'How do I apply for a job?',
                    'answer': 'Browse our job listings, click on any job that interests you to view details, and click the "Apply Now" button. You\'ll need to upload your resume and write a cover letter. Make sure your profile is complete for a better chance of being noticed.',
                    'order': 2
                },
                {
                    'question': 'How can I track my application status?',
                    'answer': 'Log into your dashboard and navigate to "My Applications". Here you\'ll see all your job applications with their current status (Pending, Reviewed, Shortlisted, Interviewed, Offered, Hired, or Rejected). You\'ll also receive email notifications for status updates.',
                    'order': 3
                },
                {
                    'question': 'Is my personal information secure?',
                    'answer': 'Yes, absolutely. We use industry-standard SSL encryption to protect your data. Your personal information is never shared with third parties without your explicit consent. You can review our Privacy Policy for more details on how we handle your data.',
                    'order': 4
                },
                {
                    'question': 'How can I improve my chances of getting hired?',
                    'answer': 'Complete your profile 100% by adding your skills, experience, and a professional photo. Tailor your resume and cover letter for each application. Research the company before applying and prepare well for interviews. Stay active on the platform and apply regularly.',
                    'order': 5
                },
                {
                    'question': 'Can I edit or withdraw my application?',
                    'answer': 'Once submitted, applications cannot be edited. However, you can withdraw your application from your dashboard if its status is still "Pending", "Reviewed", or "Shortlisted". After withdrawal, you can reapply with updated information if the job is still accepting applications.',
                    'order': 6
                },
            ]
            
            for faq_data in faqs:
                FAQ.objects.create(**faq_data)
            
            self.stdout.write(self.style.SUCCESS(f'Created {len(faqs)} default FAQs'))
        else:
            self.stdout.write(self.style.WARNING('FAQs already exist'))
        
        # Create default Why Choose Us features
        if WhyChooseUs.objects.count() == 0:
            features = [
                {
                    'icon': 'fas fa-users',
                    'title': 'Access Top Talent',
                    'description': 'Instantly connect with highly skilled and verified professionals across multiple industries, reducing the time and effort needed to find the right candidate for your organization.',
                    'order': 1
                },
                {
                    'icon': 'fas fa-rocket',
                    'title': 'Efficient Hiring Process',
                    'description': 'Our streamlined recruitment system helps employers post jobs, filter candidates, and hire faster with improved accuracy and reduced cost. Save time and resources with our smart matching technology.',
                    'order': 2
                },
                {
                    'icon': 'fas fa-chart-line',
                    'title': 'Career Growth Opportunities',
                    'description': 'We empower job seekers with access to quality job opportunities, helping them grow professionally and build long-term careers. Find positions that match your skills and career aspirations.',
                    'order': 3
                },
                {
                    'icon': 'fas fa-shield-alt',
                    'title': 'Trusted & Secure Platform',
                    'description': 'Your data security is our priority. We use enterprise-grade encryption and follow industry best practices to ensure your personal information and job applications are always protected.',
                    'order': 4
                },
                {
                    'icon': 'fas fa-headset',
                    'title': '24/7 Support',
                    'description': 'Our dedicated support team is available around the clock to help you with any questions or issues. Whether you\'re an employer or job seeker, we\'re here to ensure your experience is smooth and successful.',
                    'order': 5
                },
                {
                    'icon': 'fas fa-globe',
                    'title': 'Global Reach',
                    'description': 'Access job opportunities from companies worldwide. Our platform connects talent with employers across borders, opening up international career possibilities and diverse hiring options.',
                    'order': 6
                },
            ]
            
            for feature_data in features:
                WhyChooseUs.objects.create(**feature_data)
            
            self.stdout.write(self.style.SUCCESS(f'Created {len(features)} default Why Choose Us features'))
        else:
            self.stdout.write(self.style.WARNING('Why Choose Us features already exist'))