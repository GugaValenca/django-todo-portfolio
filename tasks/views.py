from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.utils import timezone
from django.db.models import Q
from .models import Task
from .forms import TaskForm, CustomUserCreationForm


class RegisterView(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'registration/register.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        messages.success(self.request, 'Conta criada com sucesso! Faça login.')
        return super().form_valid(form)


@login_required
def task_list(request):
    tasks = Task.objects.filter(user=request.user)

    # Filtros
    status_filter = request.GET.get('status')
    priority_filter = request.GET.get('priority')
    search = request.GET.get('search')

    if status_filter:
        tasks = tasks.filter(status=status_filter)

    if priority_filter:
        tasks = tasks.filter(priority=priority_filter)

    if search:
        tasks = tasks.filter(
            Q(title__icontains=search) | Q(description__icontains=search)
        )

    # Estatísticas
    stats = {
        'total': Task.objects.filter(user=request.user).count(),
        'pendentes': Task.objects.filter(user=request.user, status='pendente').count(),
        'em_andamento': Task.objects.filter(user=request.user, status='em_andamento').count(),
        'concluidas': Task.objects.filter(user=request.user, status='concluida').count(),
        'vencidas': Task.objects.filter(
            user=request.user,
            due_date__lt=timezone.now(),
            status__in=['pendente', 'em_andamento']
        ).count(),
    }

    context = {
        'tasks': tasks,
        'stats': stats,
        'status_choices': Task.STATUS_CHOICES,
        'priority_choices': Task.PRIORITY_CHOICES,
        'current_status': status_filter,
        'current_priority': priority_filter,
        'search_query': search,
    }

    return render(request, 'tasks/task_list.html', context)


@login_required
def task_create(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            task.save()
            messages.success(request, 'Tarefa criada com sucesso!')
            return redirect('task-list')
    else:
        form = TaskForm()

    return render(request, 'tasks/task_form.html', {
        'form': form,
        'title': 'Nova Tarefa'
    })


@login_required
def task_update(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)

    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            updated_task = form.save()

            # Marca como concluída se o status mudou
            if updated_task.status == 'concluida' and not updated_task.completed_at:
                updated_task.completed_at = timezone.now()
                updated_task.save()
            elif updated_task.status != 'concluida':
                updated_task.completed_at = None
                updated_task.save()

            messages.success(request, 'Tarefa atualizada com sucesso!')
            return redirect('task-list')
    else:
        form = TaskForm(instance=task)

    return render(request, 'tasks/task_form.html', {
        'form': form,
        'task': task,
        'title': 'Editar Tarefa'
    })


@login_required
def task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)

    if request.method == 'POST':
        task.delete()
        messages.success(request, 'Tarefa excluída com sucesso!')
        return redirect('task-list')

    return render(request, 'tasks/task_confirm_delete.html', {'task': task})


@login_required
def toggle_task_status(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)

    if task.status == 'concluida':
        task.status = 'pendente'
        task.completed_at = None
    else:
        task.status = 'concluida'
        task.completed_at = timezone.now()

    task.save()
    return redirect('task-list')
# Create your views here.
