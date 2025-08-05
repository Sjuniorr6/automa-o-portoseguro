from django.shortcuts import render
from .models import Formulario2, FormularioAmil, AutomationLog
from .forms import Formulario2Form, FormularioAmilForm
from django.views.generic import CreateView, ListView
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.contrib import messages
import json
from .automation_amil import start_amil_automation

# Create your views here.
def home_view(request):
    """Página inicial com os dois botões de formulário"""
    return render(request, 'formulario2/home.html')

class Formulario2CreateView(CreateView):
    model = Formulario2
    form_class = Formulario2Form
    template_name = 'formulario2/formulario2.html'
    success_url = reverse_lazy('formulario2_list')
    
    def form_valid(self, form):
        """Override form_valid to add success message"""
        response = super().form_valid(form)
        messages.success(self.request, 'Formulário Porto enviado com sucesso!')
        return response
    
    def form_invalid(self, form):
        """Override form_invalid to add error messages"""
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f'Erro no campo {field}: {error}')
        return super().form_invalid(form)

class FormularioAmilCreateView(CreateView):
    model = FormularioAmil
    form_class = FormularioAmilForm
    template_name = 'formulario2/formulario_amil.html'
    success_url = reverse_lazy('formulario_amil_list')
    
    def form_valid(self, form):
        """Override form_valid to add success message and start automation"""
        response = super().form_valid(form)
        messages.success(self.request, 'Formulário Amil enviado com sucesso!')
        
        # Iniciar automação do Selenium em uma thread separada
        try:
            print("Iniciando automação da Amil...")
            start_amil_automation()
            messages.info(self.request, 'Automação da Amil iniciada! O navegador será aberto em alguns segundos.')
        except Exception as e:
            print(f"Erro ao iniciar automação: {e}")
            messages.warning(self.request, 'Formulário salvo, mas houve um erro ao iniciar a automação.')
        
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

class FormularioAmilListView(ListView):
    model = FormularioAmil
    template_name = 'formulario2/formulario_amil_list.html'
    context_object_name = 'formulario_amil_list'

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
class FormularioAmilAPIView(View):
    """
    API endpoint para gerenciar dados do FormularioAmil
    GET: Retorna todos os registros
    POST: Cria um novo registro
    """
    
    def get(self, request):
        """Retorna todos os registros em formato JSON"""
        try:
            formularios = FormularioAmil.objects.all()
            data = []
            
            for formulario in formularios:
                data.append({
                    'id': formulario.id,
                    'nome': formulario.nome,
                    'cpf': formulario.cpf,
                    'nome_cartao': formulario.nome_cartao,
                    'data_inclusao': formulario.data_inclusao.strftime('%Y-%m-%d') if formulario.data_inclusao else None,
                    'data_registro': formulario.data_registro.strftime('%Y-%m-%d') if formulario.data_registro else None,
                    'data_nascimento': formulario.data_nascimento.strftime('%Y-%m-%d') if formulario.data_nascimento else None,
                    'sexo': formulario.sexo,
                    'nacionalidade': formulario.nacionalidade,
                    'nome_mae': formulario.nome_mae,
                    'nome_pai': formulario.nome_pai or '',
                    'estado_civil': formulario.estado_civil,
                    'plano': formulario.plano,
                    'contrato_dental': formulario.contrato_dental or '',
                    'plano_dental': formulario.plano_dental or '',
                    'created_at': formulario.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'updated_at': formulario.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
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
            formulario = FormularioAmil.objects.create(
                nome=data.get('nome'),
                cpf=data.get('cpf'),
                nome_cartao=data.get('nome_cartao'),
                data_inclusao=data.get('data_inclusao'),
                data_registro=data.get('data_registro'),
                data_nascimento=data.get('data_nascimento'),
                sexo=data.get('sexo'),
                nacionalidade=data.get('nacionalidade', 'B'),
                nome_mae=data.get('nome_mae'),
                nome_pai=data.get('nome_pai', ''),
                estado_civil=data.get('estado_civil'),
                plano=data.get('plano'),
                contrato_dental=data.get('contrato_dental', ''),
                plano_dental=data.get('plano_dental', '')
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Registro Amil criado com sucesso',
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

@method_decorator(csrf_exempt, name='dispatch')
class FormularioAmilDetailAPIView(View):
    """
    API endpoint para gerenciar um registro específico do FormularioAmil
    GET: Retorna um registro específico
    PUT: Atualiza um registro
    DELETE: Remove um registro
    """
    
    def get(self, request, pk):
        """Retorna um registro específico"""
        try:
            formulario = FormularioAmil.objects.get(pk=pk)
            data = {
                'id': formulario.id,
                'nome': formulario.nome,
                'cpf': formulario.cpf,
                'nome_cartao': formulario.nome_cartao,
                'data_inclusao': formulario.data_inclusao.strftime('%Y-%m-%d') if formulario.data_inclusao else None,
                'data_registro': formulario.data_registro.strftime('%Y-%m-%d') if formulario.data_registro else None,
                'data_nascimento': formulario.data_nascimento.strftime('%Y-%m-%d') if formulario.data_nascimento else None,
                'sexo': formulario.sexo,
                'nacionalidade': formulario.nacionalidade,
                'nome_mae': formulario.nome_mae,
                'nome_pai': formulario.nome_pai or '',
                'estado_civil': formulario.estado_civil,
                'plano': formulario.plano,
                'contrato_dental': formulario.contrato_dental or '',
                'plano_dental': formulario.plano_dental or '',
                'created_at': formulario.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'updated_at': formulario.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
            }
            
            return JsonResponse({
                'success': True,
                'data': data
            })
            
        except FormularioAmil.DoesNotExist:
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
            formulario = FormularioAmil.objects.get(pk=pk)
            data = json.loads(request.body)
            
            # Atualizar campos
            for field, value in data.items():
                if hasattr(formulario, field):
                    setattr(formulario, field, value)
            
            formulario.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Registro Amil atualizado com sucesso'
            })
            
        except FormularioAmil.DoesNotExist:
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
            formulario = FormularioAmil.objects.get(pk=pk)
            formulario.delete()
            
            return JsonResponse({
                'success': True,
                'message': 'Registro Amil removido com sucesso'
            })
            
        except FormularioAmil.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Registro não encontrado'
            }, status=404)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
        
        
        
        
        
        
        
        
        
        