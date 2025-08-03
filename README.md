# 📋 Sistema de Formulários Django

Um sistema moderno e responsivo de formulários desenvolvido com Django, Tailwind CSS e JavaScript, com efeitos visuais impressionantes e uma interface de usuário intuitiva.

## ✨ Características

- **Design Moderno**: Interface com glassmorphism e gradientes
- **Responsivo**: Funciona perfeitamente em desktop, tablet e mobile
- **Animações**: Efeitos visuais suaves e interativos
- **Validação**: Máscaras de entrada para CPF e telefone
- **Filtros**: Busca e filtros avançados na lista
- **Admin**: Interface administrativa personalizada
- **Efeitos**: Partículas flutuantes, confete, ripple effects

## 🚀 Tecnologias Utilizadas

- **Backend**: Django 5.2
- **Frontend**: Tailwind CSS, JavaScript Vanilla
- **Banco de Dados**: SQLite (configurável)
- **Efeitos**: CSS Animations, JavaScript DOM Manipulation

## 📦 Instalação

### Pré-requisitos

- Python 3.8+
- pip (gerenciador de pacotes Python)

### Passos para Instalação

1. **Clone o repositório**
   ```bash
   git clone <url-do-repositorio>
   cd formulario
   ```

2. **Crie um ambiente virtual**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Instale as dependências**
   ```bash
   pip install django
   ```

4. **Execute as migrações**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Crie um superusuário (opcional)**
   ```bash
   python manage.py createsuperuser
   ```

6. **Execute o servidor**
   ```bash
   python manage.py runserver
   ```

## 🌐 URLs do Sistema

- **Lista de Formulários**: `http://localhost:8000/formulario2/`
- **Criar Formulário**: `http://localhost:8000/formulario2/create/`
- **Admin Django**: `http://localhost:8000/admin/`

## 📝 Estrutura do Projeto

```
formulario/
├── formulario/                 # Configurações do projeto
│   ├── settings.py            # Configurações Django
│   ├── urls.py                # URLs principais
│   └── wsgi.py                # Configuração WSGI
├── formulario2/               # App principal
│   ├── models.py              # Modelo de dados
│   ├── views.py               # Views do sistema
│   ├── urls.py                # URLs do app
│   ├── admin.py               # Configuração admin
│   ├── templates/             # Templates HTML
│   │   ├── formulario2.html   # Template do formulário
│   │   └── formulario2_list.html # Template da lista
│   └── static/                # Arquivos estáticos
│       └── formulario2/
│           ├── css/
│           │   └── custom.css  # Estilos personalizados
│           └── js/
│               └── effects.js  # Efeitos JavaScript
└── manage.py                  # Script de gerenciamento Django
```

## 🎨 Características Visuais

### Efeitos Implementados

1. **Glassmorphism**: Efeito de vidro translúcido
2. **Gradientes**: Fundos com gradientes coloridos
3. **Animações**: Transições suaves e efeitos de entrada
4. **Partículas**: Efeito de partículas flutuantes no fundo
5. **Ripple**: Efeito de ondulação nos botões
6. **Hover Effects**: Efeitos ao passar o mouse
7. **Loading States**: Estados de carregamento animados
8. **Confete**: Efeito de confete no sucesso

### Cores e Temas

- **Primária**: Gradiente azul-roxo (#667eea → #764ba2)
- **Secundária**: Gradiente rosa-vermelho (#f093fb → #f5576c)
- **Sucesso**: Gradiente azul-ciano (#4facfe → #00f2fe)
- **Aviso**: Gradiente rosa-amarelo (#fa709a → #fee140)

## 📊 Modelo de Dados

O sistema inclui os seguintes campos:

- **Informações Pessoais**: Nome completo, nome social, data de nascimento, gênero, estado civil
- **Documentos**: RG, CPF, órgão emissor, data de emissão
- **Contato**: Telefone, email
- **Informações Adicionais**: Nome da mãe

## 🔧 Funcionalidades

### Formulário de Cadastro
- ✅ Validação em tempo real
- ✅ Máscaras de entrada (CPF, telefone)
- ✅ Labels flutuantes
- ✅ Efeitos visuais interativos
- ✅ Estados de loading
- ✅ Mensagens de sucesso

### Lista de Formulários
- ✅ Visualização em cards
- ✅ Busca por texto
- ✅ Filtros por gênero e estado civil
- ✅ Paginação
- ✅ Ações (ver, editar, excluir)
- ✅ Modal de detalhes
- ✅ Estatísticas em tempo real

### Interface Administrativa
- ✅ Lista organizada por campos
- ✅ Filtros avançados
- ✅ Busca integrada
- ✅ Agrupamento por seções
- ✅ Campos somente leitura

## 🎯 Efeitos JavaScript

### Animações Personalizadas
- `createParticles()`: Partículas flutuantes
- `typeWriter()`: Efeito de digitação
- `createConfetti()`: Efeito de confete
- `addRippleEffect()`: Efeito ripple nos botões
- `showLoading()`: Spinner de carregamento
- `shake()`: Efeito de tremor para validação
- `fadeIn()`: Fade in suave
- `slideIn()`: Slide in com direção

### Interações
- Hover effects em cards e botões
- Focus effects em inputs
- Loading states durante submissão
- Validação visual em tempo real
- Animações de entrada sequenciais

## 📱 Responsividade

O sistema é totalmente responsivo com breakpoints:

- **Mobile**: < 768px
- **Tablet**: 768px - 1024px
- **Desktop**: > 1024px

## 🎨 Personalização

### Cores
Para alterar as cores do tema, edite o arquivo `static/formulario2/css/custom.css`:

```css
.gradient-primary {
    background: linear-gradient(135deg, #sua-cor-1 0%, #sua-cor-2 100%);
}
```

### Animações
Para modificar as animações, edite o arquivo `static/formulario2/js/effects.js`:

```javascript
const customAnimations = {
    // Suas animações personalizadas
};
```

## 🚀 Deploy

### Produção
Para deploy em produção:

1. Configure `DEBUG = False` em `settings.py`
2. Configure `ALLOWED_HOSTS` com seu domínio
3. Configure um banco de dados de produção (PostgreSQL recomendado)
4. Configure arquivos estáticos:
   ```bash
   python manage.py collectstatic
   ```

### Docker (Opcional)
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 👨‍💻 Autor

Desenvolvido com ❤️ usando Django e Tailwind CSS

## 🆘 Suporte

Se você encontrar algum problema ou tiver dúvidas:

1. Verifique a documentação
2. Abra uma issue no repositório
3. Entre em contato através do email

---

**✨ Divirta-se codificando! ✨** 