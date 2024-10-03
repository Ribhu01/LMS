from django.db import models
from django.contrib.auth.models import AbstractUser
from django.urls import reverse
from django.conf import settings
import misaka
# Create your models here.
class User(AbstractUser):
    is_student = models.BooleanField(default=False)
    is_teacher = models.BooleanField(default=False)

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name='student_profile')
    name = models.CharField(max_length=250)
    roll_no = models.CharField(max_length=50)
    email = models.EmailField(max_length=254)
    phone = models.CharField(max_length=15, help_text="Enter a valid phone number.")
    student_profile_pic = models.ImageField(upload_to="classroom/student_profile_pic", blank=True)

    def get_absolute_url(self):
        return reverse('classroom:student_detail', kwargs={'pk': self.pk})

    def __str__(self):
        return f"{self.name} (Roll No: {self.roll_no})"

    class Meta:
        ordering = ['roll_no']
        verbose_name_plural = "Students"

class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name='teacher_profile')
    name = models.CharField(max_length=250)
    subject_name = models.CharField(max_length=250)
    email = models.EmailField(max_length=254)
    phone = models.CharField(maxlength=15, help_text="Enter a valid phone number.")
    teacher_profile_pic = models.ImageField(upload_to="classroom/teacher_profile_pic", blank=True)
    class_students = models.ManyToManyField(Student, through="StudentsInClass", related_name='teachers')

    def get_absolute_url(self):
        return reverse('classroom:teacher_detail', kwargs={'pk': self.pk})

    def __str__(self):
        return f"{self.name} (Subject: {self.subject_name})"

class StudentMarks(models.Model):
    teacher = models.ForeignKey(Teacher, related_name='given_marks', on_delete=models.CASCADE)
    student = models.ForeignKey(Student, related_name="marks", on_delete=models.CASCADE)
    subject_name = models.CharField(max_length=250)
    marks_obtained = models.PositiveIntegerField()
    maximum_marks = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.subject_name} - {self.marks_obtained}/{self.maximum_marks}"

class StudentsInClass(models.Model):
    teacher = models.ForeignKey(Teacher, related_name="class_students", on_delete=models.CASCADE)
    student = models.ForeignKey(Student, related_name="classes", on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.student.name} in {self.teacher.name}'s class"

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['teacher', 'student'], name='unique_teacher_student')
        ]

class MessageToTeacher(models.Model):
    student = models.ForeignKey(Student, related_name='messages_to_teacher', on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, related_name='received_messages', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now=True)
    message = models.TextField()
    message_html = models.TextField(editable=False)

    def __str__(self):
        return f"Message from {self.student.name} to {self.teacher.name}"

    def save(self, *args, **kwargs):
        self.message_html = misaka.html(self.message)
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(fields=['student', 'message'], name='unique_student_message')
        ]

class ClassNotice(models.Model):
    teacher = models.ForeignKey(Teacher, related_name='notices', on_delete=models.CASCADE)
    students = models.ManyToManyField(Student, related_name='notices_received')
    created_at = models.DateTimeField(auto_now=True)
    message = models.TextField()
    message_html = models.TextField(editable=False)

    def __str__(self):
        return f"Notice from {self.teacher.name}: {self.message[:20]}..."

    def save(self, *args, **kwargs):
        self.message_html = misaka.html(self.message)
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(fields=['teacher', 'message'], name='unique_teacher_notice')
        ]

class ClassAssignment(models.Model):
    students = models.ManyToManyField(Student, related_name='assignments')
    teacher = models.ForeignKey(Teacher, related_name='assignments_given', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now=True)
    assignment_name = models.CharField(max_length=250)
    assignment_file = models.FileField(upload_to='assignments')

    def __str__(self):
        return f"Assignment: {self.assignment_name}"

    class Meta:
        ordering = ['-created_at']

class SubmitAssignment(models.Model):
    student = models.ForeignKey(Student, related_name='submitted_assignments', on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, related_name='submitted_by_students', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now=True)
    submitted_assignment = models.ForeignKey(ClassAssignment, related_name='submissions', on_delete=models.CASCADE)
    submit_file = models.FileField(upload_to='submissions')

    def __str__(self):
        return f"{self.student.name} submitted {self.submitted_assignment.assignment_name}"

    class Meta:
        ordering = ['-created_at']
