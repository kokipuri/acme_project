from django.views.generic import ( 
    CreateView, DeleteView, DetailView, ListView, UpdateView
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy, reverse
from django.shortcuts import get_object_or_404
from django.views.generic import CreateView

from .forms import BirthdayForm, CongratulationForm
from .models import Birthday, Congratulation
from .utils import calculate_birthday_countdown


class BirthdayCreateView(LoginRequiredMixin, CreateView):
    model = Birthday
    form_class = BirthdayForm

    def form_valid(self, form):
        # Присвоить полю author объект пользователя из запроса.
        form.instance.author = self.request.user
        # Продолжить валидацию, описанную в форме.
        return super().form_valid(form)


class BirthdayUpdateView(LoginRequiredMixin, UpdateView):
    model = Birthday
    form_class = BirthdayForm

    def dispatch(self, request, *args, **kwargs):
        # Получаем объект по первичному ключу и автору или вызываем 404 ошибку.
        get_object_or_404(Birthday, pk=kwargs['pk'], author=request.user)
        # Если объект был найден, то вызываем родительский метод, 
        # чтобы работа CBV продолжилась.
        return super().dispatch(request, *args, **kwargs)


class BirthdayDeleteView(LoginRequiredMixin, DeleteView):
    model = Birthday
    success_url = reverse_lazy('birthday:list')

    def dispatch(self, request, *args, **kwargs):
        # Получаем объект по первичному ключу и автору или вызываем 404 ошибку.
        get_object_or_404(Birthday, pk=kwargs['pk'], author=request.user)
        # Если объект был найден, то вызываем родительский метод, 
        # чтобы работа CBV продолжилась.
        return super().dispatch(request, *args, **kwargs)


class BirthdayDetailView(DetailView):
    model = Birthday
    

    def get_context_data(self, **kwargs):
        # Получаем словарь контекста:
        context = super().get_context_data(**kwargs)
        # Добавляем в словарь новый ключ:
        context['birthday_countdown'] = calculate_birthday_countdown(
            # Дату рождения берём из объекта в словаре context:
            self.object.birthday
        )
        # Записываем в переменную form пустой объект формы.
        context['form'] = CongratulationForm()
        # Запрашиваем все поздравления для выбранного дня рождения.
        context['congratulations'] = (
            # Дополнительно подгружаем авторов комментариев,
            # чтобы избежать множества запросов к БД.
            self.object.congratulations.select_related('author')
        )
        # Возвращаем словарь контекста.
        return context

# Наследуем класс от встроенного ListView:
class BirthdayListView(ListView):
    # Указываем модель, с которой работает CBV...
    model = Birthday
    # По умолчанию этот класс 
    # выполняет запрос queryset = Birthday.objects.all(),
    # но мы его переопределим:
    queryset = Birthday.objects.prefetch_related(
        'tags'
    ).select_related('author')
    # ...сортировку, которая будет применена при выводе списка объектов:
    ordering = 'id'
    # ...и даже настройки пагинации:
    paginate_by = 10


class CongratulationCreateView(LoginRequiredMixin, CreateView):
    birthday = None
    model = Congratulation
    form_class = CongratulationForm

    # Переопределяем dispatch()
    def dispatch(self, request, *args, **kwargs):
        self.birthday = get_object_or_404(Birthday, pk=kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)

    # Переопределяем form_valid()
    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.birthday = self.birthday
        return super().form_valid(form)

    # Переопределяем get_success_url()
    def get_success_url(self):
        return reverse('birthday:detail', kwargs={'pk': self.birthday.pk})

#@login_required
#def add_comment(request, pk):
    # Получаем объект дня рождения или выбрасываем 404 ошибку.
    #birthday = get_object_or_404(Birthday, pk=pk)
    # Функция должна обрабатывать только POST-запросы.
    #form = CongratulationForm(request.POST)
    #if form.is_valid():
        # Создаём объект поздравления, но не сохраняем его в БД.
        #congratulation = form.save(commit=False)
        # В поле author передаём объект автора поздравления.
        #congratulation.author = request.user
        # В поле birthday передаём объект дня рождения.
        #congratulation.birthday = birthday
        # Сохраняем объект в БД.
        #congratulation.save()
    # Перенаправляем пользователя назад, на страницу дня рождения.
    #return redirect('birthday:detail', pk=pk)



#def birthday(request, pk=None):
    #if pk is not None:
        #instance = get_object_or_404(Birthday, pk=pk)
    #else:
        #instance = None
    #form = BirthdayForm(
        #request.POST or None,
        # Файлы, переданные в запросе, указываются отдельно.
        #files=request.FILES or None,
        #instance=instance
    #)
    #context = {'form': form}
    #if form.is_valid():
        #form.save()
        # ...вызовем функцию подсчёта дней:
        #birthday_countdown = calculate_birthday_countdown(
            # ...и передаём в неё дату из словаря cleaned_data.
            #form.cleaned_data['birthday']
        #)
        # Обновляем словарь контекста: добавляем в него новый элемент.
        #context.update({'birthday_countdown': birthday_countdown})
    #return render(request, 'birthday/birthday.html', context)


#def delete_birthday(request, pk):
    # Получаем объект модели или выбрасываем 404 ошибку.
    #instance = get_object_or_404(Birthday, pk=pk)
    # В форму передаём только объект модели;
    # передавать в форму параметры запроса не нужно.
    #form = BirthdayForm(instance=instance)
    #context = {'form': form}
    # Если был получен POST-запрос...
    #if request.method == 'POST':
        # ...удаляем объект:
        #instance.delete()
        # ...и переадресовываем пользователя на страницу со списком записей.
        #return redirect('birthday:list')
    # Если был получен GET-запрос — отображаем форму.
    #return render(request, 'birthday/birthday.html', context)


#def birthday_list(request):
    # Получаем все объекты модели Birthday из БД.
    #birthdays = Birthday.objects.order_by('id')
    # Создаём объект пагинатора с количеством 10 записей на страницу.
    #paginator = Paginator(birthdays, 10)
    
    # Получаем из запроса значение параметра page.
    #page_number = request.GET.get('page')
    # Получаем запрошенную страницу пагинатора. 
    # Если параметра page нет в запросе или его значение не приводится к числу,
    # вернётся первая страница.
    #page_obj = paginator.get_page(page_number)
    # Вместо полного списка объектов передаём в контекст 
    # объект страницы пагинатора
    #context = {'page_obj': page_obj}
    #return render(request, 'birthday/birthday_list.html', context)