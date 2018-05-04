from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.db.models import Max
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.functional import cached_property
from django.views import View
from django.views.generic import CreateView
from django.views.generic import DeleteView
from django.views.generic import DetailView
from django.views.generic import FormView
from django.views.generic import ListView
from django.views.generic import UpdateView

from maasaic.apps.content.forms import CellCreateForm
from maasaic.apps.content.forms import CellOrderForm
from maasaic.apps.content.forms import CellPositionForm
from maasaic.apps.content.forms import CellUpdateContentForm
from maasaic.apps.content.forms import CellVisibilityForm
from maasaic.apps.content.forms import PageCreateForm
from maasaic.apps.content.forms import PagePublishForm
from maasaic.apps.content.forms import PageResetForm
from maasaic.apps.content.forms import PageUpdateForm
from maasaic.apps.content.forms import SectionCreateForm
from maasaic.apps.content.forms import SectionOrderForm
from maasaic.apps.content.forms import SectionVisibilityForm
from maasaic.apps.content.forms import UploadImageForm
from maasaic.apps.content.forms import WebsiteConfigForm
from maasaic.apps.content.forms import WebsiteCreateForm
from maasaic.apps.content.forms import WebsiteDefaultsForm
from maasaic.apps.content.forms import WebsitePublishForm
from maasaic.apps.content.models import Cell
from maasaic.apps.content.models import CellImage
from maasaic.apps.content.models import Font
from maasaic.apps.content.models import Page
from maasaic.apps.content.models import PageFont
from maasaic.apps.content.models import Section
from maasaic.apps.content.models import UploadedImage
from maasaic.apps.content.models import Website


# ------------------------------------------------------------------------------
# Websites
# ------------------------------------------------------------------------------
class WebsiteUrlMixin(object):
    @cached_property
    def website(self):
        return get_object_or_404(Website,
                                 subdomain=self.kwargs['subdomain'],
                                 user=self.request.user)

    def get_context_data(self, *args, **kwargs):
        ctx = super(WebsiteUrlMixin, self).get_context_data(*args, **kwargs)
        ctx['website'] = self.website
        return ctx


class PageUrlMixin(object):
    mode = None

    @cached_property
    def page(self):
        kwargs = {'pk': self.kwargs['pk']}
        if self.mode:
            kwargs['mode'] = self.mode
        return get_object_or_404(Page, **kwargs)

    def get_context_data(self, *args, **kwargs):
        ctx = super(PageUrlMixin, self).get_context_data(*args, **kwargs)
        ctx['page'] = self.page
        return ctx


class CurrentTabMixin(object):
    current_tab = None

    def get_context_data(self, *args, **kwargs):
        ctx = super(CurrentTabMixin, self).get_context_data(*args, **kwargs)
        ctx['current_tab'] = self.current_tab
        return ctx


# ------------------------------------------------------------------------------
# Websites
# ------------------------------------------------------------------------------
class WebsiteListView(LoginRequiredMixin, ListView):
    template_name = 'frontend/website_list.html'
    context_object_name = 'websites'

    def get_queryset(self):
        return Website.objects.filter(user=self.request.user)

    def get_context_data(self, *args, **kwargs):
        context = super(WebsiteListView, self).get_context_data(*args, **kwargs)
        context['website_create_form'] = WebsiteCreateForm()
        return context


class WebsiteCreateView(LoginRequiredMixin, FormView):
    template_name = 'frontend/website_create.html'
    form_class = WebsiteCreateForm

    def form_valid(self, form):
        website = form.save(commit=False)
        website.user = self.request.user
        if not website.name:
            website.name = website.subdomain.title()
        website.save()
        msg = 'That\'s it, %s is now created. ' \
              'Add some pages and make it go live.' % website.domain
        messages.success(self.request, msg)
        url = reverse('website_detail', args=[website.subdomain])
        return HttpResponseRedirect(url)


class WebsiteDetailBase(LoginRequiredMixin, CurrentTabMixin,
                        WebsiteUrlMixin, View):

    def get_object(self):
        return self.website


