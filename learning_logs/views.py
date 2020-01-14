from django.shortcuts import render
from django.urls import reverse

from .models import Topic, Entry
from django.http import HttpResponseRedirect, Http404
from .froms import TopicForm, EntryForm
from django.contrib.auth.decorators import login_required
# Create your views here.


def index(request):
    """学习笔记的主页"""
    return render(request=request, template_name='learning_logs/index.html')


@login_required
def topics(request):
    """显示所有主题"""
    topics1 = Topic.objects.filter(owner=request.user).order_by('date_added')
    context = {'topics': topics1}
    return render(request=request, template_name='learning_logs/topics.html', context=context)


@login_required
def topic(request, topic_id):
    """显示但个主题及其所有的条目"""
    topic1 = Topic.objects.get(id=topic_id)
    # 确认请求的主题属于当前用户
    if topic1.owner != request.user:
        raise Http404
    entries = topic1.entry_set.order_by('-date_added')
    context = {'topic': topic1, 'entries': entries}
    return render(request=request, template_name='learning_logs/topic.html', context=context)


@login_required
def new_topic(request):
    """添加主新题"""
    if request.method != 'POST':
        # 未提交数据：创建一个新的表单
        form = TopicForm()
    else:
        # POST提交的数据，对数据进行处理
        form = TopicForm(data=request.POST)
        if form.is_valid():
            new_topic1 = form.save(commit=False)
            new_topic1.owner = request.user
            new_topic1.save()
            return HttpResponseRedirect(reverse('learning_logs:topics'))
    context = {'form': form}
    return render(request=request, template_name='learning_logs/new_topic.html', context=context)


@login_required
def new_entry(request, topic_id):
    """添加新条目"""
    topic1 = Topic.objects.get(id=topic_id)
    if request.method != 'POST':
        form = EntryForm()
    else:
        form = EntryForm(data=request.POST)
        if form.is_valid():
            new_entry1 = form.save(commit=False)
            new_entry1.topic = topic1
            new_entry1.save()
            return HttpResponseRedirect(reverse('learning_logs:topic', args=[topic_id]))
    context = {'topic': topic1, 'form': form}
    return render(request=request, template_name='learning_logs/new_entry.html', context=context)


@login_required
def edit_entry(request, entry_id):
    """编辑既有的条目"""
    entry = Entry.objects.get(id=entry_id)
    topic1 = entry.topic
    if topic1.owner != request.user:
        raise Http404
    if request.method != 'POST':
        form = EntryForm(instance=entry)
    else:
        form = EntryForm(instance=entry, data=request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('learning_logs:topic', args=[topic1.id]))
    context = {'entry': entry, 'topic': topic1, 'form': form}
    return render(request=request, template_name='learning_logs/edit_entry.html', context=context)
