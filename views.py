# coding:utf-8
from __future__ import print_function

from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse
from django.http import Http404
from django.http import HttpResponseRedirect
from django.core.files import File
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView
from os.path import abspath, dirname, join, basename, exists
from uuid import uuid4

import os
import json
from urllib.parse import urljoin
import subprocess
import apksign

from .forms import UploadModelFileForm
from .models import UpFile


@csrf_exempt  # for post out of html
def upload(request):
    if request.method == 'POST':
        form = UploadModelFileForm(request.POST, request.FILES)
        if form.is_valid():

            o = form.save(commit=False)

            # path检查
            # realative to MEDIA_ROOT
            path_rela = join(apksign.PACKAGE_DIR, o.path)
            path_full = join(settings.MEDIA_ROOT, apksign.PACKAGE_DIR, o.path)
            if exists(path_full):
                return HttpResponse(json.dumps({'err': 'existed'}), content_type="application/json")
            if not exists(dirname(path_full)):
                os.makedirs(dirname(path_full))

            # 证书检查
            store = form['certification'].value()
            if store not in apksign.CERTS:
                print('wrong certification %s' % store, file=sys.stderr)
                return HttpResponse(json.dumps({'err': 'wrong certification %s' % store}), content_type="application/json")

            # 保存
            o.from_ip = get_client_ip(request)
            o.status = 'uploaded'
            o.save()

            # 签名
            unsignedjar = o.file.path
            signed_alignedjar = path_full
            signed_unalignedjar = signed_alignedjar + ".tmp"

            os.chdir(apksign.EXE_DIR)
            cmd_sign = 'jarsigner -keystore %s %s -signedjar %s %s %s' % \
                (join(apksign.PROFILES_DIR, store),
                 ''.join(' -' + key + ' ' + str(value)
                         for key, value in apksign.CERTS[store].items()),
                 signed_unalignedjar,
                 unsignedjar,
                 store)
            cmd_align = r'./zipalign -v 4 %s %s' % (
                signed_unalignedjar, signed_alignedjar)
            p = subprocess.Popen(cmd_sign, stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE, env=os.environ, shell=True)
            out, err = p.communicate()
            if len(err) > 0:
                print(cmd_sign, file=sys.stderr)
                print(err, file=sys.stderr)
                o.status = 'signfail'
                o.save()
                return HttpResponse(json.dumps({'err': o.status}), content_type="application/json")
            p = subprocess.Popen(
                cmd_align, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            out, err = p.communicate()
            os.remove(signed_unalignedjar)
            if len(err) > 0:
                o.status = 'alignfail'
                o.save()
                return HttpResponse(json.dumps({'err': o.status}), content_type="application/json")

            o.signed.name = path_rela
            o.status = 'success'
            o.save()

            # 保存列表
            form.save_m2m()

            current_uri = '%s://%s' % ('https' if request.is_secure() else 'http',
                                       request.get_host())
            result = {"url": urljoin(
                current_uri, join(settings.MEDIA_URL, o.signed.url))}
        else:
            result = {"err": dict(form.errors)}
        return HttpResponse(json.dumps(result), content_type="application/json")
    else:
        form = UploadModelFileForm()

    return render(request, 'apksign/upload.html', {'form': form})


class AllView(ListView):
    template_name = "apksign/upfile_list.html"
    paginate_by = 20

    def get_queryset(self):
        return UpFile.objects.order_by("-up_date")

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(ListView, self).get_context_data(**kwargs)
        # Add in the publisher
        context['request'] = self.request
        return context


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