class WebsiteDetailView(WebsiteDetailBase, DetailView):
    model = Website
    template_name = 'frontend/website_dashboard.html'
    slug_field = 'subdomain'
    slug_url_kwarg = 'subdomain'
    current_tab = 'dashboard'


class WebsiteGalleryView(WebsiteDetailView):
    template_name = 'frontend/website_gallery.html'
    current_tab = 'gallery'


class WebsiteConfigView(WebsiteDetailBase, UpdateView):
    template_name = 'frontend/website_detail_config.html'
    form_class = WebsiteConfigForm
    model = Website
    slug_field = 'subdomain'
    slug_url_kwarg = 'subdomain'
    current_tab = 'config'

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'Website configuration updated')
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('website_config', args=[self.website.subdomain])


class WebsitePageDefaultsView(WebsiteDetailBase, FormView):
    template_name = 'frontend/website_detail_defaults.html'
    form_class = WebsiteDefaultsForm
    model = Website
    slug_field = 'subdomain'
    slug_url_kwarg = 'subdomain'
    current_tab = 'defaults'

    def get_form_kwargs(self):
        kw = super(WebsitePageDefaultsView, self).get_form_kwargs()
        kw['website'] = self.website
        return kw

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'Page default values updated')
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('website_defaults', args=[self.website.subdomain])


class WebsitePublishView(WebsiteDetailBase, UpdateView):
    form_class = WebsitePublishForm
    model = Website
    slug_field = 'subdomain'
    slug_url_kwarg = 'subdomain'

    def form_valid(self, form):
        form.save()
        is_visible = form.cleaned_data['is_visible']
        if is_visible:
            msg = 'Yeey! Now %s is live ;)' % self.website.domain
            level = messages.SUCCESS
        else:
            msg = '%s is now offline.' % self.website.domain
            level = messages.WARNING
        messages.add_message(self.request, level, msg)
        url = reverse('page_list', args=[self.website.subdomain])
        return HttpResponseRedirect(url)

    def form_invalid(self, form):
        return self.form_valid(form)


# ------------------------------------------------------------------------------
# Pages
# ------------------------------------------------------------------------------
class PageListView(WebsiteDetailBase, DetailView):
    template_name = 'frontend/page_list.html'
    model = Website
    slug_field = 'subdomain'
    slug_url_kwarg = 'subdomain'
    current_tab = 'pages'

    def get_context_data(self, **kwargs):
        context = super(PageListView, self).get_context_data(**kwargs)
        context['page_create_form'] = PageCreateForm(website=self.website)
        return context


class PageCreateView(WebsiteDetailBase, CreateView):
    template_name = 'frontend/page_create.html'
    model = Page
    form_class = PageCreateForm
    current_tab = 'pages'

    def get_form_kwargs(self):
        kw = super(PageCreateView, self).get_form_kwargs()
        kw['website'] = self.website
        return kw

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'Page created')
        url = reverse('page_list', args=[self.website.subdomain])
        return HttpResponseRedirect(url)


class PageConfigView(WebsiteDetailBase, PageUrlMixin, UpdateView):
    template_name = 'frontend/page_config.html'
    model = Page
    current_tab = 'pages'
    context_object_name = 'page'
    form_class = PageUpdateForm

    def get_form_kwargs(self):
        kw = super(PageConfigView, self).get_form_kwargs()
        kw['website'] = self.website
        return kw

    def form_valid(self, form):
        page = form.save()
        msg = 'The config for "%s" was updated' % page.title
        messages.success(self.request, msg)
        url = reverse('page_list', args=[self.website.subdomain])
        return HttpResponseRedirect(url)

    def get_object(self, queryset=None):
        return self.page


class PageUpdateView(WebsiteDetailBase, PageUrlMixin, DetailView):
    template_name = 'app/page.html'
    model = Page

    def get_context_data(self, **kwargs):
        context = super(PageUpdateView, self).get_context_data(**kwargs)
        context['page_edit_on'] = True
        context['fonts'] = Font.objects.all()
        context['section_create_form'] = SectionCreateForm(page=self.page)
        context['show_borders'] = 'borders' not in self.request.GET
        return context

    def get_object(self, queryset=None):
        return self.page


