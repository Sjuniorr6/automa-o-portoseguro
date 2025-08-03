from django.shortcuts import render
from .models import Formulario2, AutomationLog
from .forms import Formulario2Form
from django.views.generic import CreateView, ListView
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.contrib import messages
import json

# Create your views here.
class Formulario2CreateView(CreateView):
    model = Formulario2
    form_class = Formulario2Form
    template_name = 'formulario2/formulario2.html'
    success_url = reverse_lazy('formulario2_list')
    
    def form_valid(self, form):
        """Override form_valid to add success message"""
        response = super().form_valid(form)
        messages.success(self.request, 'Formulário enviado com sucesso!')
        return response
    
    def form_invalid(self, form):
        """Override form_invalid to add error messages"""
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f'Erro no campo {field}: {error}')
        return super().form_invalid(form)

class Formulario2ListView(ListView):
    model = Formulario2
    template_name = 'formulario2/formulario2_list.html'
    context_object_name = 'formulario2_list'

class AutomationLogListView(ListView):
    model = AutomationLog
    template_name = 'formulario2/automation_logs.html'
    context_object_name = 'automation_logs'
    paginate_by = 20

def api_viewer(request):
    """View para renderizar o visualizador de dados da API"""
    return render(request, 'formulario2/api_viewer.html')

@method_decorator(csrf_exempt, name='dispatch')
class Formulario2APIView(View):
    """
    API endpoint para gerenciar dados do Formulario2
    GET: Retorna todos os registros
    POST: Cria um novo registro
    """
    
    def get(self, request):
        """Retorna todos os registros em formato JSON"""
        try:
            formularios = Formulario2.objects.all()
            data = []
            
            for formulario in formularios:
                data.append({
                    'id': formulario.id,
                    'nomeCompleto': formulario.nomeCompleto,
                    'nomeSocial': formulario.nomeSocial or '',
                    'dataNascimento': formulario.dataNascimento.strftime('%Y-%m-%d') if formulario.dataNascimento else None,
                    'genero': formulario.genero,
                    'estadoCivil': formulario.estadoCivil,
                    'rg': formulario.rg,
                    'cpf': formulario.cpf,
                    'orgaoEmissor': formulario.orgaoEmissor,
                    'dataEmissao': formulario.dataEmissao.strftime('%Y-%m-%d') if formulario.dataEmissao else None,
                    'telefone': formulario.telefone,
                    'email': formulario.email,
                    'nomeMae': formulario.nomeMae,
                })
            
            return JsonResponse({
                'success': True,
                'count': len(data),
                'data': data
            }, safe=False)
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    def post(self, request):
        """Cria um novo registro via API"""
        try:
            data = json.loads(request.body)
            
            # Criar novo formulário
            formulario = Formulario2.objects.create(
                nomeCompleto=data.get('nomeCompleto'),
                nomeSocial=data.get('nomeSocial', ''),
                dataNascimento=data.get('dataNascimento'),
                genero=data.get('genero'),
                estadoCivil=data.get('estadoCivil'),
                rg=data.get('rg'),
                cpf=data.get('cpf'),
                orgaoEmissor=data.get('orgaoEmissor'),
                dataEmissao=data.get('dataEmissao'),
                telefone=data.get('telefone'),
                email=data.get('email'),
                nomeMae=data.get('nomeMae')
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Registro criado com sucesso',
                'id': formulario.id
            }, status=201)
            
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'JSON inválido'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class Formulario2DetailAPIView(View):
    """
    API endpoint para gerenciar um registro específico
    GET: Retorna um registro específico
    PUT: Atualiza um registro
    DELETE: Remove um registro
    """
    
    def get(self, request, pk):
        """Retorna um registro específico"""
        try:
            formulario = Formulario2.objects.get(pk=pk)
            data = {
                'id': formulario.id,
                'nomeCompleto': formulario.nomeCompleto,
                'nomeSocial': formulario.nomeSocial or '',
                'dataNascimento': formulario.dataNascimento.strftime('%Y-%m-%d') if formulario.dataNascimento else None,
                'genero': formulario.genero,
                'estadoCivil': formulario.estadoCivil,
                'rg': formulario.rg,
                'cpf': formulario.cpf,
                'orgaoEmissor': formulario.orgaoEmissor,
                'dataEmissao': formulario.dataEmissao.strftime('%Y-%m-%d') if formulario.dataEmissao else None,
                'telefone': formulario.telefone,
                'email': formulario.email,
                'nomeMae': formulario.nomeMae,
            }
            
            return JsonResponse({
                'success': True,
                'data': data
            })
            
        except Formulario2.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Registro não encontrado'
            }, status=404)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    def put(self, request, pk):
        """Atualiza um registro"""
        try:
            formulario = Formulario2.objects.get(pk=pk)
            data = json.loads(request.body)
            
            # Atualizar campos
            for field, value in data.items():
                if hasattr(formulario, field):
                    setattr(formulario, field, value)
            
            formulario.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Registro atualizado com sucesso'
            })
            
        except Formulario2.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Registro não encontrado'
            }, status=404)
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'JSON inválido'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    def delete(self, request, pk):
        """Remove um registro"""
        try:
            formulario = Formulario2.objects.get(pk=pk)
            formulario.delete()
            
            return JsonResponse({
                'success': True,
                'message': 'Registro removido com sucesso'
            })
            
        except Formulario2.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Registro não encontrado'
            }, status=404)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
        
        
        
        
        
        
        
        
        
        