from django.db import models
from django.contrib.auth.models import User


class Task(models.Model):
    PRIORITY_CHOICES = [
        ('baixa', 'Baixa'),
        ('media', 'Média'),
        ('alta', 'Alta'),
    ]

    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('em_andamento', 'Em Andamento'),
        ('concluida', 'Concluída'),
    ]

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField('Título', max_length=200)
    description = models.TextField('Descrição', blank=True)
    priority = models.CharField(
        'Prioridade', max_length=10, choices=PRIORITY_CHOICES, default='media')
    status = models.CharField('Status', max_length=15,
                              choices=STATUS_CHOICES, default='pendente')
    due_date = models.DateTimeField(
        'Data de Vencimento', null=True, blank=True)
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)
    completed_at = models.DateTimeField('Concluído em', null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Tarefa'
        verbose_name_plural = 'Tarefas'

    def __str__(self):
        return self.title

    @property
    def is_overdue(self):
        if self.due_date and self.status != 'concluida':
            from django.utils import timezone
            return timezone.now() > self.due_date
        return False