class PageDeleteView(DeleteView, PageUrlMixin, WebsiteDetailBase):
    model = Page

    def get_object(self, queryset=None):
        return self.page

    def get_success_url(self):
        return reverse('page_list', args=[self.website.subdomain])

    def delete(self, request, *args, **kwargs):
        response = super(PageDeleteView, self)\
            .delete(request, *args, **kwargs)
        messages.success(self.request, 'Your page has been deleted')
        return response


class PagePublishView(UpdateView, PageUrlMixin, WebsiteDetailView):
    form_class = PagePublishForm
    model = Page
    mode = Page.Mode.LIVE

    def get_object(self):
        return self.page

    def form_valid(self, form):
        if form.cleaned_data['is_visible']:
            with transaction.atomic():
                all_content = ''
                page = form.save()
                Section.objects.filter(page=page).delete()
                visible_sections = list(page.edit_page.visible_sections)
                for edit_section in visible_sections:
                    section_attr = edit_section.get_attr_dict()
                    section_attr['page'] = page
                    section_attr['is_visible'] = True
                    live_section = Section.objects.create(**section_attr)
                    visible_cells = list(edit_section.visible_cells)
                    for edit_cell in visible_cells:
                        cell_attr = edit_cell.get_attr_dict()
                        cell_attr['is_visible'] = True
                        cell_attr['section'] = live_section
                        live_cell = Cell.objects.create(**cell_attr)
                        all_content += live_cell.content
                        try:
                            edit_cell_im = CellImage.objects.get(cell=edit_cell)
                            CellImage.objects.create(
                                cell=live_cell,
                                image=edit_cell_im.image,
                                cropping=edit_cell_im.cropping,
                                uploaded_image=edit_cell_im.uploaded_image)
                        except CellImage.DoesNotExist:
                            pass

                PageFont.objects.filter(page=page).delete()
                fonts = Font.objects.all()
                page_fonts = []
                for font in fonts:
                    if font.name in all_content:
                        page_fonts.append(PageFont(page=page, font=font))
                if page_fonts:
                    PageFont.objects.bulk_create(page_fonts)

            msg = 'The page "%s" is now live' % page.title
            messages.success(self.request, msg)
        else:
            page = form.save()
            msg = 'The page "%s" is now offline' % page.title
            messages.warning(self.request, msg)

        url = self.request.GET.get(
            'next',
            reverse('page_list', args=[self.website.subdomain]))
        return HttpResponseRedirect(url)


class PageResetView(FormView, PageUrlMixin, WebsiteDetailBase):
    form_class = PageResetForm
    model = Page
    mode = Page.Mode.EDIT

    def get_object(self):
        return self.page

    def form_valid(self, form):
        with transaction.atomic():
            Section.objects.filter(page=self.page).delete()
            live_sections = list(self.page.target_page.section_set.all())
            for live_section in live_sections:
                section_attr = live_section.get_attr_dict()
                section_attr['page'] = self.page
                section_attr['is_visible'] = live_section.is_visible
                edit_section = Section.objects.create(**section_attr)
                live_cells = list(live_section.cell_set.all())
                for live_cell in live_cells:
                    cell_attr = live_cell.get_attr_dict()
                    cell_attr['is_visible'] = live_cell.is_visible
                    cell_attr['section'] = edit_section
                    Cell.objects.create(**cell_attr)

        url = reverse('page_update',
                      args=[self.page.website.subdomain, self.page.pk])
        return HttpResponseRedirect(url)


# ------------------------------------------------------------------------------
# Sections
# ------------------------------------------------------------------------------
class SectionCreateView(CreateView, LoginRequiredMixin):
    form_class = SectionCreateForm
    template_name = 'frontend/section_create.html'

    def get_form_kwargs(self):
        kw = super(SectionCreateView, self).get_form_kwargs()
        kw['page'] = Page.objects.get(id=self.request.POST['page'])
        return kw

    def form_valid(self, form):
        section = form.save(commit=False)
        max_order = Section.objects.filter(page=section.page)\
            .aggregate(Max('order'))['order__max']
        if max_order:
            section.order = max_order + 1
        else:
            section.order = 0
        section.save()
        url = reverse('page_update', args=[section.page.website.subdomain,
                                           section.page.pk])
        return HttpResponseRedirect(url)


