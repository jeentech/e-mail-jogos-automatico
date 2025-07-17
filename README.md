📧 E-mail Jogos Automático
Envio automático por e-mail dos principais jogos dos clubes brasileiros e da seleção brasileira do dia, utilizando Python e APIs.

🚀 Objetivo
Este projeto tem como finalidade automatizar o envio diário por e-mail dos jogos programados para os principais clubes de futebol brasileiros e para a seleção brasileira. Através de uma API, o script coleta as informações atualizadas e envia um resumo para os destinatários cadastrados.

🛠️ Tecnologias Utilizadas
Python: Linguagem de programação principal.

APIs de Futebol: Para obter os dados dos jogos.

Biblioteca smtplib: Para envio de e-mails.

📥 Como Usar
Clonar o Repositório

bash
Copiar
Editar
git clone https://github.com/jeentech/e-mail-jogos-automatico.git
cd e-mail-jogos-automatico
Instalar Dependências

Certifique-se de ter o Python instalado. Em seguida, instale as bibliotecas necessárias:

bash
Copiar
Editar
pip install -r requirements.txt
Configurar o Envio de E-mails

Edite o arquivo jogos_diarios.py com suas credenciais de e-mail (remetente e destinatários).

Configure o servidor SMTP de acordo com o provedor de e-mail utilizado.

Executar o Script

bash
Copiar
Editar
python jogos_diarios.py
O script buscará os jogos do dia e enviará um e-mail com as informações.

📄 Estrutura do Projeto
bash
Copiar
Editar
e-mail-jogos-automatico/
│
├── jogos_diarios.py        # Script principal para envio dos jogos
├── teste.py                # Script para testes unitários
└── requirements.txt        # Dependências do projeto
📧 Exemplo de E-mail Enviado
O e-mail enviado contém:

Data e hora dos jogos.

Equipes participantes.

Local da partida.

⚠️ Avisos
Certifique-se de que o servidor SMTP esteja configurado corretamente.

Verifique as políticas de envio de e-mails do seu provedor para evitar bloqueios.

🤝 Contribuições
Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou pull requests.

📄 Licença
Este projeto está licenciado sob a MIT License.