class SectionDeleteView(DeleteView, LoginRequiredMixin):
    model = Section

    def get_success_url(self):
        section = self.get_object()
        return reverse('page_update', args=[section.page.website.subdomain,
                                            section.page.pk])


class SectionUpdateView(UpdateView, LoginRequiredMixin):
    form_class = SectionCreateForm
    model = Section
    template_name = 'frontend/section_create.html'

    def get_form_kwargs(self):
        kw = super(SectionUpdateView, self).get_form_kwargs()
        kw['page'] = Page.objects.get(id=self.request.POST['page'])
        return kw

    def form_valid(self, form):
        section = form.save()
        url = reverse('page_update', args=[section.page.website.subdomain,
                                           section.page.pk])
        return HttpResponseRedirect(url)


class SectionOrderUpdateView(UpdateView, LoginRequiredMixin):
    form_class = SectionOrderForm
    http_method_names = ['post']
    model = Section

    def get_success_url(self):
        section = self.get_object()
        return reverse('page_update', args=[section.page.website.subdomain,
                                            section.page.pk])

    def form_invalid(self, form):
        return HttpResponseRedirect(self.get_success_url())


class SectionVisibilityUpdateView(UpdateView, LoginRequiredMixin):
    form_class = SectionVisibilityForm
    http_method_names = ['post']

    def get_object(self, queryset=None):
        section = get_object_or_404(Section, pk=self.kwargs['pk'])
        return section

    def form_valid(self, form):
        section = form.save(commit=True)
        url = reverse('page_update', args=[section.page.website.subdomain,
                                           section.page.pk])
        return HttpResponseRedirect(url)

    def form_invalid(self, form):
        messages.error(self.request, form.errors)
        return HttpResponseRedirect(redirect_to=self.get_success_url())


# ------------------------------------------------------------------------------
# Cells
# ------------------------------------------------------------------------------
class CellCreateView(CreateView, LoginRequiredMixin):
    model = Cell
    form_class = CellCreateForm

    def form_valid(self, form):
        cell = form.save(commit=True)
        url = reverse('page_update', args=[cell.section.page.website.subdomain,
                                           cell.section.page.pk])
        return HttpResponseRedirect(url)


class BaseCellUpdateView(UpdateView, LoginRequiredMixin):
    http_method_names = ['post']
    model = Cell

    def get_success_url(self):
        cell = self.get_object()
        return reverse('page_update', args=[cell.section.page.website.subdomain,
                                            cell.section.page.pk])

    def form_invalid(self, form):
        return HttpResponseRedirect(self.get_success_url())


class CellContentUpdateView(BaseCellUpdateView):
    form_class = CellUpdateContentForm


class CellPositionUpdateView(BaseCellUpdateView):
    form_class = CellPositionForm


class CellVisibilityUpdateView(BaseCellUpdateView):
    form_class = CellVisibilityForm


class CellOrderUpdateView(BaseCellUpdateView):
    form_class = CellOrderForm


class CellDeleteView(DeleteView, LoginRequiredMixin):
    model = Cell

    def get_success_url(self):
        cell = self.get_object()
        return reverse('page_update', args=[cell.section.page.website.subdomain,
                                            cell.section.page.pk])


# ------------------------------------------------------------------------------
# Images
# ------------------------------------------------------------------------------
class ImageCreateView(LoginRequiredMixin, WebsiteUrlMixin, CreateView):
    model = UploadedImage
    form_class = UploadImageForm
    template_name = 'frontend/image_create.html'

    def get_context_data(self, **kwargs):
        context = super(ImageCreateView, self).get_context_data(**kwargs)
        context['GIPHY_KEY'] = settings.GIPHY_KEY
        context['images'] = UploadedImage.objects\
            .filter(website=self.website)\
            .order_by('-created_at')
        return context

    def form_valid(self, form):
        uploaded_image = form.save(commit=False)
        uploaded_image.website = self.website
        uploaded_image.size = uploaded_image.image.size
        uploaded_image.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('image_create', args=[self.website.subdomain])
